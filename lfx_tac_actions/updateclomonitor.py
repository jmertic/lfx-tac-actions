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
import logging
import ipaddress
import socket
from pathlib import Path
import sys

from . import setup_logging, get_landscape_endpoint

def load_from_artwork_repo(artwork_url):
    urlparts = urllib.parse.urlparse(artwork_url)
    project = {}
    try:
        with requests.get(f"{urlparts.scheme}://{urlparts.netloc}/assets/data.json") as artwork_response:
            artwork_response.raise_for_status()
            artwork_data = artwork_response.json()
            if artwork_data.get(urlparts.path):
                project['clotributor_category'] = artwork_data.get(urlparts.path,{}).get('clotributor_category')
                project['logo_url'] = f"{urlparts.scheme}://{urlparts.netloc}{urlparts.path}{artwork_data.get(urlparts.path,{}).get('primary_logo')}"
                if artwork_data.get(urlparts.path,{}).get('primary_logo') != artwork_data.get(urlparts.path,{}).get('dark_logo'):
                    project['logo_dark_url'] = f"{urlparts.scheme}://{urlparts.netloc}{urlparts.path}{artwork_data.get(urlparts.path,{}).get('dark_logo')}"
                logging.info(f"Setting logo_url to {project.get('logo_url')} and logo_dark_url to {project.get('logo_dark_url')} from {project.get('artwork_url')}")
    except Exception as e:
        logging.exception(f"Error getting artwork repo file {artwork_response.url} - error message '{e}'")

    return project

def parse_repositories(repos):
    returnrepos = []

    for repo in repos:
        returnrepos.append({
            'name': repo.get('url').rsplit('/', 1)[-1],
            'url': repo.get('url'),
            'exclude': ['clomonitor']
        })

    return returnrepos

def main(args=None):
    parser = argparse.ArgumentParser(description="Pulls hosted project data from a project's landscape in YAML format to `stdout` that can imported into CLOMonitor.")
    parser.add_argument('--log-level','-l',default='WARNING',help='Provide logging level. Example: --log-level DEBUG, default: WARNING')
    parser.add_argument("--landscape_url", help="URL to the project's landscape",required=True)
    args = parser.parse_args(args)

    setup_logging(args.log_level)

    project_entries = []

    try:
        landscape_hosted_projects = get_landscape_endpoint(args.landscape_url)
        hosted_projects_response = requests.get(landscape_hosted_projects)
        hosted_projects_response.raise_for_status()
        project_data = hosted_projects_response.json()
    except Exception as e:
        logging.critical(f"Error getting landscape_url {args.landscape_url} - error message '{e}'")
        return

    for project in project_data:
        if project.get('maturity') == 'emeritus':
            continue
        logging.info(f"Processing {project.get('name')}")

        # grab correct logo from artwork repo
        if project.get('artwork_url'):
            logging.info("Loading data from %s", project.get("artwork_url"))
            artwork_data = load_from_artwork_repo(project.get('artwork_url'))
            project['clotributor_category'] = artwork_data.get('clotributor_category')
            project['logo_url'] = artwork_data.get('logo_url') or project['logo_url']
            project['logo_dark_url'] = artwork_data.get('logo_dark_url')

        if project.get('maturity') == 'long-term-working-group':
            project['maturity'] = 'working-group'

        project_entry = {
            'name': project.get('lfx_slug'),
            'display_name': project.get('name'),
            'description': project.get('description'),
            'category': project.get('clotributor_category'),
            'logo_url': project.get('logo_url'),
            'logo_dark_url': project.get('logo_dark_url'),
            'devstats_url': project.get('devstats_url'),
            'maturity': project.get('maturity'),
            'repositories': []
        }
        project_entry['repositories'] = parse_repositories(project.get('repositories',[]))
        if project_entry.get('repositories',[]) != []:
            logging.info(f"Adding {project.get('name')}")
            project_entries.append({k: v for k, v in project_entry.items() if v})

    if not project_entries:
        logging.warning("No valid data retrieved.")
        return

    yaml.dump(project_entries, sys.stdout, sort_keys=False, indent=2)

if __name__ == '__main__':
    main()
