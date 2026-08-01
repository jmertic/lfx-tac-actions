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
import urllib.parse
import logging
from pathlib import Path
import sys

from . import setup_logging, setup_argparse, get_landscape_endpoint

def main(args=None):
    parser = setup_argparse(description="Pulls hosted project data from a project's landscape and streams in CSV format to `stdout`.")
    parser.add_argument("--landscape_url", help="URL to the project's landscape",required=True)
    args = parser.parse_args(args)

    setup_logging(args.log_level)

    csv_rows = []

    try:
        landscape_hosted_projects = get_landscape_endpoint(args.landscape_url)
        hosted_projects_response = requests.get(landscape_hosted_projects)
        hosted_projects_response.raise_for_status()
        project_data = hosted_projects_response.json()
    except Exception as e:
        logging.critical(f"Error getting landscape_url {args.landscape_url} - '{e}'")
        return

    for project in project_data:
        categories = []
        categories.append("{category} / {subcategory}".format(category=project.get('category'),subcategory=project.get('subcategory')))
        for additional_category in project.get('additional_categories',[]):
            categories.append("{category} / {subcategory}".format(category=additional_category['category'],subcategory=additional_category['subcategory']))
        other_links_lookup = {d['name']: d['url'] for d in project.get('other_links',[])}

        logging.info("Processing {}".format(project.get('name')))
        csv_rows.append({
            'Name': project.get('name'),
            'Level': project.get('maturity'),
            'Logo URL': project.get('logo_url'),
            'Slug': project.get('annotations',{}).get('slug',project.get('lfx_slug')),
            'Categories': ','.join(categories),
            'Website': project.get('homepage_url'),
            'Chair': project.get('annotations',{}).get('chair'),
            'TAC Representative': project.get('annotations',{}).get('TAC_representative'),
            'Documentation': project.get('extra',{}).get('documentation_url'),
            'Calendar': other_links_lookup.get('Calendar'),
            'Artwork': project.get('artwork_url'),
            'iCal': other_links_lookup.get('iCal'),
            'LFX Insights URL': project.get('devstats_url'),
            'Accepted Date': project.get('accepted_at'),
            'Last Review Date': project.get('latest_annual_review_at'),
            'Next Review Date': project.get('annotations',{}).get('next_annual_review_date'),
            'Slack URL': project.get('slack_url'),
            'Chat Channel': project.get('chat_channel'),
            'Mailing List': project.get('mailing_list_url'),
            'Github Org': project.get('annotations',{}).get('project_org'),
            'Best Practices Badge ID': project.get('bestPracticeBadgeId') ,
            'Primary Github Repo': next((d['url'] for d in project.get('repositories',[]) if d['primary']), None),
            'Contributed By': project.get('annotations',{}).get('contributed_by'),
            })

    if not csv_rows:
        logging.warning("No valid data retrieved.")
        return

    writer = csv.DictWriter(sys.stdout, fieldnames = csv_rows[0].keys())
    writer.writeheader()
    writer.writerows(csv_rows)

if __name__ == '__main__':
    main()
