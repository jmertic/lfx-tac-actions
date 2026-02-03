#!/usr/bin/env python3
#
# Copyright this project and it's contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import unittest
import tempfile
import os
import responses
import argparse

from lfx_tac_actions.updatetacagendaitems import main

class TestUpdateTACAgendaItems(unittest.TestCase):
    
    def testMainNoTACAgendaUrl(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmpfilepath = os.path.join(tempdir, 'someFileInTmpDir.csv')
            main(["-o",tmpfilepath,"--tac_agenda_gh_project_url",""])
            self.assertFalse(os.path.exists(tmpfilepath), f"File '{tmpfilepath}' exists.")

    def testBadLogLevel(self):
        with self.assertRaises(ValueError) as cm:
            main(["-l","BAD","--tac_agenda_gh_project_url","foo"])
        self.assertIn('Invalid log level: BAD', str(cm.exception))

    def testMainBrokenTACAgendaUrls(self):
        brokenurls = [
            "https://google.com/d/d",
            "https://github.com/orgs/openmainframeproject/settings",
            ]
        for brokenurl in brokenurls:
            with tempfile.TemporaryDirectory() as tempdir:
                tmpfilepath = os.path.join(tempdir, 'someFileInTmpDir.csv')
                main(["-o",tmpfilepath,"--tac_agenda_gh_project_url",brokenurl])
                self.assertFalse(os.path.exists(tmpfilepath), f"File '{tmpfilepath}' exists.")
    
    @unittest.mock.patch('subprocess.run')
    def testMainInvalidJSONResponse(self, mock_run):
        mock_result = unittest.mock.Mock()
        mock_result.stdout = 'error 12121212'
        mock_result.stderr = 'foo'
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as tempdir:
            tmpfilepath = os.path.join(tempdir, 'someFileInTmpDir.csv')
            main(["-o",tmpfilepath,"--tac_agenda_gh_project_url","https://github.com/orgs/openmainframeproject/projects/21"])
            self.assertFalse(os.path.exists(tmpfilepath), f"File '{tmpfilepath}' exists.")
    
    @unittest.mock.patch.dict(os.environ, {"TAC_AGENDA_GH_PROJECT_URL": "https://github.com/orgs/openmainframeproject/projects/21"}, clear=True)
    @unittest.mock.patch('subprocess.run')
    def testMain(self, mock_run):
        labelList = {
            '"2-annual-review"': '2-annual-review',
            '"1-new-project-wg"': '1-new-project-wg',
            '"2-annual-review-tac"': '2-annual-review',
            '"2-annual-review-sig"': '2-annual-review-sig',
            '"3-tac-meeting-long"': '3-tac-meeting-long',
            '"4-tac-meeting-short"': '4-tac-meeting-short',
            '"5-annual-review-sig"': '',
            }
        for label, output in labelList.items():
            mock_result = unittest.mock.Mock()
            mock_result.stdout = '{"items":[{"assignees":["carolalynn"],"content":{"body":"","number":473,"repository":"AcademySoftwareFoundation/tac","title":"D&I Working Group","type":"Issue","url":"https://github.com/AcademySoftwareFoundation/tac/issues/473"},"id":"PVTI_lADOAm6tAs4AS_w4zgJSO7E","labels":['+label+'],"landscape URL":"https://landscape.aswf.io/card-mode?project=working-group&selected=d-i-working-group","pCC Project ID":"a092M00001KWjDZQA1","pCC TSC Committee ID":"ac9cbe7f-0dc8-4be0-b404-cb7b9b0bb22f","repository":"https://github.com/AcademySoftwareFoundation/tac","scheduled Date":"2024-12-11","status":"Next Meeting Agenda Items","title":"D&I Working Group"}],"totalCount":32}'
            mock_run.return_value = mock_result

            with tempfile.TemporaryDirectory() as tempdir:
                tmpfilepath = os.path.join(tempdir, 'someFileInTmpDir.csv')
                main(["-o",tmpfilepath,"--tac_agenda_gh_project_url","https://github.com/orgs/openmainframeproject/projects/21"])

                with open(tmpfilepath, 'r') as tmpfile:
                    self.maxDiff = None
                    self.assertEqual(tmpfile.read(),f'''title,url,number,scheduled_date,status,last_review_date,meeting_label
D&I Working Group,https://github.com/AcademySoftwareFoundation/tac/issues/473,473,2024-12-11,Next Meeting Agenda Items,,{output}
''')

if __name__ == '__main__':
    unittest.main()
