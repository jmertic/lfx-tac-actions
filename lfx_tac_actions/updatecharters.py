#!/usr/bin/env python3
#
# Copyright this project and it's contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import requests
import os
from urllib.parse import urlparse
import argparse
from pathlib import Path
import logging

def main(args=None):
    parser = argparse.ArgumentParser(description="Downloads the Technical Charters for the subprojects of a project identified by --slug, saving them in a specified directory with naming format of `SLUG_charter`.")
    parser.add_argument("-s", "--slug", help="Umbrella Foundation slug", required=True)
    parser.add_argument("-o", "--output", help="location to save output to",default='.')
    parser.add_argument('--log-level','-l',default='WARNING',help='Provide logging level. Example: --log-level DEBUG, default: WARNING')
    args = parser.parse_args(args)

    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {args.log_level}')
    logging.basicConfig(level=numeric_level,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    endpoint_url = 'https://api-gw.platform.linuxfoundation.org/project-service/v1/public/projects?$filter=parentSlug%20eq%20{}%20and%20status%20eq%20Active&pageSize=2000&orderBy=name'

    try:
        response = requests.get(endpoint_url.format(args.slug))
        response.raise_for_status()
        projectlist = response.json()
    except Exception as e:
        logging.critical(f"Error getting charters at {response.url} - {e}")
        return

    for record in projectlist['Data']:
        if record.get('CharterURL'):
            if record.get('CharterURL').startswith('https://github.com'):
                record['CharterURL'] = record['CharterURL'].replace("/raw/","/").replace("/blob/","/").replace("https://github.com","https://raw.githubusercontent.com")
            logging.info("Getting file {}".format(record.get('CharterURL')))
            try:
                with requests.get(record['CharterURL'],stream=False) as response:
                    response.raise_for_status()
                    _, extension = os.path.splitext(urlparse(record['CharterURL']).path)
                    with open(Path(args.output,f"{record['Slug']}_charter").with_suffix(extension), 'wb') as f:
                        logging.info("Writing file {}".format(f.name))
                        f.write(response.content)
            except Exception as e:
                logging.error(f"Error getting file {record['CharterURL']} - '{e}'")

if __name__ == '__main__':
    main()
