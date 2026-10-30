#!/usr/bin/enVv python3
#
# Copyright this project and it's contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import json
import logging
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

from rich.console import Console
from rich.markdown import Markdown

from . import setup_argparse, setup_logging

logger = logging.getLogger(__name__)

GRAPHQL_URL = "https://api.github.com/graphql"
REST_API_BASE = "https://api.github.com"
TARGET_FIELD_NAME = "PCC TSC Committee URL"
TARGET_LABEL_SUBSTRING = "2-annual-review"

def parse_project_url(project_url: str) -> tuple[str, int]:
    """Extracts organization login and project number from a GitHub project URL."""
    pattern = r"github\.com/(?:orgs|users)/([^/]+)/projects/(\d+)"
    match = re.search(pattern, project_url)
    if not match:
        raise ValueError(
            f"Invalid GitHub Project URL: '{project_url}'. Expected format: https://github.com/orgs/<org>/projects/<number>"
        )
    return match.group(1), int(match.group(2))


def run_graphql_query(token: str, query: str, variables: dict = None) -> dict:
    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "LFX-TAC-Auditor",
    }
    req = urllib.request.Request(GRAPHQL_URL, data=payload, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if "errors" in data:
                logger.error("GraphQL returned errors: %s", json.dumps(data["errors"], indent=2))
                sys.exit(1)
            return data["data"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        logger.exception("HTTP error %d querying GraphQL API: %s", e.code, error_body)
        sys.exit(1)


def create_github_issue(token: str, repo: str, title: str, body: str) -> None:
    url = f"{REST_API_BASE}/repos/{repo}/issues"
    payload = json.dumps({"title": title, "body": body}).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "LFX-TAC-Auditor",
    }
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            logger.info("Audit issue created successfully: %s", data.get("html_url"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        logger.exception("Failed to create issue in %s: %d - %s", repo, e.code, error_body)

def _extract_field_text(item: dict, field_name: str) -> str | None:
    """Extracts text content for a specific ProjectV2 field."""
    for val in item.get("fieldValues", {}).get("nodes", []):
        if val.get("field", {}).get("name") == field_name:
            return val.get("text")
    return None


def _audit_single_item(item: dict) -> dict | None:
    """Audits an individual project item and returns missing record dict if invalid."""
    content = item.get("content") or {}
    labels_data = content.get("labels", {}).get("nodes", [])
    label_names = [label.get("name", "") for label in labels_data]

    if not any(TARGET_LABEL_SUBSTRING in name for name in label_names):
        return None

    title = content.get("title", "Untitled Project")
    url = content.get("url", "")
    logger.info(f"Checking {title}")

    committee_url = _extract_field_text(item, TARGET_FIELD_NAME)
    if not committee_url or not committee_url.strip():
        logger.warning("Project '%s' is missing '%s'", title, TARGET_FIELD_NAME)
        return {"title": title, "url": url}

    logger.info(f"{TARGET_FIELD_NAME} set to {committee_url}")
    return None


def audit_project(org: str, project_number: int, token: str) -> list:
    query = """
    query($org: String!, $projectNumber: Int!, $cursor: String) {
      organization(login: $org) {
        projectV2(number: $projectNumber) {
          items(first: 100, after: $cursor) {
            pageInfo {
              hasNextPage
              endCursor
            }
            nodes {
              id
              fieldValues(first: 20) {
                nodes {
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    name
                    field { ... on ProjectV2FieldCommon { name } }
                  }
                  ... on ProjectV2ItemFieldTextValue {
                    text
                    field { ... on ProjectV2FieldCommon { name } }
                  }
                }
              }
              content {
                ... on Issue {
                  title
                  url
                  labels(first: 20) {
                    nodes {
                      name
                    }
                  }
                }
                ... on PullRequest {
                  title
                  url
                  labels(first: 20) {
                    nodes {
                      name
                    }
                  }
                }
                ... on DraftIssue {
                  title
                }
              }
            }
          }
        }
      }
    }
    """
    cursor = None
    all_missing = []

    while True:
        variables = {"org": org, "projectNumber": project_number, "cursor": cursor}
        logger.debug("Executing GraphQL fetch with cursor: %s", cursor)
        data = run_graphql_query(token, query, variables)
        project = data.get("organization", {}).get("projectV2")

        if not project:
            logger.error(
                "Project #%d under organization '%s' not found or inaccessible.",
                project_number,
                org,
            )
            sys.exit(1)

        items_data = project["items"]
        for item in items_data["nodes"]:
            missing_item = _audit_single_item(item)
            if missing_item:
                all_missing.append(missing_item)

        if not items_data["pageInfo"]["hasNextPage"]:
            break
        cursor = items_data["pageInfo"]["endCursor"]

    return all_missing

def main() -> int:
    parser = setup_argparse(
        description="Audit approved projects on GitHub Projects V2 for missing committee URLs."
    )

    parser.add_argument(
        "--project-url",
        help="URL of the Project Board (e.g. tac_agenda_gh_project_url)",
    )
    parser.add_argument(
        "--create-issue-in",
        help="Optional 'owner/repo' to automatically open an issue if missing URLs are found",
    )

    args = parser.parse_args()
    setup_logging(args.log_level)

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        logger.error("GitHub token must be provided via --token or GITHUB_TOKEN environment variable.")
        return 1


    try:
        org, project_number = parse_project_url(getattr(args, "project_url", None))
    except ValueError as e:
        logger.exception(str(e))
        return 1

    logger.info("Auditing organization '%s', Project #%d...", org, project_number)
    missing_records = audit_project(org, project_number, token)

    if not missing_records:
        logger.info(f"Audit clean: All approved projects have `{TARGET_FIELD_NAME}` set correctly.")
        return 0

    logger.warning("Audit completed: Found %d approved project(s) with missing URLs.", len(missing_records))

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_md = f"### ⚠️ Approved Projects Missing `{TARGET_FIELD_NAME}`\n\n"
    report_md += f"**Organization:** `{org}` | **Project:** `#{project_number}` | **Audit Date:** `{today_str}`\n\n"
    report_md += "| Project Title | Link |\n"
    report_md += "| :--- | :--- |\n"
    for rec in missing_records:
        link_str = f"[View Item]({rec['url']})" if rec["url"] else "N/A"
        report_md += f"| {rec['title']} | {link_str} |\n"

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        logger.debug("Writing audit findings to GITHUB_STEP_SUMMARY (%s)", summary_path)
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(report_md)

    create_issue_in = getattr(args, "create_issue_in", None)
    if create_issue_in:
        issue_title = f"[Audit] Missing {TARGET_FIELD_NAME} for {org} Board #{project_number} ({today_str})"
        logger.info("Creating tracking issue in '%s'...", create_issue_in)
        create_github_issue(token, create_issue_in, issue_title, report_md)
    else:
        console = Console()
        console.print()
        console.print(Markdown(report_md))

    return 0

if __name__ == "__main__":
    sys.exit(main())
