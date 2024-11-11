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

if "LANDSCAPE_URL" in os.environ and os.environ["LANDSCAPE_URL"] != '':
    projectsCsvFile = '_data/projects.csv'
    landscapeBaseURL = os.environ["LANDSCAPE_URL"] 
    landscapeHostedProjects = '{}/api/projects/all.json'.format(landscapeBaseURL)

    csvRows = []

    with urllib.request.urlopen(landscapeHostedProjects) as hostedProjectsResponse:
        projectData = json.load(hostedProjectsResponse)
        categories = []
        categories.append("{category} / {subcategory}".format(category=projectData.get('category'),subcategory=projectData.get('subcategory'))
        if 'additional_categories' in projectData:
            for additional_category in projectData.get('additional_categories'):
                categories.append("{category} / {subcategory}".format(category=additional_category['category'],subcategory=additional_category['subcategory'])
        print("Processing {}...".format(projectData.get('name')))
        csvRows.append({
            'Name': projectData.get('name'),
            'Level': projectData.get('maturity'),
            'Logo URL': project.get('logo_url'),
            'Slug': projectData.get('annotations',{}).get('slug'),
            'Categories': ','.join(categories),
            'Website': projectData.get('homepage_url'),
            'Chair': projectData.get('annotations',{}).get('chair'),
            'TAC Representative': projectData.get('annotations',{}).get('TAC_representative'),
            'Documentation': projectData.get('extra',{}).get('documentation_url'),
            'Calendar': projectData.get('annotations',{}).get('calendar_url'),
            'Artwork': projectData.get('artwork_url'),
            'iCal': projectData.get('annotations',{}).get('ical_url'),
            'LFX Insights URL': projectData.get('dev_stats_url'),
            'Accepted Date': projectData.get('accepted_at'),
            'Last Review Date': projectData.get('extra',{}).get('annual_review_date'),
            'Next Review Date': projectData.get('extra',{}).get('next_annual_review_date'),
            'Slack URL': projectData.get('slack_url'),
            'Chat Channel': projectData.get('chat_channel'),
            'Mailing List': projectData.get('mailing_list_url'),
            'Github Org': projectData.get('annotations',{}).get('project_org'),
            #'Best Practices Badge ID': projectData.get('bestPracticeBadgeId') if 'bestPracticeBadgeId' in projectData else None,
            'Primary Github Repo': projectData.get('repo_url'),
            'Contributed By': projectData.get('annotations',{}).get('contributed_by'),
            })

    with open(projectsCsvFile, 'w') as projectsCsvFileObject:
        writer = csv.DictWriter(projectsCsvFileObject, fieldnames = csvRows[0].keys())
        writer.writeheader() 
        writer.writerows(csvRows) 
