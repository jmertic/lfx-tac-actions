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

from lfx_tac_actions.updateclomonitor import main

class TestUpdateCLOMonitor(unittest.TestCase):
    
    def testMainNoLandscapeUrl(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmpfilepath = os.path.join(tempdir, 'someFileInTmpDir.yaml')
            main(["-o",tmpfilepath,"--landscape_url",""])
        
        self.assertLogs("Error getting landscape_url api/projects/all.json - error message 'Invalid URL 'api/projects/all.json': No scheme supplied. Perhaps you meant https://api/projects/all.json?", level='CRITICAL')
    
    def testBadLogLevel(self):
        with self.assertRaises(ValueError) as cm:
            main(["-l","BAD","--landscape_url","foo"])
        self.assertIn('Invalid log level: BAD', str(cm.exception))

    @responses.activate
    def testMainEmeritusProject(self):
        responses.add(
            method=responses.GET,
            url="https://landscape.aswf.io/api/projects/all.json",
            json=[
                {
                    "category": "ASWF Projects",
                    "homepage_url": "https://opencolorio.org/",
                    "id": "aswf-projects--all--opencolorio",
                    "logo_url": "https://aswf.landscape2.io/logos/2d4849a9c8ebf6d6e9e1096d191e88739c4abd47754620e7a1c5244ebe14aa05.svg",
                    "name": "OpenColorIO",
                    "subcategory": "All",
                    "accepted_at": "2020-04-24",
                    "additional_categories": [
                      {
                        "category": "Imaging and Color",
                        "subcategory": "Color Science"
                      },
                      {
                        "category": "Dev Days 2024",
                        "subcategory": "Participating Project"
                      }
                    ],
                    "annotations": {
                      "ical_url": "https://webcal.prod.itx.linuxfoundation.org/lfx/a092M00001If9v8QAB",
                      "chair": "Carol Payne",
                      "calendar_url": "https://zoom-lfx.platform.linuxfoundation.org/meetings/opencolorio",
                      "next_annual_review_date": "2025-01-22"
                    },
                    "country": "United States",
                    "crunchbase_url": "https://www.crunchbase.com/organization/academy-software-foundation",
                    "description": "The OpenColorIO project is committed to providing an industry standard solution for highly precise, performant, and consistent color management across digital content creation applications and pipelines.",
                    "devstats_url": "https://insights.lfx.linuxfoundation.org/foundation/aswf/overview?project=opencolorio",
                    "latest_annual_review_at": "2023-11-01",
                    "latest_annual_review_url": "https://github.com/AcademySoftwareFoundation/tac/issues/474",
                    "lfx_slug": "opencolorio",
                    "mailing_list_url": "https://lists.aswf.io/g/ocio-user",
                    "maturity": "emeritus",
                    "oss": True,
                    "repositories": [
                      {
                        "url": "https://github.com/AcademySoftwareFoundation/OpenColorIO",
                        "languages": {
                          "Batchfile": 26254,
                          "C": 61491,
                          "C++": 8288679,
                          "CMake": 286452,
                          "Java": 73341,
                          "Objective-C": 6826,
                          "Objective-C++": 37712,
                          "Python": 1268733,
                          "Roff": 867637,
                          "Shell": 19585
                        },
                        "primary": True
                      },
                      {
                        "url": "https://github.com/AcademySoftwareFoundation/OpenColorIO-Config-ACES",
                        "languages": {
                          "Dockerfile": 1814,
                          "Python": 391928
                        },
                        "primary": False
                      }
                    ],
                    "slack_url": "https://slack.opencolorio.org"
                }
                ]
            )
        with tempfile.TemporaryDirectory() as tempdir:
            tmpfilepath = os.path.join(tempdir, 'someFileInTmpDir.yaml')
            main(["-o",tmpfilepath,"--landscape_url","https://landscape.aswf.io"])

            with open(tmpfilepath, 'r') as tmpfile:
                self.maxDiff = None
                self.assertEqual(tmpfile.read(),'''[]\n''')
    
    @responses.activate
    def testMainInvalidArtworkUrl(self):
        responses.add(
            method=responses.GET,
            url="https://artwork.aswf.io/assets/data.json",
            status=404,
            body="Not here!"
            )
        responses.add(
            method=responses.GET,
            url="https://landscape.aswf.io/api/projects/all.json",
            json=[
                {
                    "category": "ASWF Projects",
                    "homepage_url": "https://opencolorio.org/",
                    "id": "aswf-projects--all--opencolorio",
                    "logo_url": "https://aswf.landscape2.io/logos/2d4849a9c8ebf6d6e9e1096d191e88739c4abd47754620e7a1c5244ebe14aa05.svg",
                    "name": "OpenColorIO",
                    "subcategory": "All",
                    "accepted_at": "2020-04-24",
                    "additional_categories": [
                      {
                        "category": "Imaging and Color",
                        "subcategory": "Color Science"
                      },
                      {
                        "category": "Dev Days 2024",
                        "subcategory": "Participating Project"
                      }
                    ],
                    "annotations": {
                      "ical_url": "https://webcal.prod.itx.linuxfoundation.org/lfx/a092M00001If9v8QAB",
                      "slug": "opencolorio",
                      "chair": "Carol Payne",
                      "calendar_url": "https://zoom-lfx.platform.linuxfoundation.org/meetings/opencolorio",
                      "next_annual_review_date": "2025-01-22"
                    },
                    "country": "United States",
                    "crunchbase_url": "https://www.crunchbase.com/organization/academy-software-foundation",
                    "artwork_url": "https://artwork.aswf.io/projects/opencolorio/",
                    "description": "The OpenColorIO project is committed to providing an industry standard solution for highly precise, performant, and consistent color management across digital content creation applications and pipelines.",
                    "devstats_url": "https://insights.lfx.linuxfoundation.org/foundation/aswf/overview?project=opencolorio",
                    "latest_annual_review_at": "2023-11-01",
                    "latest_annual_review_url": "https://github.com/AcademySoftwareFoundation/tac/issues/474",
                    "mailing_list_url": "https://lists.aswf.io/g/ocio-user",
                    "maturity": "adopted",
                    "oss": True,
                    "repositories": [
                      {
                        "url": "https://github.com/AcademySoftwareFoundation/OpenColorIO",
                        "languages": {
                          "Batchfile": 26254,
                          "C": 61491,
                          "C++": 8288679,
                          "CMake": 286452,
                          "Java": 73341,
                          "Objective-C": 6826,
                          "Objective-C++": 37712,
                          "Python": 1268733,
                          "Roff": 867637,
                          "Shell": 19585
                        },
                        "primary": True
                      },
                      {
                        "url": "https://github.com/AcademySoftwareFoundation/OpenColorIO-Config-ACES",
                        "languages": {
                          "Dockerfile": 1814,
                          "Python": 391928
                        },
                        "primary": False
                      }
                    ],
                    "slack_url": "https://slack.opencolorio.org"
                }
                ]
            )
        with tempfile.TemporaryDirectory() as tempdir:
            tmpfilepath = os.path.join(tempdir, 'someFileInTmpDir.yaml')
            with self.assertLogs(level="ERROR") as cm:
                main(["-o",tmpfilepath,"--landscape_url","https://landscape.aswf.io"])
            self.assertIn("Error getting artwork repo file https://artwork.aswf.io/assets/data.json - error message '404 Client Error: Not Found for url: https://artwork.aswf.io/assets/data.json", str(cm.output[0]))

            with open(tmpfilepath, 'r') as tmpfile:
                self.maxDiff = None
                self.assertEqual(tmpfile.read(),'''- name: opencolorio
  display_name: OpenColorIO
  description: The OpenColorIO project is committed to providing an industry standard
    solution for highly precise, performant, and consistent color management across
    digital content creation applications and pipelines.
  category: Visual Effects and Computer Graphics
  logo_url: https://aswf.landscape2.io/logos/2d4849a9c8ebf6d6e9e1096d191e88739c4abd47754620e7a1c5244ebe14aa05.svg
  logo_url_dark: https://aswf.landscape2.io/logos/2d4849a9c8ebf6d6e9e1096d191e88739c4abd47754620e7a1c5244ebe14aa05.svg
  devstats_url: null
  maturity: adopted
  repositories:
  - name: OpenColorIO
    url: https://github.com/AcademySoftwareFoundation/OpenColorIO
    exclude:
    - clomonitor
  - name: OpenColorIO-Config-ACES
    url: https://github.com/AcademySoftwareFoundation/OpenColorIO-Config-ACES
    exclude:
    - clomonitor
''')

    @responses.activate
    def testMainNoArtworkUrl(self):
        responses.add(
            method=responses.GET,
            url="https://landscape.aswf.io/api/projects/all.json",
            json=[
                {
                    "category": "ASWF Projects",
                    "homepage_url": "https://opencolorio.org/",
                    "id": "aswf-projects--all--opencolorio",
                    "logo_url": "https://aswf.landscape2.io/logos/2d4849a9c8ebf6d6e9e1096d191e88739c4abd47754620e7a1c5244ebe14aa05.svg",
                    "name": "OpenColorIO",
                    "subcategory": "All",
                    "accepted_at": "2020-04-24",
                    "additional_categories": [
                      {
                        "category": "Imaging and Color",
                        "subcategory": "Color Science"
                      },
                      {
                        "category": "Dev Days 2024",
                        "subcategory": "Participating Project"
                      }
                    ],
                    "annotations": {
                      "ical_url": "https://webcal.prod.itx.linuxfoundation.org/lfx/a092M00001If9v8QAB",
                      "slug": "opencolorio",
                      "chair": "Carol Payne",
                      "calendar_url": "https://zoom-lfx.platform.linuxfoundation.org/meetings/opencolorio",
                      "next_annual_review_date": "2025-01-22"
                    },
                    "country": "United States",
                    "crunchbase_url": "https://www.crunchbase.com/organization/academy-software-foundation",
                    "description": "The OpenColorIO project is committed to providing an industry standard solution for highly precise, performant, and consistent color management across digital content creation applications and pipelines.",
                    "devstats_url": "https://insights.lfx.linuxfoundation.org/foundation/aswf/overview?project=opencolorio",
                    "latest_annual_review_at": "2023-11-01",
                    "latest_annual_review_url": "https://github.com/AcademySoftwareFoundation/tac/issues/474",
                    "mailing_list_url": "https://lists.aswf.io/g/ocio-user",
                    "maturity": "adopted",
                    "oss": True,
                    "repositories": [
                      {
                        "url": "https://github.com/AcademySoftwareFoundation/OpenColorIO",
                        "languages": {
                          "Batchfile": 26254,
                          "C": 61491,
                          "C++": 8288679,
                          "CMake": 286452,
                          "Java": 73341,
                          "Objective-C": 6826,
                          "Objective-C++": 37712,
                          "Python": 1268733,
                          "Roff": 867637,
                          "Shell": 19585
                        },
                        "primary": True
                      },
                      {
                        "url": "https://github.com/AcademySoftwareFoundation/OpenColorIO-Config-ACES",
                        "languages": {
                          "Dockerfile": 1814,
                          "Python": 391928
                        },
                        "primary": False
                      }
                    ],
                    "slack_url": "https://slack.opencolorio.org"
                }
                ]
            )
        with tempfile.TemporaryDirectory() as tempdir:
            tmpfilepath = os.path.join(tempdir, 'someFileInTmpDir.yaml')
            main(["-o",tmpfilepath,"--landscape_url","https://landscape.aswf.io"])

            with open(tmpfilepath, 'r') as tmpfile:
                self.maxDiff = None
                self.assertEqual(tmpfile.read(),'''- name: opencolorio
  display_name: OpenColorIO
  description: The OpenColorIO project is committed to providing an industry standard
    solution for highly precise, performant, and consistent color management across
    digital content creation applications and pipelines.
  category: Visual Effects and Computer Graphics
  logo_url: https://aswf.landscape2.io/logos/2d4849a9c8ebf6d6e9e1096d191e88739c4abd47754620e7a1c5244ebe14aa05.svg
  logo_url_dark: https://aswf.landscape2.io/logos/2d4849a9c8ebf6d6e9e1096d191e88739c4abd47754620e7a1c5244ebe14aa05.svg
  devstats_url: null
  maturity: adopted
  repositories:
  - name: OpenColorIO
    url: https://github.com/AcademySoftwareFoundation/OpenColorIO
    exclude:
    - clomonitor
  - name: OpenColorIO-Config-ACES
    url: https://github.com/AcademySoftwareFoundation/OpenColorIO-Config-ACES
    exclude:
    - clomonitor
''')

    @responses.activate
    def testMain(self):
        responses.add(
            method=responses.GET,
            url="https://artwork.aswf.io/assets/data.json",
            json={
                    "/projects/opencolorio/": {
                        "name": "OpenColorIO",
                        "category": "Adopted Projects",
                        "primary_logo": "stacked/color/opencolorio-stacked-color.svg",
                        "dark_logo": "stacked/color/opencolorio-stacked-color.svg",
                        }
                })
        responses.add(
            method=responses.GET,
            url="https://landscape.aswf.io/api/projects/all.json",
            json=[
                {
                    "name": "Project Not to Add",
                },
                {
                    "category": "ASWF Projects",
                    "homepage_url": "https://opencolorio.org/",
                    "id": "aswf-projects--all--opencolorio",
                    "logo_url": "https://aswf.landscape2.io/logos/2d4849a9c8ebf6d6e9e1096d191e88739c4abd47754620e7a1c5244ebe14aa05.svg",
                    "name": "OpenColorIO",
                    "subcategory": "All",
                    "accepted_at": "2020-04-24",
                    "additional_categories": [
                      {
                        "category": "Imaging and Color",
                        "subcategory": "Color Science"
                      },
                      {
                        "category": "Dev Days 2024",
                        "subcategory": "Participating Project"
                      }
                    ],
                    "annotations": {
                      "ical_url": "https://webcal.prod.itx.linuxfoundation.org/lfx/a092M00001If9v8QAB",
                      "slug": "opencolorio",
                      "chair": "Carol Payne",
                      "calendar_url": "https://zoom-lfx.platform.linuxfoundation.org/meetings/opencolorio",
                      "next_annual_review_date": "2025-01-22"
                    },
                    "artwork_url": "https://artwork.aswf.io/projects/opencolorio/",
                    "country": "United States",
                    "crunchbase_url": "https://www.crunchbase.com/organization/academy-software-foundation",
                    "description": "The OpenColorIO project is committed to providing an industry standard solution for highly precise, performant, and consistent color management across digital content creation applications and pipelines.",
                    "devstats_url": "https://insights.lfx.linuxfoundation.org/foundation/aswf/overview?project=opencolorio",
                    "latest_annual_review_at": "2023-11-01",
                    "latest_annual_review_url": "https://github.com/AcademySoftwareFoundation/tac/issues/474",
                    "mailing_list_url": "https://lists.aswf.io/g/ocio-user",
                    "maturity": "adopted",
                    "oss": True,
                    "repositories": [
                      {
                        "url": "https://github.com/AcademySoftwareFoundation/OpenColorIO",
                        "languages": {
                          "Batchfile": 26254,
                          "C": 61491,
                          "C++": 8288679,
                          "CMake": 286452,
                          "Java": 73341,
                          "Objective-C": 6826,
                          "Objective-C++": 37712,
                          "Python": 1268733,
                          "Roff": 867637,
                          "Shell": 19585
                        },
                        "primary": True
                      },
                      {
                        "url": "https://github.com/AcademySoftwareFoundation/OpenColorIO-Config-ACES",
                        "languages": {
                          "Dockerfile": 1814,
                          "Python": 391928
                        },
                        "primary": False
                      }
                    ],
                    "slack_url": "https://slack.opencolorio.org"
                }
                ]
            )
        with tempfile.TemporaryDirectory() as tempdir:
            tmpfilepath = os.path.join(tempdir, 'someFileInTmpDir.yaml')
            main(["-o",tmpfilepath,"--landscape_url","https://landscape.aswf.io"])

            with open(tmpfilepath, 'r') as tmpfile:
                self.maxDiff = None
                self.assertEqual(tmpfile.read(),'''- name: opencolorio
  display_name: OpenColorIO
  description: The OpenColorIO project is committed to providing an industry standard
    solution for highly precise, performant, and consistent color management across
    digital content creation applications and pipelines.
  category: Visual Effects and Computer Graphics
  logo_url: https://artwork.aswf.io/projects/opencolorio/stacked/color/opencolorio-stacked-color.svg
  logo_url_dark: https://artwork.aswf.io/projects/opencolorio/stacked/color/opencolorio-stacked-color.svg
  devstats_url: null
  maturity: adopted
  repositories:
  - name: OpenColorIO
    url: https://github.com/AcademySoftwareFoundation/OpenColorIO
    exclude:
    - clomonitor
  - name: OpenColorIO-Config-ACES
    url: https://github.com/AcademySoftwareFoundation/OpenColorIO-Config-ACES
    exclude:
    - clomonitor
''')

if __name__ == '__main__':
    unittest.main()
