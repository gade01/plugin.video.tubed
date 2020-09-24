# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from urllib.parse import parse_qs
from urllib.parse import urlencode

from ..constants import ADDON_ID


def parse_query(query):
    payload = {
        'mode': 'main'
    }

    args = parse_qs(query.lstrip('?'))

    for arg in args:
        if len(args[arg]) == 1:
            payload[arg] = args[arg][0]

        else:
            payload[arg] = args[arg]

    return payload


def create_addon_path(parameters):
    return '?'.join(['plugin://%s/' % ADDON_ID, urlencode(parameters)])