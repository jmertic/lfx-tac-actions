#!/usr/bin/env python3
#
# Copyright this project and its contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import argparse
import csv
import requests
import json
import os
from urllib.parse import urlparse
import logging
from pathlib import Path
import re
import sys

from pathvalidate.argparse import validate_filepath_arg

from . import setup_logging

def main(args=None):
    parser = argparse.ArgumentParser(description="Pulls the current list of TAC members from LFX PCC and streams CSV format to `stdout`.")
    parser.add_argument('--log-level','-l',default='WARNING',help='Provide logging level. Example: --log-level DEBUG, default: WARNING')
    parser.add_argument("--lfx_tac_committee_url", help="URL to the TAC Committee in LFX PCC", required=True)
    args = parser.parse_args(args)

    setup_logging(args.log_level)

    committee_url = 'https://api-gw.platform.linuxfoundation.org/project-service/v2/public/projects/{project_id}/committees/{committee_id}/members'

    pattern = r'^https://projectadmin\.lfx\.linuxfoundation\.org/project/(?P<project_id>[^/]+)/collaboration/committees/(?P<committee_id>[^/?#]+)$'
    match = re.search(pattern, args.lfx_tac_committee_url)
    if not match:
        logging.critical(f"Invalid value for lfx_tac_committee_url - {args.lfx_tac_committee_url}")
        return

    csv_rows = []
    try:
        committee_url_response = requests.get(committee_url.format(project_id=match.group('project_id'),committee_id=match.group('committee_id')))
        committee_url_response.raise_for_status()
        committee_url_response_json = committee_url_response.json()
    except Exception as e:
        logging.critical(f"Error getting {committee_url.format(project_id=match.group('project_id'),committee_id=match.group('committee_id'))} - {e}")
        return

    for committee_member in committee_url_response_json.get('Data',[]):
        logging.info("Processing {} {}".format(committee_member.get('FirstName').title(),committee_member.get('LastName').title()))
        csv_rows.append({
            'Full Name': "{} {}".format(committee_member.get('FirstName').title(),committee_member.get('LastName').title()),
            'Account Name: Account Name': committee_member.get('Organization',{}).get('Name'),
            'Appointed By': committee_member.get('AppointedBy'),
            'Voting Status': committee_member.get('VotingStatus'),
            'Special Role': committee_member.get('Role'),
            'Title': committee_member.get('Title'),
            'HeadshotURL': committee_member.get('LogoURL')
            })

    if not csv_rows:
        logging.warning("No valid data retrieved.")
        return

    writer = csv.DictWriter(sys.stdout, fieldnames = csv_rows[0].keys())
    writer.writeheader()
    writer.writerows(csv_rows)

if __name__ == '__main__':
    main()
