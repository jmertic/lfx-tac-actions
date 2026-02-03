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

def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="filename to save output to",default='_data/tacmembers.csv')
    parser.add_argument('--log-level','-l',default='WARNING',help='Provide logging level. Example: --log-level DEBUG, default: WARNING')
    parser.add_argument("--lfx_tac_committee_url", help="URL to the TAC Committee in LFX PCC", required=True)
    args = parser.parse_args(args)

    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {args.log_level}')
    logging.basicConfig(level=numeric_level,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    committee_url = 'https://api-gw.platform.linuxfoundation.org/project-service/v2/public/projects/{project_id}/committees/{committee_id}/members'
    
    urlparts = urlparse(args.lfx_tac_committee_url).path.split('/')
    if not urlparts or len(urlparts) < 5 or urlparts[1] != 'project' or urlparts[3] != 'collaboration' or urlparts[4] != 'committees':
        logging.critical(f"Invalid value for lfx_tac_committee_url - {args.lfx_tac_committee_url}")
        return
    
    csv_rows = []
    try:
        committee_url_response = requests.get(committee_url.format(project_id=urlparts[2],committee_id=urlparts[5]))
        committee_url_response.raise_for_status()
        committee_url_response_json = committee_url_response.json()
    except Exception as e:
        logging.critical(f"Error getting {committee_url_response.url} - {e}")
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

    with open(args.output, 'w') as csv_file_object:
        logging.info("Saving file {}".format(args.output))
        writer = csv.DictWriter(csv_file_object, fieldnames = csv_rows[0].keys())
        writer.writeheader() 
        writer.writerows(csv_rows)

if __name__ == '__main__':
    main()
