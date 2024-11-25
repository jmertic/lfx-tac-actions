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

from lfx_tac_actions.updatetacmembers import *

class TestUpdateTACMembers(unittest.TestCase):
    
    @unittest.mock.patch.dict(os.environ, {"LFX_TAC_COMMITTEE_URL": ""}, clear=True)
    def testMainNoLandscapeUrl(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmpfilepath = os.path.join(tempdir, 'someFileInTmpDir.csv')
            with unittest.mock.patch('argparse.ArgumentParser.parse_args') as mock:
                mock.return_value = argparse.Namespace(output=tmpfilepath)
                main()
                self.assertFalse(os.path.exists(tmpfilepath), f"File '{tmpfilepath}' exists.")

    @responses.activate
    @unittest.mock.patch.dict(os.environ, {"LFX_TAC_COMMITTEE_URL": "https://projectadmin.lfx.linuxfoundation.org/project/a0941000002wBymAAE/collaboration/committees/163b26f7-a49b-40a3-89bb-e0592296c003"}, clear=True)
    def testMain(self):
        responses.add(
            method=responses.GET,
            url="https://api-gw.platform.linuxfoundation.org/project-service/v2/public/projects/a0941000002wBymAAE/committees/163b26f7-a49b-40a3-89bb-e0592296c003/members",
            json={
              "Data": [
                {
                  "AppointedBy": "Vote of TSC Committee",
                  "FirstName": "Andrea",
                  "LastName": "Orth",
                  "Role": "None",
                  "Status": "Active",
                  "VotingStartDate": "2022-06-21",
                  "VotingStatus": "Voting Rep",
                  "MemberID": "0032M000032nKeAQAU",
                  "OrganizationID": "0014100000Te2cmAAB",
                  "AboutMe": {
                    "Description": "I've worked in IT for over 25 years at the same Fortune 50 company. I started out as a mainframe developer working with COBOL and DB2. Early in my career I worked with the GenevaERS product and came to understand the scalability and efficiency the mainframe provides. During my career, I've had had different roles including Scrum Master and Product Owner. \n\nI have served as the Vice Chair of the GenevaERS Technical Steering Committee sponsored by the Linux Foundation's Open Mainframe Project since the project's inception.  Among other things, I have acted as Scrum Master, run communications for the project, provide customer input and direction, and provided an independent voice.  I was recently appointed the Chair of the project.\n\nHobbies include collecting hobbies and caring for my over 30 pets.",
                    "GitHub": "https://github.com/AOrthVector",
                    "LinkedIn": "https://linkedin.com/in/andrea-orth"
                  },
                  "CreatedDate": "2022-06-21T17:47:53.358Z",
                  "ID": "e48fee2b-9848-40e1-bb5b-4aa6e350e90e",
                  "LogoURL": "https://avatars0.githubusercontent.com/u/61636929?v=4",
                  "Organization": {
                    "ID": "0014100000Te2cmAAB",
                    "LogoURL": "https://lf-master-organization-logos-prod.s3.us-east-2.amazonaws.com/state-farm-mutual-insurance-company.svg",
                    "Name": "State Farm Mutual Automobile Insurance Company"
                  },
                  "SystemModStamp": "2024-01-16T21:13:07.501Z",
                  "Title": "Scrum Master"
                },
                ]
              }
            )
        with tempfile.TemporaryDirectory() as tempdir:
            tmpfilepath = os.path.join(tempdir, 'someFileInTmpDir.csv')
            with unittest.mock.patch('argparse.ArgumentParser.parse_args') as mock:
                mock.return_value = argparse.Namespace(output=tmpfilepath)
                main()

                with open(tmpfilepath, 'r') as tmpfile:
                    self.maxDiff = None
                    self.assertEqual(tmpfile.read(),'''Full Name,Account Name: Account Name,Appointed By,Voting Status,Special Role,Title,HeadshotURL\nAndrea Orth,State Farm Mutual Automobile Insurance Company,Vote of TSC Committee,Voting Rep,None,Scrum Master,https://avatars0.githubusercontent.com/u/61636929?v=4\n''')

if __name__ == '__main__':
    unittest.main()
