#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author:       Sychev Pavel
# Created:      28.02.2012
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL

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


def process_torrent(torrent, save_as_tamplate):
    new_torrent = torrent.copy()
    if torrent["tracker"] not in plugins.servers:
        print "No such server handler: {}".format(torrent["tracker"])
    else:
        plugin = plugins.servers[torrent["tracker"]]
        plugin.authorize()

        torrent_id = torrent["id"]
        description = torrent.get("description")
        old_md5 = torrent.get("hash", "")
        (new_md5, data) = plugin.load_torrent(torrent_id)

        if new_md5 != old_md5:
            print "Updated [{}] {}".format(torrent_id, description)
            format_args = {
                "torrent_id": torrent_id,
                "plugin_name": plugin.get_plugin_name(),
            }
            file_name = save_as_tamplate.format(**format_args)
            with open(file_name, 'wb') as torrent_file:
                torrent_file.write(data)
            plugins.process_on_new_torrent(torrent_id, description, plugin)
            new_torrent["hash"] = new_md5
    return new_torrent


def main():
    plugins.load(settings["plugins"])

    shows_settings = settings["shows"]
    torrents_list_path = shows_settings["list"]["path"]
    encoding = shows_settings["list"].get("enc", "cp1251")
    save_as_tamplate = shows_settings["save_as"]
    torrents_list = load_torrents_list(torrents_list_path, encoding)
    new_torrents_list = []

    plugins.process_on_start()

    for torrent in torrents_list:
        new_torrent = torrent
        try:
            new_torrent = process_torrent(torrent, save_as_tamplate)
        except Exception as e:
            print 'Torrent processing failure ({}): {}'.format(torrent, e)
        new_torrents_list.append(new_torrent)

    plugins.process_on_finish()

    save_torrents_list(new_torrents_list, torrents_list_path, encoding)


if __name__ == '__main__':
    main()
