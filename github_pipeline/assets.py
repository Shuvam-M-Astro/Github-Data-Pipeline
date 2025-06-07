from typing import Any
from datetime import datetime, timezone

from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    FreshnessPolicy,
    MetadataValue,
    asset,
    get_dagster_logger, 
)

from .resources import GitHubAPIResource
from .utils import create_markdown_report, extract_metadata, validate_repo_data 


def fetch_repo_data(github_api: GitHubAPIResource, owner: str, repo: str) -> dict[str, Any]:
    """Fetch all required data for a repository.

    Args:
        - github_api (GitHubAPIResource):
            GitHub API resource instance.
        - owner (str):
            The account owner of the repository.
        - repo (str):
            The name of the repository.

    Returns:
        - dict[str, Any]:
            Dictionary containing all repository data.

    Raises:
        - requests.HTTPError: When HTTP 4xx or 5xx response is received (propagated from GitHubAPIResource).
        - ValueError: When data validation fails (from validate_repo_data).
    """
    logger = get_dagster_logger() # Using Dagster's Logger
    try:
        # Fetch data using the GitHubAPIResource (which now handles retries and pagination internally)
        repo_metadata = github_api.get_repository(owner=owner, repo=repo)
        releases = github_api.get_releases(owner=owner, repo=repo)
        issues = github_api.get_issues(owner=owner, repo=repo)
        prs = github_api.get_pull_requests(owner=owner, repo=repo)

        repo_data = {
            'metadata': repo_metadata,
            'releases': releases,
            'issues': issues,
            'prs': prs,
        }

        # Validate the collected data structure and content
        validate_repo_data(repo_data)

        # Log metrics about the collected data
        logger.info(f"Collected data for {owner}/{repo}:")
        logger.info(f"- {len(releases)} releases")
        logger.info(f"- {len(issues)} issues")
        logger.info(f"- {len(prs)} pull requests")

        return repo_data
    except Exception as e:
        # Catch any exception during fetching or validation and log it
        logger.error(f"Error fetching data for {owner}/{repo}: {str(e)}")
        raise # Re-raise the exception to propagate the asset failure


@asset(
    name='delta-rs_repo_metadata',
    key_prefix=['stage', 'github', 'repositories', 'delta-io', 'delta-rs'],
    io_manager_key='json_io_manager',
    group_name='github',
    freshness_policy=FreshnessPolicy(maximum_lag_minutes=60 * 24),  # 24 hours
)
def delta_rs_metadata(context: AssetExecutionContext, github_api: GitHubAPIResource) -> dict[str, Any]:
    """Metadata from the GitHub repository of the Delta Lake Python client."""
    repo_data = fetch_repo_data(github_api=github_api, owner='delta-io', repo='delta-rs')

    context.add_output_metadata(
        metadata={
            'repo link': MetadataValue.url(repo_data['metadata'].get('html_url')),
            'data preview': MetadataValue.json(repo_data['metadata']),
        }
    )

    return repo_data


@asset(
    name='iceberg-python_repo_metadata',
    key_prefix=['stage', 'github', 'repositories', 'apache', 'iceberg-python'],
    io_manager_key='json_io_manager',
    group_name='github',
    freshness_policy=FreshnessPolicy(maximum_lag_minutes=60 * 24),  # 24 hours
)
def iceberg_python_metadata(context: AssetExecutionContext, github_api: GitHubAPIResource) -> dict[str, Any]:
    """Metadata from the GitHub repository of the Iceberg Python client."""
    repo_data = fetch_repo_data(github_api=github_api, owner='apache', repo='iceberg-python')

    context.add_output_metadata(
        metadata={
            'repo link': MetadataValue.url(repo_data['metadata'].get('html_url')),
            'data preview': MetadataValue.json(repo_data['metadata']),
        }
    )

    return repo_data


@asset(
    name='hudi-rs_repo_metadata',
    key_prefix=['stage', 'github', 'repositories', 'apache', 'hudi-rs'],
    io_manager_key='json_io_manager',
    group_name='github',
    freshness_policy=FreshnessPolicy(maximum_lag_minutes=60 * 24),  # 24 hours
)
def hudi_rs_metadata(context: AssetExecutionContext, github_api: GitHubAPIResource) -> dict[str, Any]:
    """Metadata from the GitHub repository of the Hudi Rust client.""" # Corrected docstring
    repo_data = fetch_repo_data(github_api=github_api, owner='apache', repo='hudi-rs')

    context.add_output_metadata(
        metadata={
            'repo link': MetadataValue.url(repo_data['metadata'].get('html_url')),
            'data preview': MetadataValue.json(repo_data['metadata']),
        }
    )

    return repo_data


@asset(
    key_prefix=['dm', 'reports'],
    ins={
        'delta_rs': AssetIn(AssetKey('delta-rs_repo_metadata')),
        'iceberg_python': AssetIn(AssetKey('iceberg-python_repo_metadata')),
        'hudi_rs': AssetIn(AssetKey('hudi-rs_repo_metadata')),
    },
    io_manager_key='md_io_manager',
    group_name='github',
)
def repo_report(
    context: AssetExecutionContext, delta_rs: dict[str, Any], iceberg_python: dict[str, Any], hudi_rs: dict[str, Any]
) -> str:
    """Report for comparing GitHub repositories."""

    report_data = {
        'delta-rs': extract_metadata(repo_metadata=delta_rs), # Corrected typo from repo_matadata
        'iceberg-python': extract_metadata(repo_metadata=iceberg_python), # Corrected typo from repo_matadata
        'hudi-rs': extract_metadata(repo_metadata=hudi_rs), # Corrected typo from repo_matadata
    }

    return create_markdown_report(context=context, report_data=report_data)
