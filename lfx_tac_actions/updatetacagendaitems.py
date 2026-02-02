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

def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="filename to save output to",default='_data/tacmembers.csv')
    parser.add_argument("--tac_agenda_gh_project_url", help="URL to the TAC agenda GitHub Project",required=True)
    args = parser.parse_args(args)
    
    urlparts = urlparse(args.tac_agenda_gh_project_url).path.split('/')
    if urlparts and len(urlparts) >= 4 and urlparts[1] == 'orgs' and urlparts[3] == 'projects':
        command = subprocess.run("gh project item-list {gh_project_id} --owner {gh_org} --format json --limit 100".format(gh_project_id=urlparts[4],gh_org=urlparts[2]), shell=True, capture_output=True)
        json_project_data = command.stdout
        
        csv_rows = []
        try:
            project_data = json.loads(json_project_data)
        except ValueError:
            print("Invalid response from gh client: '{}'".format(command.stderr))
            return
        
        for item in project_data.get('items',[]):
            print("Processing {}...".format(item['content']['title']))
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
            print("Saving file {}".format(args.output))
            writer = csv.DictWriter(csv_file_object, fieldnames = csv_rows[0].keys())
            writer.writeheader() 
            writer.writerows(csv_rows)

if __name__ == '__main__':
    main()
