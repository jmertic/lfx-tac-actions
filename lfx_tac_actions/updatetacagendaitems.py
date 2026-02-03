#!/usr/bin/env python3
#
# Copyright this project and its contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import sys
import csv
import json
import os
import subprocess
from urllib.parse import urlparse
import argparse
import logging

def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="filename to save output to",default='_data/tacmembers.csv')
    parser.add_argument('--log-level','-l',default='WARNING',help='Provide logging level. Example: --log-level DEBUG, default: WARNING')
    parser.add_argument("--tac_agenda_gh_project_url", help="URL to the TAC agenda GitHub Project",required=True)
    args = parser.parse_args(args)
    
    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {args.log_level}')
    logging.basicConfig(level=numeric_level,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    urlparts = urlparse(args.tac_agenda_gh_project_url).path.split('/')
    if not urlparts or len(urlparts) < 5 or urlparts[1] != 'orgs' or urlparts[3] != 'projects':
        logging.critical(f"Invalid value for tac_agenda_gh_project_url - {args.tac_agenda_gh_project_url}")
        return

    csv_rows = []
    try:
        command = subprocess.run("gh project item-list {gh_project_id} --owner {gh_org} --format json --limit 100".format(gh_project_id=urlparts[4],gh_org=urlparts[2]), shell=True, capture_output=True)
        json_project_data = command.stdout
        project_data = json.loads(json_project_data)
    except ValueError:
        logging.error(f"Invalid response from gh client: {command.stderr}")
        return
    
    for item in project_data.get('items',[]):
        logging.info("Processing {item['content']['title']}")
        meeting_item = {
            'title': item.get('content',{}).get('title'),
            'url': item.get('content',{}).get('url'),
            'number': item.get('content',{}).get('number'),
            'scheduled_date': item.get('scheduled Date'),
            'status': item.get('status'),
            'last_review_date': item.get('last Review Date'),
            }
        if '1-new-project-wg' in item.get('labels',{}):
            meeting_item['meeting_label'] = '1-new-project-wg'
        elif '2-annual-review' in item.get('labels',{}):
            meeting_item['meeting_label'] = '2-annual-review'
        elif '2-annual-review-tac' in item.get('labels',{}):
            meeting_item['meeting_label'] = '2-annual-review'
        elif '2-annual-review-sig' in item.get('labels',{}):
            meeting_item['meeting_label'] = '2-annual-review-sig'
        elif '3-tac-meeting-long' in item.get('labels',{}):
            meeting_item['meeting_label'] = '3-tac-meeting-long'
        elif '4-tac-meeting-short' in item.get('labels',{}):
            meeting_item['meeting_label'] = '4-tac-meeting-short'
        else:
            meeting_item['meeting_label'] = None
        csv_rows.append(meeting_item)

    with open(args.output, 'w') as csv_file_object:
        logging.info(f"Saving file {args.output}")
        writer = csv.DictWriter(csv_file_object, fieldnames = csv_rows[0].keys())
        writer.writeheader() 
        writer.writerows(csv_rows)

if __name__ == '__main__':
    main()
