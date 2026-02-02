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

def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--slug", help="Umbrella Foundation slug", required=True)
    parser.add_argument("-o", "--output", help="location to save output to",default='.')
    args = parser.parse_args(args)

    endpointURL = 'https://api-gw.platform.linuxfoundation.org/project-service/v1/public/projects?$filter=parentSlug%20eq%20{}%20and%20status%20eq%20Active&pageSize=2000&orderBy=name'

    with requests.get(endpointURL.format(args.slug)) as response:
        projectList = response.json()
        for record in projectList['Data']:
            if record.get('CharterURL'):
                if record.get('CharterURL').startswith('https://github.com'):
                    record['CharterURL'] = record['CharterURL'].replace("/raw/","/").replace("/blob/","/").replace("https://github.com","https://raw.githubusercontent.com")
                print("Getting file {}...".format(record.get('CharterURL')))
                try:
                    with requests.get(record['CharterURL'],stream=False) as response:
                        response.raise_for_status()
                        root, extension = os.path.splitext(urlparse(record['CharterURL']).path)
                        with open(Path(args.output,f"{record['Slug']}_charter").with_suffix(extension), 'wb') as f:
                            print("Writing file {}...".format(f.name))
                            f.write(response.content)
                except:
                    print("Error getting file")

if __name__ == '__main__':
    main()
