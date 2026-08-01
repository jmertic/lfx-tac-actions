#!/usr/bin/env python3
#
# Copyright this project and it's contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import io
import os
import sys
import unittest
from unittest.mock import Mock, patch

from lfx_tac_actions.updatetacagendaitems import main


class TestUpdateTACAgendaItems(unittest.TestCase):

    def testMainNoTACAgendaUrl(self):
        captured_stdout = io.StringIO()
        with (
            self.assertLogs(level="CRITICAL") as cm,
            patch("sys.stdout", new=captured_stdout),
        ):
            main(["--tac_agenda_gh_project_url", ""])

        self.assertEqual(captured_stdout.getvalue(), "")
        self.assertTrue(
            any(
                "Invalid value for tac_agenda_gh_project_url" in log_msg
                for log_msg in cm.output
            )
        )

    def testBadLogLevel(self):
        with self.assertRaises(ValueError) as cm:
            main(["-l", "BAD", "--tac_agenda_gh_project_url", "foo"])
        self.assertIn("Invalid log level: BAD", str(cm.exception))

    def testMainBrokenTACAgendaUrls(self):
        brokenurls = [
            "https://google.com/d/d",
            "https://github.com/orgs/openmainframeproject/settings",
        ]
        for brokenurl in brokenurls:
            captured_stdout = io.StringIO()
            with (
                self.assertLogs(level="CRITICAL") as cm,
                patch("sys.stdout", new=captured_stdout),
            ):
                main(["--tac_agenda_gh_project_url", brokenurl])

            self.assertEqual(
                captured_stdout.getvalue(),
                "",
                f"Expected no stdout output for broken URL '{brokenurl}'",
            )
            self.assertTrue(
                any(
                    "Invalid value for tac_agenda_gh_project_url" in log_msg
                    for log_msg in cm.output
                )
            )

    @patch("subprocess.run")
    def testMainInvalidJSONResponse(self, mock_run):
        mock_result = Mock()
        mock_result.stdout = "error 12121212"
        mock_result.stderr = "foo"
        mock_run.return_value = mock_result

        captured_stdout = io.StringIO()
        with (
            self.assertLogs(level="ERROR") as cm,
            patch("sys.stdout", new=captured_stdout),
        ):
            main(
                [
                    "--tac_agenda_gh_project_url",
                    "https://github.com/orgs/openmainframeproject/projects/21",
                ]
            )

        self.maxDiff = None
        self.assertEqual(captured_stdout.getvalue(), "")
        self.assertTrue(
            any(
                "Invalid response from gh client" in log_msg
                for log_msg in cm.output
            )
        )

    @patch.dict(
        os.environ,
        {
            "TAC_AGENDA_GH_PROJECT_URL": "https://github.com/orgs/openmainframeproject/projects/21"
        },
        clear=True,
    )
    @patch("subprocess.run")
    def testMain(self, mock_run):
        labelList = {
            '"2-annual-review"': "2-annual-review",
            '"1-new-project-wg"': "1-new-project-wg",
            '"2-annual-review-tac"': "2-annual-review",
            '"2-annual-review-sig"': "2-annual-review-sig",
            '"3-tac-meeting-long"': "3-tac-meeting-long",
            '"4-tac-meeting-short"': "4-tac-meeting-short",
            '"5-annual-review-sig"': "",
        }
        for label, output in labelList.items():
            mock_result = Mock()
            mock_result.stdout = (
                '{"items":[{"assignees":["carolalynn"],"content":{"body":"","number":473,'
                '"repository":"AcademySoftwareFoundation/tac","title":"D&I Working Group","type":"Issue",'
                '"url":"https://github.com/AcademySoftwareFoundation/tac/issues/473"},'
                '"id":"PVTI_lADOAm6tAs4AS_w4zgJSO7E","labels":['
                + label
                + '],"landscape URL":"https://landscape.aswf.io/card-mode?project=working-group&selected=d-i-working-group",'
                '"pCC Project ID":"a092M00001KWjDZQA1","pCC TSC Committee ID":"ac9cbe7f-0dc8-4be0-b404-cb7b9b0bb22f",'
                '"repository":"https://github.com/AcademySoftwareFoundation/tac","scheduled Date":"2024-12-11",'
                '"status":"Next Meeting Agenda Items","title":"D&I Working Group"}],"totalCount":32}'
            )
            mock_run.return_value = mock_result

            captured_stdout = io.StringIO()
            with patch("sys.stdout", new=captured_stdout):
                main(
                    [
                        "--tac_agenda_gh_project_url",
                        "https://github.com/orgs/openmainframeproject/projects/21",
                    ]
                )

            self.maxDiff = None
            expected_csv = (
                "title,url,number,scheduled_date,status,last_review_date,meeting_label\r\n"
                f"D&I Working Group,https://github.com/AcademySoftwareFoundation/tac/issues/473,473,2024-12-11,Next Meeting Agenda Items,,{output}\r\n"
            )
            self.assertEqual(captured_stdout.getvalue(), expected_csv)


if __name__ == "__main__":
    unittest.main()
