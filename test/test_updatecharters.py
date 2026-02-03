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
from pathlib import Path

from lfx_tac_actions.updatecharters import main

class TestUpdateCharters(unittest.TestCase):
    
    def testMainNoSlug(self):
        with self.assertRaises(SystemExit) as cm:
            main(["-o",""])
        self.assertEqual(cm.exception.code, 2)

    def testBadLogLevel(self):
        with self.assertRaises(ValueError) as cm:
            main(["-l","BAD","--slug","foo"])
        self.assertIn('Invalid log level: BAD', str(cm.exception))

    @responses.activate
    def testMainBadURL(self):
        responses.add(
            method=responses.GET,
            url="https://api-gw.platform.linuxfoundation.org/project-service/v1/public/projects?$filter=parentSlug%20eq%20lfenergy%20and%20status%20eq%20Active&pageSize=2000&orderBy=name",
            status=404,
            body="Not here!"
            )
        
        with self.assertLogs(level="CRITICAL") as cm:
            main(["--slug","lfenergy"])
        self.assertIn('Error getting charters at https://api-gw.platform.linuxfoundation.org/project-service/v1/public/projects?$filter=parentSlug%20eq%20lfenergy%20and%20status%20eq%20Active&pageSize=2000&orderBy=name', str(cm.output[0]))

    @responses.activate
    def testMain(self):
        responses.add(
            method=responses.GET,
            url="https://api-gw.platform.linuxfoundation.org/project-service/v1/public/projects?$filter=parentSlug%20eq%20lfenergy%20and%20status%20eq%20Active&pageSize=2000&orderBy=name",
            json={
              "Data": [
                {
                  "CharterURL": "https://github.com/lf-energy/foundation/blob/main/project_charters/arras_charter.pdf",
                  "Name": "Arras",
                  "Slug": "arras",
                },
                {
                  "Name": "CitrineOS",
                  "Slug": "citrineos",
                },
                {
                  "CharterURL": "https://lfx-cdn-prod.s3.us-east-1.amazonaws.com/project-artifacts/citylearn/citylearn_Charter.pdf?v=1764754270554",
                  "Name": "CityLearn",
                  "Slug": "citylearn",
                },
                {
                  "CharterURL": "https://github.com/lf-energy/foundation/blob/master/project_charters/fledgepower_charter.pdf",
                  "Name": "FledgePower",
                  "Slug": "fledgepower",
                },
                {
                  "CharterURL": "https://badurl.com/badcharter.pdf",
                  "Name": "Bad Project",
                  "Slug": "badproject",
                },
              ],
              "Metadata": {
                "Offset": 0,
                "PageSize": 2000,
                "TotalSize": 43
              }
}
            )
        responses.add(
            method=responses.GET,
            url="https://raw.githubusercontent.com/lf-energy/foundation/main/project_charters/arras_charter.pdf",
            body="blah blah blah")
        responses.add(
            method=responses.GET,
            url="https://lfx-cdn-prod.s3.us-east-1.amazonaws.com/project-artifacts/citylearn/citylearn_Charter.pdf?v=1764754270554",
            body="blah blah blah")
        responses.add(
            method=responses.GET,
            url="https://raw.githubusercontent.com/lf-energy/foundation/master/project_charters/fledgepower_charter.pdf",
            body="blah blah blah")
        responses.add(
            method=responses.GET,
            url="https://badurl.com/badcharter.pdf",
            status=404,
            body="Not here!"
            )


        with tempfile.TemporaryDirectory() as tempdir:
            with self.assertLogs(level="ERROR") as cm:
                main(["-o",tempdir,"--slug","lfenergy"])
            
            self.assertTrue(os.path.isfile(Path(tempdir,"arras_charter.pdf")))
            self.assertFalse(os.path.isfile(Path(tempdir,"citrineos_charter.pdf")))
            self.assertFalse(os.path.isfile(Path(tempdir,"badproject_charter.pdf")))
            self.assertTrue(os.path.isfile(Path(tempdir,"citylearn_charter.pdf")))
            self.assertTrue(os.path.isfile(Path(tempdir,"fledgepower_charter.pdf")))
            self.assertIn("Error getting file https://badurl.com/badcharter.pdf - '404 Client Error: Not Found for url: https://badurl.com/badcharter.pdf", str(cm.output[0]))

if __name__ == '__main__':
    unittest.main()
