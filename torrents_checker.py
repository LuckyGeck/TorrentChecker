#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# Name:        TorrentChecker
# Purpose:     Get new episodes of serials from different torrent trackers
#
# Author:      Sychev Pavel
#
# Created:     28.02.2012
# Copyright:   (c) Sychev Pavel 2012
# Licence:     GPL
# -------------------------------------------------------------------------

from plugins import plugins
from codecs import open
import json
from settings import settings


def load_torrents_list(path, encoding):
    torrents_list = []
    try:
        with open(path, 'r', 'utf8') as torrents_file:
            torrents_list = json.load(torrents_file, encoding=encoding)
    except:
        pass
    return torrents_list


def save_torrents_list(torrents_list, path, encoding):
    json_string = json.dumps(torrents_list,
                             indent=4, encoding=encoding, ensure_ascii=False)
    with open(path, 'w', 'utf8') as torrents_file:
        torrents_file.write(json_string)


def process_torrent(torrent):
    new_torrent = torrent.copy()
    if torrent["tracker"] not in plugins.servers:
        print "No such server handler: {}".format(torrent["tracker"])
    else:
        plugin = plugins.servers[torrent["tracker"]]
        plugin.authorize()

        torrent_id = torrent["id"]
        description = torrent.get("descr")
        old_md5 = torrent.get("hash", "")
        (new_md5, data) = plugin.load_torrent(torrent_id)

        if new_md5 != old_md5:
            print "Updated [{}] {}".format(torrent_id, description)
            file_name = plugin.filename_template % torrent_id
            with open(file_name, 'wb') as torrent_file:
                torrent_file.write(data)
            plugins.process_on_new_torrent(torrent_id, description, plugin)
            new_torrent["hash"] = new_md5
    return new_torrent


def main():
    plugins.load(settings)

    torrents_list_path = settings["torrents.list"]

    encoding = settings.get("torrents.list_enc", "cp1251")
    torrents_list = load_torrents_list(torrents_list_path, encoding)
    new_torrents_list = []

    plugins.process_on_start()

    for torrent in torrents_list:
        new_torrent = torrent
        try:
            new_torrent = process_torrent(torrent)
        except Exception as e:
            print 'Torrent processing failure: {}'.format(torrent)
        new_torrents_list.append(new_torrent)

    plugins.process_on_finish()

    save_torrents_list(new_torrents_list, torrents_list_path, encoding)


if __name__ == '__main__':
    main()
