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
import logging

def main(args=None):
    parser = argparse.ArgumentParser(description="Exports Google Slides and Powerpoint decks from Google Drive, saving them in PDF and PPTX format in a specified directory.")
    parser.add_argument("--overview_decks", required=True, help="JSON array of Google Presentations to export ( format is '[{'url': GOOGLE-DRIVE-URL,'filename': EXPORT_FILENAME},...]' )")
    parser.add_argument("-o", "--output", help="location to save output to",default='.')
    parser.add_argument("--export_formats", help="Comma delimited lists of export formats", default="pdf,pptx")
    parser.add_argument('--log-level','-l',default='WARNING',help='Provide logging level. Example: --log-level DEBUG, default: WARNING')
    args = parser.parse_args(args)

    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {args.log_level}')
    logging.basicConfig(level=numeric_level,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    documents = json.loads(args.overview_decks)
    for document in documents:
        logging.info("Getting file {}".format(document['url']))
        for export_format in args.export_formats.split(","):
            pattern = r"/presentation/d/([a-zA-Z0-9-_]+)"
            match = re.search(pattern, document['url'])
            if match:
                try:
                    with requests.get('https://docs.google.com/feeds/download/presentations/Export?id={docid}&exportFormat={export_format}'.format(docid=match.group(1),export_format=export_format),stream=False) as response:
                        response.raise_for_status()
                        with open(Path(args.output,document['filename']).with_suffix(f".{export_format.lstrip('.')}"), 'wb') as f:
                            logging.info("Writing file {}".format(f.name))
                            f.write(response.content)
                except Exception as e:
                    logging.error(f"Error getting overview deck {document['url']} - {e}")
            else:
                logging.error(f"Invalid Google Presentation URL {document['url']}")

if __name__ == '__main__':
    main()
