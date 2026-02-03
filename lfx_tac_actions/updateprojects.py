#!/usr/bin/env python3
#
# Copyright this project and its contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import csv
import requests
import json
import os
import argparse
import urllib.parse
import logging

def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="filename to save output to",default='_data/projects.csv')
    parser.add_argument('--log-level','-l',default='WARNING',help='Provide logging level. Example: --log-level DEBUG, default: WARNING')
    parser.add_argument("--landscape_url", help="URL to the project's landscape",required=True)
    args = parser.parse_args(args)
    
    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {args.log_level}')
    logging.basicConfig(level=numeric_level,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    landscape_hosted_projects = urllib.parse.urljoin(args.landscape_url,'api/projects/all.json')

    csv_rows = []
    try:
        hosted_projects_response = requests.get(landscape_hosted_projects)
        hosted_projects_response.raise_for_status()
        project_data = hosted_projects_response.json()
    except Exception as e:
        logging.critical(f"Error getting landscape_url {landscape_hosted_projects} - '{e}'")
        return
            
    for project in project_data:
        categories = []
        categories.append("{category} / {subcategory}".format(category=project.get('category'),subcategory=project.get('subcategory')))
        for additional_category in project.get('additional_categories',[]):
            categories.append("{category} / {subcategory}".format(category=additional_category['category'],subcategory=additional_category['subcategory']))
        repo_url = ''
        for repository in project.get('repositories',[]):
            if repository.get('primary'):
                repo_url = repository.get('url')

        logging.info("Processing {}".format(project.get('name')))
        csv_rows.append({
            'Name': project.get('name'),
            'Level': project.get('maturity'),
            'Logo URL': project.get('logo_url'),
            'Slug': project.get('annotations',{}).get('slug'),
            'Categories': ','.join(categories),
            'Website': project.get('homepage_url'),
            'Chair': project.get('annotations',{}).get('chair'),
            'TAC Representative': project.get('annotations',{}).get('TAC_representative'),
            'Documentation': project.get('extra',{}).get('documentation_url'),
            'Calendar': project.get('annotations',{}).get('calendar_url'),
            'Artwork': project.get('artwork_url'),
            'iCal': project.get('annotations',{}).get('ical_url'),
            'LFX Insights URL': project.get('devstats_url'),
            'Accepted Date': project.get('accepted_at'),
            'Last Review Date': project.get('latest_annual_review_at'),
            'Next Review Date': project.get('annotations',{}).get('next_annual_review_date'),
            'Slack URL': project.get('slack_url'),
            'Chat Channel': project.get('chat_channel'),
            'Mailing List': project.get('mailing_list_url'),
            'Github Org': project.get('annotations',{}).get('project_org'),
            'Best Practices Badge ID': project.get('bestPracticeBadgeId') ,
            'Primary Github Repo': repo_url,
            'Contributed By': project.get('annotations',{}).get('contributed_by'),
            })

    with open(args.output, 'w') as csv_file_object:
        logging.info("Saving file {}".format(args.output))
        writer = csv.DictWriter(csv_file_object, fieldnames = csv_rows[0].keys())
        writer.writeheader() 
        writer.writerows(csv_rows)

if __name__ == '__main__':
    main()
