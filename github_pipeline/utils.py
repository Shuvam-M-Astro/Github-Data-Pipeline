from typing import Any
from datetime import datetime, timezone

import pandas as pd
from dagster import AssetExecutionContext, MetadataValue

def validate_repo_data(repo_data: dict[str, Any]):
    """Basic validation for repository data structure.
    Raises ValueError if expected keys or types are missing.
    """
    if not isinstance(repo_data, dict):
        raise ValueError("repo_data must be a dictionary.")
    if 'metadata' not in repo_data or not isinstance(repo_data['metadata'], dict):
        raise ValueError("repo_data must contain a 'metadata' dictionary.")
    if 'releases' not in repo_data or not isinstance(repo_data['releases'], list):
        raise ValueError("repo_data must contain a 'releases' list.")
    if 'issues' not in repo_data or not isinstance(repo_data['issues'], list):
        raise ValueError("repo_data must contain an 'issues' list.")
    if 'prs' not in repo_data or not isinstance(repo_data['prs'], list):
        raise ValueError("repo_data must contain a 'prs' list.")
    if 'html_url' not in repo_data['metadata']:
         raise ValueError("repo_data['metadata'] must contain 'html_url'.")


def create_markdown_report(context: AssetExecutionContext, report_data: dict[str, dict]) -> str:
    """Create a markdown report from the report data.

    Args:
        - context (AssetExecutionContext):
            Asset execution context.
        - report_data (dict[str, dict]):
            Data for the report as a dictionary.

    Returns:
        - str:
            Markdown formatted report.
    """
    # Convert dict with report data to markdown table
    df_report = pd.DataFrame.from_dict(report_data)
    md_report = df_report.to_markdown()

    context.add_output_metadata(
        metadata={
            'report': MetadataValue.md(md_report),
        }
    )

    return md_report


def calculate_avg_days_until_closed(items: list[dict[str, Any]]) -> float:
    """Calculate average days until items were closed.

    Args:
        - items (list[dict[str, Any]]):
            List of items (issues or PRs) with created_at and closed_at timestamps.

    Returns:
        - float:
            Average days until closure.
    """
    closed_items = [
        item for item in items
        if item.get('state') == 'closed' and item.get('created_at') and item.get('closed_at')
    ]

    if not closed_items:
        return 0.0

    total_days = 0
    for item in closed_items:
        created_at = datetime.fromisoformat(item['created_at'].replace('Z', '+00:00'))
        closed_at = datetime.fromisoformat(item['closed_at'].replace('Z', '+00:00'))
        days_until_closed = (closed_at - created_at).total_seconds() / (24 * 3600)  # Convert to days
        total_days += days_until_closed

    return total_days / len(closed_items)


def extract_metadata(repo_metadata: dict[str, Any]) -> dict[str, Any]:
    """Extracts list of fields from the repo metadata, issues and PRs and adds them to the report data dict.

    Args:
        - repo_metadata (dict[str, Any]):
            Metadata object for a GitHub repository.

    Returns:
        - dict[str, Any]:
            Extracted data from one repository as a column for the report.
    """
    metadata = repo_metadata['metadata']
    releases = repo_metadata['releases']
    issues = repo_metadata['issues']
    prs = repo_metadata['prs']

    # Count open and closed issues
    open_issues = sum(1 for issue in issues if issue.get('state') == 'open')
    closed_issues = sum(1 for issue in issues if issue.get('state') == 'closed')

    # Count open and closed PRs
    open_prs = sum(1 for pr in prs if pr.get('state') == 'open')
    closed_prs = sum(1 for pr in prs if pr.get('state') == 'closed')

    # Calculate average days until closure
    avg_days_issues = calculate_avg_days_until_closed(issues)
    avg_days_prs = calculate_avg_days_until_closed(prs)

    # set all fields for the report
    extracted_data = {
        'stars': metadata.get('stargazers_count'),
        'forks': metadata.get('forks_count'),
        'watchers': metadata.get('subscribers_count'),
        'releases': len(releases),
        'open issues': open_issues,
        'closed issues': closed_issues,
        'avg days until issue was closed': round(avg_days_issues, 1),
        'open PRs': open_prs,
        'closed PRs': closed_prs,
        'avg days until PR was closed': round(avg_days_prs, 1),
    }

    return extracted_data

