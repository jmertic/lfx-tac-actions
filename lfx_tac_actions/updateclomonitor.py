#!/usr/bin/env python3
#
# Copyright this project and its contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import yaml
import urllib.request
import urllib.parse
import json
import os

def main():
    if os.environ.get("LANDSCAPE_URL") != '' and os.environ.get("ARTWORK_URL") != '':
        cloMonitorFile = '_data/clomonitor.yaml'
        landscapeHostedProjects = '{}/api/projects/all.json'.format(os.environ.get("LANDSCAPE_URL"))
        projectEntries = []

        with urllib.request.urlopen(landscapeHostedProjects) as hostedProjectsResponse:
            projectData = json.load(hostedProjectsResponse)
            for project in projectData:
                if project.get('maturity') == 'emeritus':
                    continue
                print("Processing {}...".format(project.get('name')))
            
                # grab correct logo from artwork repo
                logo_url = ''
                logo_url_dark = ''
                if project.get('artwork_url'):
                    urlparts = urllib.parse.urlparse(project.get('artwork_url'))
                    with urllib.request.urlopen('{}://{}/assets/data.json'.format(urlparts.scheme,urlparts.netloc)) as artworkResponse:
                        artworkData = json.load(artworkResponse)
                        logo_url = '{}://{}{}{}'.format(urlparts.scheme,urlparts.netloc,urlparts.path, item.get(urlparts.path,{}).get('primary_logo'))
                        logo_url_dark = '{}://{}{}{}'.format(urlparts.scheme,urlparts.netloc,urlparts.path, item.get(urlparts.path,{}).get('dark_logo'))
                else:
                    logo_url = project.get('logo')
                    logo_url_dark = project.get('logo')

                projectEntry = {
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
                    projectEntry['repositories'].append({
                        'name': repo.get('url').rsplit('/', 1)[-1],
                        'url': repo.get('url'),
                        'exclude': ['clomonitor']
                    })
                projectEntries.append(projectEntry)
        
    with open(cloMonitorFile, 'w') as cloMonitorFileObject:
        yaml.dump(projectEntries, cloMonitorFileObject, sort_keys=False, indent=2)

if __name__ == '__main__':
    main()
