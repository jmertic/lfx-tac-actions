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

def main():
    if "LANDSCAPE_URL" in os.environ and os.environ["LANDSCAPE_URL"] != '':
        projectsCsvFile = '_data/projects.csv'
        landscapeBaseURL = os.environ["LANDSCAPE_URL"] 
        landscapeHostedProjects = '{}/api/projects/all.json'.format(landscapeBaseURL)

        csvRows = []

        with urllib.request.urlopen(landscapeHostedProjects) as hostedProjectsResponse:
            projectData = json.load(hostedProjectsResponse)
            for project in projectData:
                categories = []
                categories.append("{category} / {subcategory}".format(category=project.get('category'),subcategory=project.get('subcategory')))
                for additional_category in project.get('additional_categories',{}):
                    categories.append("{category} / {subcategory}".format(category=additional_category['category'],subcategory=additional_category['subcategory']))
                print("Processing {}...".format(project.get('name')))
                csvRows.append({
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

        with open(projectsCsvFile, 'w') as projectsCsvFileObject:
            writer = csv.DictWriter(projectsCsvFileObject, fieldnames = csvRows[0].keys())
            writer.writeheader() 
            writer.writerows(csvRows)

if __name__ == '__main__':
    main()
