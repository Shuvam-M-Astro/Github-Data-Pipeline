import requests
from datetime import datetime
import time

# Configuration 
GITHUB_TOKEN = ""
REPO = "delta-io/delta-rs"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}


def get_avg_close_time(url, is_issue=True):
    params = {
        "state": "closed",
        "per_page": 100,
        "page": 1
    }
    total_seconds = 0
    count = 0

    while True:
        res = requests.get(url, headers=HEADERS, params=params)
        if res.status_code != 200:
            print(f" Error: {res.status_code} - {res.text}")
            break
        items = res.json()
        if not items:
            break

        for item in items:
            if is_issue and "pull_request" in item:
                continue
            if not item.get("closed_at"):
                continue
            created = datetime.strptime(item["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            closed = datetime.strptime(item["closed_at"], "%Y-%m-%dT%H:%M:%SZ")
            total_seconds += (closed - created).total_seconds()
            count += 1

        params["page"] += 1
        time.sleep(0.2)

    avg_days = (total_seconds / 86400) / count if count > 0 else 0
    return avg_days, count

# === Run Calculation ===
issues_url = f"https://api.github.com/repos/{REPO}/issues"
prs_url = f"https://api.github.com/repos/{REPO}/pulls"

avg_issue_days, issue_count = get_avg_close_time(issues_url, is_issue=True)
avg_pr_days, pr_count = get_avg_close_time(prs_url, is_issue=False)

# === Print Final Result ===
print(f"Repository: {REPO}")
print(f"Issues Closed: {issue_count} | Avg Days: {avg_issue_days:.1f}")
print(f"PRs Closed:    {pr_count} | Avg Days: {avg_pr_days:.1f}")