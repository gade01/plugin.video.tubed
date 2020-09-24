# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import xbmcplugin  # pylint: disable=import-error

from ..constants import MODES
from ..lib.items.directory import Directory
from ..lib.url_utils import create_addon_path


def invoke(context):
    items = []

    directory = Directory(
        label=context.i18n('Most Popular'),
        path=create_addon_path(parameters={
            'mode': MODES.MOST_POPULAR
        })
    )
    items.append(tuple(directory))

    xbmcplugin.addDirectoryItems(context.handle, items, len(items))

    xbmcplugin.endOfDirectory(context.handle, True)