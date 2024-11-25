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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="filename to save output to",default='_data/tacmembers.csv')
    args = parser.parse_args()

    if os.environ.get("LFX_TAC_COMMITTEE_URL") != '':
        urlparts = urlparse(os.environ.get("LFX_TAC_COMMITTEE_URL")).path.split('/')
        if urlparts and urlparts[1] == 'project' and urlparts[3] == 'collaboration' and urlparts[4] == 'committees':
            committee_url = 'https://api-gw.platform.linuxfoundation.org/project-service/v2/public/projects/{project_id}/committees/{committee_id}/members'.format(project_id=urlparts[2],committee_id=urlparts[5])
            csv_rows = []

            with requests.get(committee_url) as committee_url_response:
                committee_url_response_json = committee_url_response.json()
                for committee_member in committee_url_response_json.get('Data',[]):
                    print("Processing {} {}...".format(committee_member.get('FirstName').title(),committee_member.get('LastName').title()))
                    csv_rows.append({
                        'Full Name': "{} {}".format(committee_member.get('FirstName').title(),committee_member.get('LastName').title()),
                        'Account Name: Account Name': committee_member.get('Organization',{}).get('Name'),
                        'Appointed By': committee_member.get('AppointedBy'),
                        'Voting Status': committee_member.get('VotingStatus'),
                        'Special Role': committee_member.get('Role'),
                        'Title': committee_member.get('Title'),
                        'HeadshotURL': committee_member.get('LogoURL')
                        })

            with open(args.output, 'w') as csv_file_object:
                print("Saving file {}".format(args.output))
                writer = csv.DictWriter(csv_file_object, fieldnames = csv_rows[0].keys())
                writer.writeheader() 
                writer.writerows(csv_rows)

if __name__ == '__main__':
    main()
