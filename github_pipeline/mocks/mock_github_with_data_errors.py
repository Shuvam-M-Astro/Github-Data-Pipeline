"""Mock implementation for GitHub API responses.

This module provides mock data and functionality that can be used
with the GitHubAPIResource class for testing and development.
"""

from typing import Any, Dict, List
import logging

# Configure logging
logger = logging.getLogger(__name__)

class MockGitHubData:
    """Default mock data for GitHub API responses."""
    
    DELTA_RS_REPO = {
        "id": 123456789,
        "name": "delta-rs",
        "full_name": "delta-io/delta-rs",
        "private": False,
        "description": "Native Rust implementation of Delta Lake",
        "stargazers_count": 2705,
        "forks_count": 468,
        "subscribers_count": 37,
        "created_at": "2020-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "html_url": "https://github.com/delta-io/delta-rs"
    }
    
    DELTA_RS_RELEASES = [
        {
            "id": 1,
            "tag_name": "v0.15.0",
            "name": "Delta Rust v0.15.0",
            "body": "New features and improvements",
            "created_at": "2023-01-01T00:00:00Z",
            "published_at": "2023-01-01T00:00:00Z"
        }
    ] * 89  # 89 releases
    
    DELTA_RS_ISSUES = [
        {
            "id": 1,
            "number": 100,
            "title": "Performance improvement needed",
            "state": "open",
            "body": "We need to optimize the read performance",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
    ] * 139  # 139 open issues
    
    DELTA_RS_CLOSED_ISSUES = [
        {
            "id": 2,
            "number": 101,
            "title": "Bug fix needed",
            "state": "closed",
            "body": "Fixed performance issue",
            "created_at": "2023-01-01T00:00:00Z",
            "closed_at": "2023-05-15T00:00:00Z",
            "updated_at": "2023-05-15T00:00:00Z"
        }
    ] * 1130  # 1130 closed issues
    
    # Data for iceberg-python repository with validation errors
    ICEBERG_PYTHON_REPO = {
        "id": "invalid-id",  # Should be integer
        "name": "",  # Empty name
        "full_name": "apache/iceberg-python",
        "private": "yes",  # Should be boolean
        "description": None,  # Missing description
        "stargazers_count": -695,  # Negative count
        "forks_count": 268.5,  # Float instead of integer
        "subscribers_count": "thirty-one",  # String instead of integer
        "created_at": "2022-13-13T25:61:61Z",  # Invalid date format
        "updated_at": "2023",  # Incomplete date
        "html_url": None  # Missing URL
    }
    
    ICEBERG_PYTHON_RELEASES = [
        {
            "id": 0,  # Invalid ID (zero)
            "tag_name": "",  # Empty tag
            "name": None,  # Missing name
            "body": {"changes": ["not", "a", "string"]},  # Should be string
            "created_at": "invalid-date",  # Invalid date
            "published_at": "2023-02-31T00:00:00Z"  # Invalid date (Feb 31)
        }
    ] * 10  # 10 releases
    
    ICEBERG_PYTHON_ISSUES = [
        {
            "id": 2147483648,  # Integer overflow
            "number": -500,  # Negative number
            "title": "A" * 1000,  # Too long title
            "state": "OPEN",  # Wrong case
            "body": b"Binary data",  # Binary instead of string
            "created_at": "2023/01/01",  # Wrong date format
            "updated_at": ""  # Empty date
        }
    ] * 151  # 151 open issues
    
    ICEBERG_PYTHON_CLOSED_ISSUES = [
        {
            "id": float('inf'),  # Invalid number
            "number": None,  # Missing number
            "title": "\u0000\u0001\u0002",  # Invalid characters
            "state": "done",  # Invalid state
            "body": ["Not", "a", "string"],  # Wrong type
            "created_at": "2023-01-01 00:00:00",  # Wrong format (missing T and Z)
            "closed_at": "ongoing",  # Invalid date
            "updated_at": "2023-01-01T00:00:00Z\0"  # Null byte in date
        }
    ] * 431  # 431 closed issues
    
    HUDI_RS_REPO = {
        "id": 456789123,
        "name": "hudi-rs",
        "full_name": "apache/hudi-rs",
        "private": False,
        "description": "Rust implementation of Apache Hudi",
        "stargazers_count": 209,
        "forks_count": 42,
        "subscribers_count": 17,
        "created_at": "2022-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "html_url": "https://github.com/apache/hudi-rs"
    }
    
    HUDI_RS_RELEASES = [
        {
            "id": 5,
            "tag_name": "v0.1.0",
            "name": "Hudi Rust v0.1.0",
            "body": "Initial release",
            "created_at": "2023-01-01T00:00:00Z",
            "published_at": "2023-01-01T00:00:00Z"
        }
    ] * 3  # 3 releases
    
    HUDI_RS_ISSUES = [
        {
            "id": 6,
            "number": 300,
            "title": "Enhancement proposal",
            "state": "open",
            "body": "Propose new enhancement",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
    ] * 28  # 28 open issues
    
    HUDI_RS_CLOSED_ISSUES = [
        {
            "id": 7,
            "number": 301,
            "title": "Bug fix",
            "state": "closed",
            "body": "Fixed critical bug",
            "created_at": "2023-01-01T00:00:00Z",
            "closed_at": "2023-02-15T00:00:00Z",
            "updated_at": "2023-02-15T00:00:00Z"
        }
    ] * 62  # 62 closed issues
    
    # Pull request data for each repository
    DELTA_RS_PRS = {
        "open": [
            {
                "id": 8,
                "number": 400,
                "title": "Feature implementation",
                "state": "open",
                "body": "Implementing new feature",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
        ] * 17,  # 17 open PRs
        "closed": [
            {
                "id": 9,
                "number": 401,
                "title": "Bug fix PR",
                "state": "closed",
                "body": "Fixed bug",
                "created_at": "2023-01-01T00:00:00Z",
                "closed_at": "2023-01-10T00:00:00Z",
                "updated_at": "2023-01-10T00:00:00Z"
            }
        ] * 1973  # 1973 closed PRs
    }
    
    ICEBERG_PYTHON_PRS = {
        "open": [
            {
                "id": 10,
                "number": 500,
                "title": "New feature PR",
                "state": "open",
                "body": "Adding new feature",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
        ] * 76,  # 76 open PRs
        "closed": [
            {
                "id": 11,
                "number": 501,
                "title": "Documentation PR",
                "state": "closed",
                "body": "Updated docs",
                "created_at": "2023-01-01T00:00:00Z",
                "closed_at": "2023-01-09T00:00:00Z",
                "updated_at": "2023-01-09T00:00:00Z"
            }
        ] * 1292  # 1292 closed PRs
    }
    
    HUDI_RS_PRS = {
        "open": [
            {
                "id": 12,
                "number": 600,
                "title": "Enhancement PR",
                "state": "open",
                "body": "Adding enhancement",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
        ] * 13,  # 13 open PRs
        "closed": [
            {
                "id": 13,
                "number": 601,
                "title": "Fix PR",
                "state": "closed",
                "body": "Fixed issue",
                "created_at": "2023-01-01T00:00:00Z",
                "closed_at": "2023-01-09T00:00:00Z",
                "updated_at": "2023-01-09T00:00:00Z"
            }
        ] * 222  # 222 closed PRs
    }

class MockGitHubAPI:
    """Mock implementation of GitHub API calls.
    
    This class provides the same interface as the real API calls but returns mock data.
    It can be used for testing and development without making actual API calls.
    """
    
    def __init__(self):
        """Initialize mock data storage with real repository data."""
        self._data = {
            "repositories": {
                "delta-io/delta-rs": MockGitHubData.DELTA_RS_REPO,
                "apache/iceberg-python": MockGitHubData.ICEBERG_PYTHON_REPO,
                "apache/hudi-rs": MockGitHubData.HUDI_RS_REPO
            },
            "releases": {
                "delta-io/delta-rs": MockGitHubData.DELTA_RS_RELEASES,
                "apache/iceberg-python": MockGitHubData.ICEBERG_PYTHON_RELEASES,
                "apache/hudi-rs": MockGitHubData.HUDI_RS_RELEASES
            },
            "issues": {
                "delta-io/delta-rs": MockGitHubData.DELTA_RS_ISSUES + MockGitHubData.DELTA_RS_CLOSED_ISSUES,
                "apache/iceberg-python": MockGitHubData.ICEBERG_PYTHON_ISSUES + MockGitHubData.ICEBERG_PYTHON_CLOSED_ISSUES,
                "apache/hudi-rs": MockGitHubData.HUDI_RS_ISSUES + MockGitHubData.HUDI_RS_CLOSED_ISSUES
            },
            "pull_requests": {
                "delta-io/delta-rs": MockGitHubData.DELTA_RS_PRS,
                "apache/iceberg-python": MockGitHubData.ICEBERG_PYTHON_PRS,
                "apache/hudi-rs": MockGitHubData.HUDI_RS_PRS
            }
        }
    
    def set_mock_data(self, owner: str, repo: str, data_type: str, data: Any) -> None:
        """Set custom mock data for a specific repository and data type.
        
        Args:
            owner (str): Repository owner
            repo (str): Repository name
            data_type (str): Type of data ('repositories', 'releases', 'issues', or 'pull_requests')
            data (Any): Mock data to set
        """
        repo_full_name = f"{owner}/{repo}"
        if data_type not in self._data:
            raise ValueError(f"Invalid data type: {data_type}")
        self._data[data_type][repo_full_name] = data
        logger.debug(f"Set mock {data_type} data for {repo_full_name}")
    
    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get mock repository metadata."""
        repo_full_name = f"{owner}/{repo}"
        logger.debug(f"Mock: Getting repository info for {repo_full_name}")
        return self._data["repositories"].get(repo_full_name, {
            **MockGitHubData.DELTA_RS_REPO,  # Use delta-rs as default
            "name": repo,
            "full_name": repo_full_name
        })
    
    def get_releases(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Get mock repository releases."""
        repo_full_name = f"{owner}/{repo}"
        logger.debug(f"Mock: Getting releases for {repo_full_name}")
        return self._data["releases"].get(repo_full_name, MockGitHubData.DELTA_RS_RELEASES)
    
    def get_issues(self, owner: str, repo: str, state: str = 'all') -> List[Dict[str, Any]]:
        """Get mock repository issues."""
        repo_full_name = f"{owner}/{repo}"
        logger.debug(f"Mock: Getting issues for {repo_full_name}")
        all_issues = self._data["issues"].get(repo_full_name, 
            MockGitHubData.DELTA_RS_ISSUES + MockGitHubData.DELTA_RS_CLOSED_ISSUES)
        
        if state != 'all':
            return [issue for issue in all_issues if issue['state'] == state]
        return all_issues
    
    def get_pull_requests(self, owner: str, repo: str, state: str = 'all') -> List[Dict[str, Any]]:
        """Get mock repository pull requests."""
        repo_full_name = f"{owner}/{repo}"
        logger.debug(f"Mock: Getting pull requests for {repo_full_name}")
        prs_data = self._data["pull_requests"].get(repo_full_name, MockGitHubData.DELTA_RS_PRS)
        
        if state == 'all':
            return prs_data['open'] + prs_data['closed']
        return prs_data.get(state, []) 
