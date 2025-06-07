from typing import Any, Generator
from urllib.parse import urljoin, urlparse, parse_qs
import datetime
import time 
import os
import logging

import requests
from dagster import ConfigurableResource, get_dagster_logger

logger = logging.getLogger(__name__)

# Import mock implementation
try:
    from github_pipeline.mock_github import MockGitHubAPI
except ImportError:
    try:
        from .mock_github import MockGitHubAPI
    except ImportError as e:
        logger.warning(f"Could not import MockGitHubAPI: {e}")
        MockGitHubAPI = None

class GitHubAPIResource(ConfigurableResource):
    """Custom Dagster resource for the GitHub REST API.

    Args:
        - github_token (str | None, optional):
            GitHub token for authentication. If no token is set, the API calls will be without authentication.
        - host (str, optional):
            Host address of the GitHub REST API. Defaults to 'https://api.github.com'.
        - retry_attempts (int): Number of times to retry failed requests. Defaults to 3.
        - retry_delay_seconds (int): Initial delay in seconds before retrying. Defaults to 5.
    """

    github_token: str | None = None
    """GitHub token for authentication. If no token is set, the API calls will be without authentication."""

    host: str = 'https://api.github.com'
    """Host of the GitHub REST API."""

    retry_attempts: int = 3
    """Number of times to retry failed requests."""

    retry_delay_seconds: int = 5
    """Initial delay in seconds before retrying (exponential backoff)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger = get_dagster_logger()
        
        # Debug logging for environment variable
        mock_env = os.getenv('GITHUB_USE_MOCK', '')
        logger.info(f"GITHUB_USE_MOCK environment variable value: '{mock_env}'")
        
        self._mock_api = None
        if mock_env.lower() == 'true':
            logger.info("Mock mode is enabled")
            if MockGitHubAPI is not None:
                self._mock_api = MockGitHubAPI()
                logger.info("Successfully initialized mock GitHub API")
            else:
                logger.warning("Mock GitHub API requested but mock_github module not available")
        else:
            logger.info("Using real GitHub API (mock mode is disabled)")

    def execute_request(
        self,
        method: str,
        path: str,
        params: dict | list[tuple] | None = None,
        json: Any | None = None,
        full_url: str | None = None, # Added for pagination
    ) -> requests.Response:
        """Execute a request to the GitHub REST API with retries and rate limit handling.

        Args:
            - method (str):
                HTTP method for the API call, e.g. 'GET'.
            - path (str):
                Path of the endpoint.
            - params (dict | list[tuple], optional):
                Dictionary or list of tuples to send as query parameters in the request.
            - json (Any, optional):
                A JSON serializable Python object to send in the body of the request.
            - full_url (str, optional):
                If provided, will use this URL directly instead of constructing from host and path.
                Useful for pagination `Link` headers.

        Returns:
            - requests.Response:
                Response object of the API call.

        Raises:
            - requests.HTTPError:
                When HTTP 4xx or 5xx response is received after all retries.
        """
        logger = get_dagster_logger()
        if params is None:
            params = {}

        # Default GitHub API version
        default_params = {'apiVersion': '2022-11-28'}
        # Passed parameters win over default
        params = {**default_params, **params}

        headers = {
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28', # Explicitly set API version header
        }
        if self.github_token:
            headers['Authorization'] = f'Bearer {self.github_token}'

        url = full_url if full_url else urljoin(self.host, path)
        retries = 0
        while retries <= self.retry_attempts:
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    params=params,
                    headers=headers,
                    json=json,
                    timeout=30, # Added timeout to prevent hanging requests
                )
                logger.info(f'Call {method}: {response.url}')

                # Check for rate limit
                if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers and int(response.headers['X-RateLimit-Remaining']) == 0:
                    reset_time = int(response.headers['X-RateLimit-Reset'])
                    sleep_duration = max(0, reset_time - datetime.datetime.now(datetime.timezone.utc).timestamp()) + 5 # Add a buffer
                    logger.warning(f"GitHub API rate limit exceeded. Retrying in {sleep_duration:.2f} seconds.")
                    time.sleep(sleep_duration)
                    retries += 1
                    continue # Skip raise_for_status and retry

                response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                return response

            except requests.exceptions.HTTPError as err:
                if 400 <= response.status_code < 500: # Client error, usually not retryable
                    logger.error(f"Client error ({response.status_code}) fetching data: {err!r} - {response.text}")
                    raise # Re-raise immediately for client errors
                else: # Server error or other retriable HTTP errors
                    logger.warning(
                        f"Attempt {retries + 1}/{self.retry_attempts + 1}: "
                        f"HTTP error ({response.status_code}) for {url}: {err!r}. "
                        f"Retrying in {self.retry_delay_seconds * (2 ** retries):.2f} seconds."
                    )
            except requests.exceptions.ConnectionError as err:
                logger.warning(
                    f"Attempt {retries + 1}/{self.retry_attempts + 1}: "
                    f"Connection error for {url}: {err!r}. "
                    f"Retrying in {self.retry_delay_seconds * (2 ** retries):.2f} seconds."
                )
            except requests.exceptions.Timeout as err:
                logger.warning(
                    f"Attempt {retries + 1}/{self.retry_attempts + 1}: "
                    f"Timeout error for {url}: {err!r}. "
                    f"Retrying in {self.retry_delay_seconds * (2 ** retries):.2f} seconds."
                )
            except Exception as err:
                logger.error(f"An unexpected error occurred during request to {url}: {err!r}")
                raise

            # Exponential backoff
            time.sleep(self.retry_delay_seconds * (2 ** retries))
            retries += 1

        logger.error(f"Failed to execute request to {url} after {self.retry_attempts} retries.")
        raise requests.exceptions.RequestException(f"Max retries exceeded for {url}")


    def _paginate_request(self, path: str, params: dict | None = None) -> Generator[dict[str, Any], None, None]:
        """Helper to handle pagination for GitHub API requests."""
        logger = get_dagster_logger()
        current_params = params.copy() if params else {}
        current_params['per_page'] = 100 # Ensure we get max per page for efficiency
        next_url = None

        while True:
            response = self.execute_request(
                method='GET',
                path=path,
                params=current_params,
                full_url=next_url # Use full_url if paginating
            )
            data = response.json()
            yield from data # Yield each item from the current page

            # Check for Link header for pagination
            if 'Link' in response.headers:
                links = response.headers['Link'].split(', ')
                next_link = None
                for link in links:
                    if 'rel="next"' in link:
                        next_link = link.split(';')[0].strip('<>')
                        break
                
                if next_link:
                    # Reset params for the next page as the full_url contains them
                    current_params = {} 
                    next_url = next_link
                else:
                    break # No more pages
            else:
                break # No Link header, single page result


    def get_repository(self, owner: str, repo: str) -> dict[str, Any]:
        """Get metadata about a GitHub repository.
        Docs: https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository

        Args:
            - owner (str):
                The account owner of the repository. The name is not case sensitive.
            - repo (str):
                The name of the repository without the `.git` extension. The name is not case sensitive.

        Returns:
            - dict[str, Any]:
                The metadata for the repository.
        """
        if self._mock_api is not None:
            return self._mock_api.get_repository(owner, repo)
            
        path = f'/repos/{owner}/{repo}'
        response = self.execute_request(method='GET', path=path)
        payload = response.json()

        return payload

    def get_releases(self, owner: str, repo: str) -> list[dict[str, Any]]:
        """Get list of releases for a repository.
        Docs: https://docs.github.com/en/rest/releases/releases?apiVersion=2022-11-28#list-releases

        Args:
            - owner (str):
                The account owner of the repository. The name is not case sensitive.
            - repo (str):
                The name of the repository without the `.git` extension. The name is not case sensitive.

        Returns:
            - list[dict[str, Any]]:
                List of releases for the repository.
        """
        if self._mock_api is not None:
            return self._mock_api.get_releases(owner, repo)
            
        path = f'/repos/{owner}/{repo}/releases'
        return list(self._paginate_request(path=path))

    def get_issues(self, owner: str, repo: str, state: str = 'all') -> list[dict[str, Any]]:
        """Get list of issues (excluding pull requests) in a repository.
        Docs: https://docs.github.com/en/rest/issues/issues?apiVersion=2022-11-28#list-repository-issues

        Note: The GitHub API returns both issues and pull requests when querying the issues endpoint.
        This method filters out pull requests to return only true issues.

        Args:
            - owner (str):
                The account owner of the repository. The name is not case sensitive.
            - repo (str):
                The name of the repository without the `.git` extension. The name is not case sensitive.
            - state (str, optional):
                Indicates the state of the issues to return. Can be either 'open', 'closed', or 'all'.
                Defaults to 'all'.

        Returns:
            - list[dict[str, Any]]:
                List of issues (excluding pull requests) in the repository.
        """
        if self._mock_api is not None:
            return self._mock_api.get_issues(owner, repo, state)
            
        path = f'/repos/{owner}/{repo}/issues'
        params = {'state': state}
        
        # Filter out pull requests by checking if 'pull_request' key exists in the response
        # Pull requests will have this key, regular issues won't
        return [
            issue for issue in self._paginate_request(path=path, params=params)
            if 'pull_request' not in issue
        ]

    def get_pull_requests(self, owner: str, repo: str, state: str = 'all') -> list[dict[str, Any]]:
        """Get list of pull requests in a repository.
        Docs: https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#list-pull-requests

        Note: While pull requests are technically issues in GitHub's data model,
        this method uses the dedicated pulls endpoint to get pull request specific data.

        Args:
            - owner (str):
                The account owner of the repository. The name is not case sensitive.
            - repo (str):
                The name of the repository without the `.git` extension. The name is not case sensitive.
            - state (str, optional):
                Indicates the state of the pull requests to return. Can be either 'open', 'closed', or 'all'.
                Defaults to 'all'.

        Returns:
            - list[dict[str, Any]]:
                List of pull requests in the repository.
        """
        if self._mock_api is not None:
            return self._mock_api.get_pull_requests(owner, repo, state)
            
        path = f'/repos/{owner}/{repo}/pulls'
        
        # The /pulls endpoint doesn't support 'all' state, we need to make separate calls
        if state == 'all':
            open_prs = list(self._paginate_request(path=path, params={'state': 'open'}))
            closed_prs = list(self._paginate_request(path=path, params={'state': 'closed'}))
            return open_prs + closed_prs
        else:
            return list(self._paginate_request(path=path, params={'state': state}))

