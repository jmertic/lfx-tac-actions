#!/usr/bin/env python3
#
# Copyright this project and it's contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import requests
import json
import re
from pathlib import Path
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--overview_decks", required=True, help="JSON array of Google Presentations to export ( format is '[{'url': GOOGLE-DRIVE-URL,'filename': EXPORT_FILENAME},...]' )")
    parser.add_argument("-o", "--output", help="location to save output to",default='.')
    parser.add_argument("--export_formats", help="Comma delimited lists of export formats", default="pdf,pptx")
    args = parser.parse_args()

    documents = json.loads(args.overview_decks)
    for document in documents:
        print("Getting file {}...".format(document['url']))
        for exportFormat in args.export_formats.split(","):
            pattern = r"/presentation/d/([a-zA-Z0-9-_]+)"
            match = re.search(pattern, document['url']) 
            if match:
                try:
                    contents = requests.get('https://docs.google.com/feeds/download/presentations/Export?id={docid}&exportFormat={exportFormat}'.format(docid=match.group(1),exportFormat=exportFormat),stream=False)
                    with open(Path(args.output,document['filename']).with_suffix(f".{exportFormat.lstrip('.')}"), 'wb') as f:
                        print("Writing file {}...".format(f.name))
                        f.write(contents.content)
                except HttpError as err:
                    print(err.content)

if __name__ == '__main__':
    main()
