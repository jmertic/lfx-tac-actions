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

from lfx_tac_actions.updateprojects import main

class TestUpdateProjects(unittest.TestCase):
    
    @unittest.mock.patch.dict(os.environ, {"LANDSCAPE_URL": ""}, clear=True)
    def testMainNoLandscapeUrl(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmpfilepath = os.path.join(tempdir, 'someFileInTmpDir.csv')
            with unittest.mock.patch('argparse.ArgumentParser.parse_args') as mock:
                mock.return_value = argparse.Namespace(output=tmpfilepath)
                main()
                self.assertFalse(os.path.exists(tmpfilepath), f"File '{tmpfilepath}' exists.")

    @responses.activate
    @unittest.mock.patch.dict(os.environ, {"LANDSCAPE_URL": "https://landscape.aswf.io"}, clear=True)
    def testMain(self):
        responses.add(
            method=responses.GET,
            url="https://landscape.aswf.io/api/projects/all.json",
            json=[
                {
                    "category": "ASWF Projects",
                    "homepage_url": "https://github.com/vfx-rs",
                    "id": "aswf-projects--all--aswf-language-interop-project",
                    "logo_url": "https://aswf.landscape2.io/logos/803e21319d55195829c27a3bc448d43e8f14dbcf544e4d44418299df3a3cca61.svg",
                    "name": "ASWF Language Interop Project",
                    "subcategory": "All",
                    "accepted_at": "2023-10-20",
                    "additional_categories": [
                      {
                        "category": "Math and Simulation",
                        "subcategory": "Math Foundations"
                      }
                    ],
                    "annotations": {
                      "slug": "aswf-language-interop-project",
                      "chair": "Scott Wilson",
                      "ical_url": "https://webcal.prod.itx.linuxfoundation.org/lfx/lfv8NMKI8tcp96N5tb",
                      "next_annual_review_date": "2025-03-19",
                      "calendar_url": "https://zoom-lfx.platform.linuxfoundation.org/meetings/aswf-language-interop-project"
                    },
                    "artwork_url": "https://artwork.aswf.io/projects/aswf-language-interop-project/",
                    "chat_channel": "#rust",
                    "country": "United States",
                    "crunchbase_url": "https://www.crunchbase.com/organization/academy-software-foundation",
                    "description": "The mission of the Project is to enable interoperability between various programming languages across each of the libraries used by the media and entertainment industry.",
                    "devstats_url": "https://insights.lfx.linuxfoundation.org/foundation/aswf/overview?project=aswf-language-interop-project",
                    "latest_annual_review_at": "2024-03-20",
                    "latest_annual_review_url": "https://github.com/AcademySoftwareFoundation/tac/issues/489",
                    "mailing_list_url": "https://lists.aswf.io/g/wg-rust",
                    "maturity": "working-group",
                    "oss": True,
                    "repositories": [
                      {
                        "url": "https://github.com/vfx-rs/organization",
                        "languages": { },
                        "primary": True
                      }
                    ],
                    "slack_url": "https://slack.aswf.io"
                  }
                ]
            )
        with tempfile.TemporaryDirectory() as tempdir:
            tmpfilepath = os.path.join(tempdir, 'someFileInTmpDir.csv')
            with unittest.mock.patch('argparse.ArgumentParser.parse_args') as mock:
                mock.return_value = argparse.Namespace(output=tmpfilepath)
                main()

                with open(tmpfilepath, 'r') as tmpfile:
                    self.maxDiff = None
                    self.assertEqual(tmpfile.read(),'Name,Level,Logo URL,Slug,Categories,Website,Chair,TAC Representative,Documentation,Calendar,Artwork,iCal,LFX Insights URL,Accepted Date,Last Review Date,Next Review Date,Slack URL,Chat Channel,Mailing List,Github Org,Best Practices Badge ID,Primary Github Repo,Contributed By\nASWF Language Interop Project,working-group,https://aswf.landscape2.io/logos/803e21319d55195829c27a3bc448d43e8f14dbcf544e4d44418299df3a3cca61.svg,aswf-language-interop-project,"ASWF Projects / All,Math and Simulation / Math Foundations",https://github.com/vfx-rs,Scott Wilson,,,https://zoom-lfx.platform.linuxfoundation.org/meetings/aswf-language-interop-project,https://artwork.aswf.io/projects/aswf-language-interop-project/,https://webcal.prod.itx.linuxfoundation.org/lfx/lfv8NMKI8tcp96N5tb,https://insights.lfx.linuxfoundation.org/foundation/aswf/overview?project=aswf-language-interop-project,2023-10-20,2024-03-20,2025-03-19,https://slack.aswf.io,#rust,https://lists.aswf.io/g/wg-rust,,,,\n')

if __name__ == '__main__':
    unittest.main()
