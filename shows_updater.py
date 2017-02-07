#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author:       Sychev Pavel
# Created:      28.02.2012
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL


import json
import hashlib
from codecs import open

from plugins import plugins
from settings import settings


def load_torrents_list(path, encoding):
    return json.load(open(path, 'r', 'utf8'), encoding=encoding)


def save_torrents_list(torrents_list, path, encoding):
    json_string = json.dump(torrents_list, open(path, 'w', 'utf8'),
                            indent=4, encoding=encoding, ensure_ascii=False)


def data_hash(data):
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()


def process_torrent(torrent, save_as_tamplate):
    plugin = plugins.servers.get(torrent["tracker"])
    if not plugin:
        msg = "No such server handler: {}".format(torrent["tracker"])
        raise Exception(msg)

    torrent_id = torrent["id"]
    description = torrent.get("description")
    old_md5 = torrent.get("hash", "")
    data = plugin.load_torrent(torrent_id)
    new_md5 = data_hash(data)
    if new_md5 == old_md5:
        return torrent

    print "Updated [{}] {}".format(torrent_id, description)
    format_args = {
        "torrent_id": torrent_id,
        "plugin_name": plugin.get_plugin_name(),
    }
    file_name = save_as_tamplate.format(**format_args)
    with open(file_name, 'wb') as torrent_file:
        torrent_file.write(data)
    plugins.process_on_new_torrent(torrent_id, description, plugin)
    new_torrent = torrent.copy()
    new_torrent["hash"] = new_md5
    return new_torrent


def main():
    plugins.load(settings["plugins"])

    shows_settings = settings["shows"]
    torrents_list_path = shows_settings["list"]["path"]
    encoding = shows_settings["list"].get("enc", "utf8")
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
