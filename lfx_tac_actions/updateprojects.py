#!/usr/bin/env python3
#
# Copyright this project and its contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import csv
import urllib.request
import json
import os
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="filename to save output to",default='_data/projects.csv')
    args = parser.parse_args()
    
    if os.environ.get("LANDSCAPE_URL") != '':
        landscape_hosted_projects = '{}/api/projects/all.json'.format(os.environ["LANDSCAPE_URL"])

        csv_rows = []
        with urllib.request.urlopen(landscape_hosted_projects) as hosted_projects_response:
            project_data = json.load(hosted_projects_response)
            for project in project_data:
                categories = []
                categories.append("{category} / {subcategory}".format(category=project.get('category'),subcategory=project.get('subcategory')))
                for additional_category in project.get('additional_categories',{}):
                    categories.append("{category} / {subcategory}".format(category=additional_category['category'],subcategory=additional_category['subcategory']))
                print("Processing {}...".format(project.get('name')))
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
                    'LFX Insights URL': project.get('dev_stats_url'),
                    'Accepted Date': project.get('accepted_at'),
                    'Last Review Date': project.get('extra',{}).get('annual_review_date'),
                    'Next Review Date': project.get('annotations',{}).get('next_annual_review_date'),
                    'Slack URL': project.get('slack_url'),
                    'Chat Channel': project.get('chat_channel'),
                    'Mailing List': project.get('mailing_list_url'),
                    'Github Org': project.get('annotations',{}).get('project_org'),
                    'Best Practices Badge ID': project.get('bestPracticeBadgeId') ,
                    'Primary Github Repo': project.get('repo_url'),
                    'Contributed By': project.get('annotations',{}).get('contributed_by'),
                    })

        with open(args.output, 'w') as csv_file_object:
            print("Saving file {}".format(args.output))
            writer = csv.DictWriter(csv_file_object, fieldnames = csv_rows[0].keys())
            writer.writeheader() 
            writer.writerows(csv_rows)

if __name__ == '__main__':
    main()
