# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from enum import Enum


class MODES(Enum):
    MAIN = 'main'
    MOST_POPULAR = 'most_popular'
    PLAY = 'play'

    def __str__(self):
        return str(self.value).lower()