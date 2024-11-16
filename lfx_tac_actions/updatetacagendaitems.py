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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="filename to save output to",default='_data/tacmembers.csv')
    args = parser.parse_args()
    
    if os.environ.get("TAC_AGENDA_GH_PROJECT_URL") != '':
        urlparts = urlparse(os.environ.get("TAC_AGENDA_GH_PROJECT_URL")).path.split('/')
        if urlparts and urlparts[1] == 'orgs' and urlparts[3] == 'projects':
            command = subprocess.run("gh project item-list {gh_project_id} --owner {gh_org} --format json --limit 100".format(gh_project_id=urlparts[4],gh_org=urlparts[2]), shell=True, capture_output=True)
            jsonProjectData = command.stdout
            
            csvRows = []
            try:
                projectData = json.loads(jsonProjectData)
            except:
                print("Invalid response from gh client: '{}'".format(command.stderr))
                sys.exit(0)
            
            for item in projectData.get('items',[]):
                print("Processing {}...".format(item['content']['title']))
                meetingItem = {
                    'title': item.get('content',{}).get('title'),
                    'url': item.get('content',{}).get('url'),
                    'number': item.get('content',{}).get('number'),
                    'scheduled_date': item.get('scheduled Date'),
                    'status': item.get('status'),
                    'last_review_date': item.get('last Review Date'),
                    }
                if '1-new-project-wg' in item.get('labels',{}):
                    meetingItem['meeting_label'] = '1-new-project-wg'
                elif '2-annual-review' in item.get('labels',{}):
                    meetingItem['meeting_label'] = '2-annual-review'
                elif '2-annual-review-tac' in item.get('labels',{}):
                    meetingItem['meeting_label'] = '2-annual-review'
                elif '2-annual-review-sig' in item.get('labels',{}):
                    meetingItem['meeting_label'] = '2-annual-review-sig'
                elif '3-tac-meeting-long' in item.get('labels',{}):
                    meetingItem['meeting_label'] = '3-tac-meeting-long'
                elif '4-tac-meeting-short' in item.get('labels',{}):
                    meetingItem['meeting_label'] = '4-tac-meeting-short'
                else:
                    meetingItem['meeting_label'] = None
                csvRows.append(meetingItem)

            with open(args.output, 'w') as csvFileObject:
                print("Saving file {}".format(args.output))
                writer = csv.DictWriter(csvFileObject, fieldnames = csvRows[0].keys())
                writer.writeheader() 
                writer.writerows(csvRows)

if __name__ == '__main__':
    main()
