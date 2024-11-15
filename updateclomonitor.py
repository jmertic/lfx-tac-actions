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

cloMonitorFile = '_data/clomonitor.yaml'

if os.environ.get("LANDSCAPE_URL") != '' and os.environ.get("ARTWORK_URL") != '':
    landscapeHostedProjects = '{}/data/exports/projects-hosted.json'.format(os.environ.get("LANDSCAPE_URL"))

    projectEntries = []

    with urllib.request.urlopen(landscapeHostedProjects) as hostedProjectsResponse:
        projectData = json.load(hostedProjectsResponse)
        if projectData.get('project') == 'emeritus':
            continue
        print("Processing {}...".format(projectData.get('name')))
        
        # grab correct logo from artwork repo
        logo_url = ''
        logo_url_dark = ''
        if 'artwork_url' in projectData:
            urlparts = urllib.parse.urlparse(projectData.get('artwork_url'))
            with urllib.request.urlopen('{}://{}/assets/data.json'.format(urlparts.scheme,urlparts.netloc)) as artworkResponse:
                artworkData = json.load(artworkResponse)
                logo_url = '{}://{}{}{}'.format(urlparts.scheme,urlparts.netloc,urlparts.path, item.get(urlparts.path,{}).get('primary_logo'))
                logo_url_dark = '{}://{}{}{}'.format(urlparts.scheme,urlparts.netloc,urlparts.path, item.get(urlparts.path,{}).get('dark_logo'))
        else:
            logo_url = project.get('logo')
            logo_url_dark = project.get('logo')

        projectEntry = {
            'name': projectData.get('id'),
            'display_name': projectData.get('name'),
            'description': projectData.get('description'),
            'category': 'Visual Effects and Computer Graphics',
            'logo_url': logo_url,
            'logo_url_dark': logo_url_dark,
            'devstats_url': projectData.get('dev_stats_url'),
            'maturity': projectData.get('maturity'),
            'repositories': []
        }
        if 'repositories' in projectData:
            for repo in projectData.get('repositories'):
                projectEntry['repositories'].append({
                    'name': repo.get('url').rsplit('/', 1)[-1],
                    'url': repo.get('url'),
                    'exclude': ['clomonitor']
                })
            projectEntries.append(projectEntry)
    
with open(cloMonitorFile, 'w') as cloMonitorFileObject:
    yaml.dump(projectEntries, cloMonitorFileObject, sort_keys=False, indent=2)
