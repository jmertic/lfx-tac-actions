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

from lfx_tac_actions.updatetacagendaitems import *

class TestUpdateTACAgendaItems(unittest.TestCase):
    
    @unittest.mock.patch.dict(os.environ, {"TAC_AGENDA_GH_PROJECT_URL": ""}, clear=True)
    def testMainNoLandscapeUrl(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmpfilepath = os.path.join(tempdir, 'someFileInTmpDir.csv')
            with unittest.mock.patch('argparse.ArgumentParser.parse_args') as mock:
                mock.return_value = argparse.Namespace(output=tmpfilepath)
                main()
                self.assertFalse(os.path.exists(tmpfilepath), f"File '{tmpfilepath}' exists.")

    @responses.activate
    @unittest.mock.patch.dict(os.environ, {"TAC_AGENDA_GH_PROJECT_URL": "https://github.com/orgs/openmainframeproject/projects/21"}, clear=True)
    @unittest.mock.patch('subprocess.run')
    def testMain(self, mock_run):
        mock_result = unittest.mock.Mock()
        mock_result.stdout = '{"items":[{"assignees":["carolalynn"],"content":{"body":"","number":473,"repository":"AcademySoftwareFoundation/tac","title":"D&I Working Group","type":"Issue","url":"https://github.com/AcademySoftwareFoundation/tac/issues/473"},"id":"PVTI_lADOAm6tAs4AS_w4zgJSO7E","labels":["2-annual-review"],"landscape URL":"https://landscape.aswf.io/card-mode?project=working-group&selected=d-i-working-group","pCC Project ID":"a092M00001KWjDZQA1","pCC TSC Committee ID":"ac9cbe7f-0dc8-4be0-b404-cb7b9b0bb22f","repository":"https://github.com/AcademySoftwareFoundation/tac","scheduled Date":"2024-12-11","status":"Next Meeting Agenda Items","title":"D&I Working Group"}],"totalCount":32}'
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as tempdir:
            tmpfilepath = os.path.join(tempdir, 'someFileInTmpDir.csv')
            with unittest.mock.patch('argparse.ArgumentParser.parse_args') as mock:
                mock.return_value = argparse.Namespace(output=tmpfilepath)
                main()

                with open(tmpfilepath, 'r') as tmpfile:
                    self.maxDiff = None
                    self.assertEqual(tmpfile.read(),'''title,url,number,scheduled_date,status,last_review_date,meeting_label
D&I Working Group,https://github.com/AcademySoftwareFoundation/tac/issues/473,473,2024-12-11,Next Meeting Agenda Items,,2-annual-review
''')

if __name__ == '__main__':
    unittest.main()
