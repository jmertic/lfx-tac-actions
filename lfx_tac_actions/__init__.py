#!/usr/bin/env python3
#
# Copyright this project and it's contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import logging
import sys
from urllib.parse import urlsplit, urlunsplit

def setup_logging(log_level):
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    logging.basicConfig(level=numeric_level,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',stream=sys.stderr)

def get_landscape_endpoint(landscape_url):
    landscape_url_parts = urlsplit(landscape_url)

    if landscape_url_parts.scheme not in ('http', 'https'):
        raise ValueError(f"Invalid URL scheme: {landscape_url_parts.scheme}. Only HTTP and HTTPS are allowed.")
        return False

    return urlunsplit((landscape_url_parts.scheme, landscape_url_parts.netloc, "/api/projects/all.json", "", ""))
