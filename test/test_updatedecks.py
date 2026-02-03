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
import re

from lfx_tac_actions.updatedecks import main

class TestUpdateDecks(unittest.TestCase):
    
    def testMainNoArgs(self):
        with self.assertRaises(SystemExit) as cm:
            main(["-o",""])
        self.assertEqual(cm.exception.code, 2)
    
    def testBadLogLevel(self):
        with self.assertRaises(ValueError) as cm:
            main(["-l","BAD","--overview_decks","foo"])
        self.assertIn('Invalid log level: BAD', str(cm.exception))

    @responses.activate
    def testMain(self):
        overview_decks = '[{"url": "https://docs.google.com/presentation/d/1V7fDPMvDR5rkAjx5f74vyMpkY_tp1hVq/edit?usp=sharing&ouid=108330571292091021915&rtpof=true&sd=true","filename": "ASWF High Level Overview"},{"url":"https://docs.google.com/presentation/d/1DymqK796EhxkLIchx7sNxJloovYLGJD8UDkOdkS42to/edit?usp=sharing","filename": "ASWF Governing Board Overview"},{"url":"https://docs.google.com/presentation/d/1qY9DPLw4aucqIdqqB1_Pi-qKEyIg2V7q9B96-G1jhqE/edit?usp=sharing","filename": "ASWF TAC Overview"},{"url":"https://docs.google.com/presentation/d/1p0FoFJ7-IdDejisJPUYdq_uApn3XW3wJ/edit?usp=sharing&ouid=108330571292091021915&rtpof=true&sd=true","filename":"ASWF Membership Overview"},{"url":"http://badurl.com/badfile","filename":"Bad File"}]'

        responses.get(
            url=re.compile(r'^https://docs\.google\.com/feeds/download/presentations/Export\?id=1V7fDPMvDR5rkAjx5f74vyMpkY_tp1hVq&exportFormat=.*$'),
            body="blah blah blah")
        responses.get(
            url=re.compile(r'^https://docs\.google\.com/feeds/download/presentations/Export\?id=1DymqK796EhxkLIchx7sNxJloovYLGJD8UDkOdkS42to&exportFormat=.*$'),
            body="blah blah blah")
        responses.get(
            url=re.compile(r'^https://docs\.google\.com/feeds/download/presentations/Export\?id=1qY9DPLw4aucqIdqqB1_Pi-qKEyIg2V7q9B96-G1jhqE&exportFormat=.*$'),
            body="blah blah blah")
        responses.get(
            url=re.compile(r'^https://docs\.google\.com/feeds/download/presentations/Export\?id=1p0FoFJ7-IdDejisJPUYdq_uApn3XW3wJ&exportFormat=.*$'),
            status=404,
            body="Not here!"
            )
        
        with tempfile.TemporaryDirectory() as tempdir:
            with self.assertLogs(level="ERROR") as cm:
                main(["-o",tempdir,"--overview_decks",overview_decks])
            
            self.assertIn("Error getting overview deck https://docs.google.com/presentation/d/1p0FoFJ7-IdDejisJPUYdq_uApn3XW3wJ/edit?usp=sharing&ouid=108330571292091021915&rtpof=true&sd=true - 404 Client Error: Not Found for url: https://docs.google.com/feeds/download/presentations/Export?id=1p0FoFJ7-IdDejisJPUYdq_uApn3XW3wJ&exportFormat=pdf", str(cm.output[0]))
            self.assertTrue(os.path.isfile(Path(tempdir,"ASWF High Level Overview.pdf")))
            self.assertTrue(os.path.isfile(Path(tempdir,"ASWF Governing Board Overview.pdf")))
            self.assertTrue(os.path.isfile(Path(tempdir,"ASWF TAC Overview.pdf")))
            self.assertFalse(os.path.isfile(Path(tempdir,"ASWF Membership Overview.pdf")))
            self.assertTrue(os.path.isfile(Path(tempdir,"ASWF High Level Overview.pptx")))
            self.assertTrue(os.path.isfile(Path(tempdir,"ASWF Governing Board Overview.pptx")))
            self.assertTrue(os.path.isfile(Path(tempdir,"ASWF TAC Overview.pptx")))
            self.assertFalse(os.path.isfile(Path(tempdir,"ASWF Membership Overview.pptx")))
            self.assertFalse(os.path.isfile(Path(tempdir,"Bad File.pdf")))
            self.assertFalse(os.path.isfile(Path(tempdir,"Bad File.pptx")))

if __name__ == '__main__':
    unittest.main()
