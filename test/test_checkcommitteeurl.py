#!/usr/bin/env python3
#
# Copyright this project and it's contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import argparse
import sys
import io
import json
import os
import shutil
import tempfile
import unittest
import urllib.error
from unittest.mock import MagicMock, mock_open, patch

# Adjust import to match your actual module structure
from lfx_tac_actions.checkcommitteeurl import (
    TARGET_FIELD_NAME,
    audit_project,
    create_github_issue,
    main,
    parse_project_url,
    run_graphql_query,
)


class TestParseProjectUrl(unittest.TestCase):
    def test_parse_valid_org_url(self):
        url = "https://github.com/orgs/hyperledger/projects/19"
        org, proj_num = parse_project_url(url)
        self.assertEqual(org, "hyperledger")
        self.assertEqual(proj_num, 19)

    def test_parse_valid_users_url(self):
        url = "https://github.com/users/testuser/projects/42"
        org, proj_num = parse_project_url(url)
        self.assertEqual(org, "testuser")
        self.assertEqual(proj_num, 42)

    def test_parse_invalid_url_raises_value_error(self):
        invalid_urls = [
            "https://github.com/hyperledger/repo",
            "https://example.com/orgs/test/projects/1",
            "not-a-url",
            None,
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                with self.assertRaises((ValueError, TypeError)):
                    parse_project_url(url)


class TestRunGraphqlQuery(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_run_graphql_query_success(self, mock_urlopen):
        expected_data = {"organization": {"projectV2": {"id": "123"}}}
        response_bytes = json.dumps({"data": expected_data}).encode("utf-8")

        mock_resp = MagicMock()
        mock_resp.read.return_value = response_bytes
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        result = run_graphql_query("fake-token", "query { test }")
        self.assertEqual(result, expected_data)

    @patch("urllib.request.urlopen")
    def test_run_graphql_query_with_errors_exits(self, mock_urlopen):
        response_bytes = json.dumps({"errors": [{"message": "Field not found"}]}).encode("utf-8")
        mock_resp = MagicMock()
        mock_resp.read.return_value = response_bytes
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        with self.assertRaises(SystemExit) as ctx:
            run_graphql_query("fake-token", "query { test }")
        self.assertEqual(ctx.exception.code, 1)

    @patch("urllib.request.urlopen")
    def test_run_graphql_query_http_error_exits(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://api.github.com/graphql",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=io.BytesIO(b"Bad credentials"),
        )

        with self.assertRaises(SystemExit) as ctx:
            run_graphql_query("bad-token", "query { test }")
        self.assertEqual(ctx.exception.code, 1)


class TestCreateGithubIssue(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_create_issue_success(self, mock_urlopen):
        response_bytes = json.dumps({"html_url": "https://github.com/org/repo/issues/1"}).encode("utf-8")
        mock_resp = MagicMock()
        mock_resp.read.return_value = response_bytes
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        # Should execute cleanly without raising an unhandled exception
        create_github_issue("fake-token", "org/repo", "Issue Title", "Issue Body")
        mock_urlopen.assert_called_once()

    @patch("urllib.request.urlopen")
    def test_create_issue_http_error_handled(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://api.github.com/repos/org/repo/issues",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=io.BytesIO(b"Repository not found"),
        )

        # Should log the error and return without raising/exiting
        create_github_issue("fake-token", "org/missing-repo", "Issue Title", "Issue Body")
        mock_urlopen.assert_called_once()


class TestAuditProject(unittest.TestCase):
    @patch("lfx_tac_actions.checkcommitteeurl.run_graphql_query")
    def test_audit_project_detects_missing_url(self, mock_query):
        mock_query.return_value = {
            "organization": {
                "projectV2": {
                    "items": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "nodes": [
                            # Item 1: Has label, missing committee URL -> FLAGGED
                            {
                                "fieldValues": {
                                    "nodes": [
                                        {"field": {"name": TARGET_FIELD_NAME}, "text": ""}
                                    ]
                                },
                                "content": {
                                    "title": "Missing URL Project",
                                    "url": "https://github.com/org/repo/issues/1",
                                    "labels": {"nodes": [{"name": "2-annual-review"}]},
                                },
                            },
                            # Item 2: Has label, has committee URL -> OK
                            {
                                "fieldValues": {
                                    "nodes": [
                                        {"field": {"name": TARGET_FIELD_NAME}, "text": "https://tsc.example.org"}
                                    ]
                                },
                                "content": {
                                    "title": "Valid Project",
                                    "url": "https://github.com/org/repo/issues/2",
                                    "labels": {"nodes": [{"name": "stage: 2-annual-review"}]},
                                },
                            },
                            # Item 3: Missing target label -> IGNORED
                            {
                                "fieldValues": {
                                    "nodes": [
                                        {"field": {"name": TARGET_FIELD_NAME}, "text": ""}
                                    ]
                                },
                                "content": {
                                    "title": "Other Project",
                                    "url": "https://github.com/org/repo/issues/3",
                                    "labels": {"nodes": [{"name": "bug"}]},
                                },
                            },
                        ],
                    }
                }
            }
        }

        missing = audit_project("org", 1, "token")
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0]["title"], "Missing URL Project")
        self.assertEqual(missing[0]["url"], "https://github.com/org/repo/issues/1")

    @patch("lfx_tac_actions.checkcommitteeurl.run_graphql_query")
    def test_audit_project_pagination(self, mock_query):
        page1 = {
            "organization": {
                "projectV2": {
                    "items": {
                        "pageInfo": {"hasNextPage": True, "endCursor": "cursor-1"},
                        "nodes": [
                            {
                                "fieldValues": {
                                    "nodes": [{"field": {"name": TARGET_FIELD_NAME}, "text": ""}]
                                },
                                "content": {
                                    "title": "Project Page 1",
                                    "url": "https://github.com/org/repo/issues/1",
                                    "labels": {"nodes": [{"name": "2-annual-review"}]},
                                },
                            }
                        ],
                    }
                }
            }
        }
        page2 = {
            "organization": {
                "projectV2": {
                    "items": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "nodes": [
                            {
                                "fieldValues": {
                                    "nodes": [
                                        {"field": {"name": TARGET_FIELD_NAME}, "text": "https://valid.org"}
                                    ]
                                },
                                "content": {
                                    "title": "Project Page 2",
                                    "url": "https://github.com/org/repo/issues/2",
                                    "labels": {"nodes": [{"name": "2-annual-review"}]},
                                },
                            }
                        ],
                    }
                }
            }
        }
        mock_query.side_effect = [page1, page2]

        missing = audit_project("org", 1, "token")
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0]["title"], "Project Page 1")
        self.assertEqual(mock_query.call_count, 2)

    @patch("lfx_tac_actions.checkcommitteeurl.run_graphql_query")
    def test_audit_project_not_found_exits(self, mock_query):
        mock_query.return_value = {"organization": {"projectV2": None}}

        with self.assertRaises(SystemExit) as ctx:
            audit_project("org", 999, "token")
        self.assertEqual(ctx.exception.code, 1)


class TestMain(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Mock setup_argparse and setup_logging
        self.argparse_patcher = patch("lfx_tac_actions.checkcommitteeurl.setup_argparse")
        self.logging_patcher = patch("lfx_tac_actions.checkcommitteeurl.setup_logging")
        self.mock_setup_argparse = self.argparse_patcher.start()
        self.mock_setup_logging = self.logging_patcher.start()

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--log-level", default="INFO")
        self.mock_setup_argparse.return_value = self.parser

    def tearDown(self):
        self.argparse_patcher.stop()
        self.logging_patcher.stop()
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch.dict(os.environ, {}, clear=True)
    def test_main_missing_token_returns_1(self):
        test_args = ["prog", "--project-url", "https://github.com/orgs/test/projects/1"]
        with patch.object(sys, "argv", test_args):
            exit_code = main()
        self.assertEqual(exit_code, 1)

    @patch.dict(os.environ, {"GITHUB_TOKEN": "valid-token"})
    def test_main_invalid_project_url_returns_1(self):
        test_args = ["prog", "--project-url", "invalid-url"]
        with patch.object(sys, "argv", test_args):
            exit_code = main()
        self.assertEqual(exit_code, 1)

    @patch.dict(os.environ, {"GITHUB_TOKEN": "valid-token"})
    @patch("lfx_tac_actions.checkcommitteeurl.audit_project")
    def test_main_clean_audit_returns_0(self, mock_audit):
        mock_audit.return_value = []
        test_args = ["prog", "--project-url", "https://github.com/orgs/hyperledger/projects/19"]

        with patch.object(sys, "argv", test_args):
            exit_code = main()

        self.assertEqual(exit_code, 0)
        mock_audit.assert_called_once_with("hyperledger", 19, "valid-token")

    @patch.dict(os.environ, {"GITHUB_TOKEN": "valid-token"})
    @patch("lfx_tac_actions.checkcommitteeurl.create_github_issue")
    @patch("lfx_tac_actions.checkcommitteeurl.audit_project")
    def test_main_with_missing_records_and_issue_creation(self, mock_audit, mock_create_issue):
        mock_audit.return_value = [
            {"title": "Test Project", "url": "https://github.com/org/repo/issues/10"}
        ]
        summary_file = os.path.join(self.temp_dir, "step_summary.md")

        with patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": summary_file}):
            test_args = [
                "prog",
                "--project-url",
                "https://github.com/orgs/hyperledger/projects/19",
                "--create-issue-in",
                "hyperledger/tac",
            ]
            with patch.object(sys, "argv", test_args):
                exit_code = main()

        self.assertEqual(exit_code, 0)

        # Verify Issue Creation call
        mock_create_issue.assert_called_once()
        call_args = mock_create_issue.call_args[0]
        self.assertEqual(call_args[0], "valid-token")
        self.assertEqual(call_args[1], "hyperledger/tac")
        self.assertIn("Missing PCC TSC Committee URL", call_args[2])
        self.assertIn("Test Project", call_args[3])

        # Verify Step Summary written
        self.assertTrue(os.path.exists(summary_file))
        with open(summary_file, "r", encoding="utf-8") as f:
            summary_content = f.read()
        self.assertIn("Test Project", summary_content)
        self.assertIn(TARGET_FIELD_NAME, summary_content)

    @patch.dict(os.environ, {"GITHUB_TOKEN": "valid-token"})
    @patch("lfx_tac_actions.checkcommitteeurl.audit_project")
    def test_main_prints_to_stdout_when_create_issue_not_set(self, mock_audit):
        mock_audit.return_value = [
            {"title": "CLI Output Project", "url": "https://github.com/org/repo/issues/10"}
        ]
        test_args = [
            "prog",
            "--project-url",
            "https://github.com/orgs/hyperledger/projects/19",
        ]

        with patch.object(sys, "argv", test_args), patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            exit_code = main()

        self.assertEqual(exit_code, 0)
        output = mock_stdout.getvalue()
        self.assertIn("Approved Projects Missing PCC TSC Committee URL", output)
        self.assertIn("CLI Output Project", output)

    @patch.dict(os.environ, {"GITHUB_TOKEN": "valid-token"})
    @patch("lfx_tac_actions.checkcommitteeurl.create_github_issue")
    @patch("lfx_tac_actions.checkcommitteeurl.audit_project")
    def test_main_creates_issue_when_create_issue_set(self, mock_audit, mock_create_issue):
        mock_audit.return_value = [
            {"title": "Issue Project", "url": "https://github.com/org/repo/issues/20"}
        ]
        test_args = [
            "prog",
            "--project-url",
            "https://github.com/orgs/hyperledger/projects/19",
            "--create-issue-in",
            "hyperledger/tac",
        ]

        with patch.object(sys, "argv", test_args), patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            exit_code = main()

        self.assertEqual(exit_code, 0)
        mock_create_issue.assert_called_once()
        # Verify the report wasn't also dumped to stdout
        self.assertNotIn("### ⚠️ Approved Projects Missing", mock_stdout.getvalue())

if __name__ == "__main__":
    unittest.main()
