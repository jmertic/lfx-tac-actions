#!/usr/bin/env python3
#
# Copyright this project and its contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import yaml
import argparse
import requests
import urllib.parse
import json
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="filename to save output to",default='_data/clomonitor.yaml')
    parser.add_argument("--landscape_url", help="URL to the project's landscape",required=True)
    args = parser.parse_args()
    
    landscape_hosted_projects = '{}/api/projects/all.json'.format(args.landscape_url)
    project_entries = []

    with requests.get(landscape_hosted_projects) as hosted_projects_response:
        project_data = hosted_projects_response.json()
        for project in project_data:
            if project.get('maturity') == 'emeritus':
                continue
            print("Processing {}...".format(project.get('name')))
        
            # grab correct logo from artwork repo
            logo_url = ''
            logo_url_dark = ''
            if project.get('artwork_url'):
                urlparts = urllib.parse.urlparse(project.get('artwork_url'))
                with requests.get('{}://{}/assets/data.json'.format(urlparts.scheme,urlparts.netloc)) as artwork_response:
                    artwork_data = artwork_response.json()
                    logo_url = '{}://{}{}{}'.format(urlparts.scheme,urlparts.netloc,urlparts.path,artwork_data.get(urlparts.path,{}).get('primary_logo'))
                    logo_url_dark = '{}://{}{}{}'.format(urlparts.scheme,urlparts.netloc,urlparts.path,artwork_data.get(urlparts.path,{}).get('dark_logo'))
            else:
                logo_url = project.get('logo_url')
                logo_url_dark = project.get('logo_url')

            project_entry = {
                'name': project.get('annotations',{}).get('slug'),
                'display_name': project.get('name'),
                'description': project.get('description'),
                'category': 'Visual Effects and Computer Graphics',
                'logo_url': logo_url,
                'logo_url_dark': logo_url_dark,
                'devstats_url': project.get('dev_stats_url'),
                'maturity': project.get('maturity'),
                'repositories': []
            }
            for repo in project.get('repositories',[]):
                project_entry['repositories'].append({
                    'name': repo.get('url').rsplit('/', 1)[-1],
                    'url': repo.get('url'),
                    'exclude': ['clomonitor']
                })
            if project_entry.get('repositories',[]) != []:
                project_entries.append(project_entry)
    
    with open(args.output, 'w') as clomonitor_file_object:
        print("Saving file {}".format(args.output))
        yaml.dump(project_entries, clomonitor_file_object, sort_keys=False, indent=2)

if __name__ == '__main__':
    main()
