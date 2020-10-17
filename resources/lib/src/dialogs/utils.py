# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import json
from html import unescape

import arrow
import xbmc  # pylint: disable=import-error

from ..generators.data_cache import get_cached
from ..generators.utils import get_thumbnail
from ..generators.video import video_generator
from ..lib.logger import Log
from ..lib.time import iso8601_duration_to_seconds

LOG = Log('dialogs', __file__)


def add_related_video_to_playlist(context, video_id):  # pylint: disable=too-many-locals
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    metadata = {}

    if playlist.size() <= 999:
        pages = 0
        add_item = None
        page_token = ''
        current_items = playlist_items(playlist.getPlayListId())

        while not add_item and pages <= 2:
            pages += 1
            try:
                payload = context.api.related_videos(
                    video_id,
                    page_token=page_token,
                    max_results=17,
                    fields='items(kind,id(videoId),snippet(title))'
                )
                result_items = payload.get('items', [])
                page_token = payload.get('nextPageToken', '')

            except:  # pylint: disable=bare-except
                result_items = []

            if result_items:
                add_item = next((
                    item for item in result_items
                    if not any((item.get('id', {}).get('videoId') in playlist_item.get('file') or
                                (unescape(item.get('snippet', {}).get('title', '')) ==
                                 playlist_item.get('label'))) for playlist_item in current_items)),
                    None)

            if not add_item and page_token:
                continue

            if add_item:
                related_id = add_item.get('id', {}).get('videoId')
                cached_payload = get_cached(context, context.api.videos, [related_id])
                cached_video = cached_payload.get(related_id, {})
                cached_snippet = cached_video.get('snippet', {})
                cached_content_details = cached_video.get('contentDetails', {})
                cached_statistics = cached_video.get('statistics', {})

                channel_id = cached_snippet.get('channelId', '')
                channel_name = unescape(cached_snippet.get('channelTitle', ''))

                video_title = unescape(cached_snippet.get('title', ''))

                published_arrow = None
                live_details = cached_video.get('liveStreamingDetails')

                if live_details:
                    actual_start = live_details.get('actualStartTime')
                    actual_end = live_details.get('actualEndTime')
                    scheduled_start = live_details.get('scheduledStartTime')

                    published = actual_end or actual_start or scheduled_start
                    if published:
                        published_arrow = arrow.get(published).to('local')

                if not published_arrow:
                    published_arrow = arrow.get(cached_snippet['publishedAt']).to('local')

                likes = int(cached_statistics.get('likeCount', '0'))
                dislikes = int(cached_statistics.get('dislikeCount', '0'))
                votes = likes + dislikes
                try:
                    rating = '%0.1f' % ((likes / votes) * 10)
                except ZeroDivisionError:
                    rating = '0.0'

                metadata = {
                    'video_id': related_id,
                    'channel_id': channel_id,
                    'title': video_title,
                    'description': unescape(cached_snippet.get('description', '')),
                    'channel_name': channel_name,
                    'year': published_arrow.year,
                    'premiered': published_arrow.format('YYYY-MM-DD'),
                    'dateadded': published_arrow.format('YYYY-MM-DD HH:mm:ss'),
                    'tag': cached_snippet.get('tags', ''),
                    'rating': rating,
                    'votes': votes,
                    'like_count': likes,
                    'dislike_count': dislikes,
                    'view_count': int(cached_statistics.get('viewCount', 0)),
                    'comment_count': int(cached_statistics.get('commentCount', 0)),
                    'thumbnail': get_thumbnail(cached_snippet),
                }

                duration = iso8601_duration_to_seconds(cached_content_details.get('duration', ''))
                if duration:
                    metadata['duration'] = duration

                generated = list(video_generator(context, [add_item]))
                path, list_item, _ = generated[0]
                playlist.add(path, list_item)
                break

            if not page_token:
                break

    return metadata


def playlist_items(playlist_id):
    request = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "Playlist.GetItems",
            "params": {
                "properties": ["title", "file"],
                "playlistid": playlist_id
            },
            "id": 1
        })

    payload = json.loads(xbmc.executeJSONRPC(request))

    if 'result' in payload:
        if 'items' in payload['result']:
            return payload['result']['items']

        return []

    if 'error' in payload:
        message = payload['error']['message']
        code = payload['error']['code']
        error = 'Requested %s and received error %s and code: %s' % (request, message, code)

    else:
        error = 'Requested %s and received error %s' % (request, str(payload))

    LOG.error(error)
    return []
