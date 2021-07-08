#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author:       Sychev Pavel
# Created:      28.02.2012
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL


import json
from codecs import open

import logging

from plugins import plugins, base
from settings import settings


logger = logging.getLogger(__name__)


def load_torrents_list(path):
    torrent_dicts = json.load(open(path, 'r'))
    return list(map(base.Torrent.load, torrent_dicts))


def save_torrents_list(torrents_list, path):
    torrent_dicts = list(map(lambda t: t.dump(), torrents_list))
    json.dump(torrent_dicts, open(path, 'w'), indent=4)


def process_torrent(torrent, save_as_template):
    # type: (base.Torrent, str) -> base.Torrent
    plugin = plugins.get_server_for_torrent(torrent)
    if not plugin:
        msg = "No such server handler: {}".format(torrent.tracker)
        raise Exception(msg)

    description = torrent.description
    data = plugin.load_torrent_data(torrent)
    new_torrent = torrent.copy()
    new_torrent.update_hash_for_data(data)
    if torrent.hash == new_torrent.hash:
        return torrent
    new_torrent.full_description = plugin.load_description(torrent)

    logger.info("Updated [{}] {}".format(torrent.id, description))
    file_name = save_as_template.format(**torrent.dump())
    with open(file_name, 'wb') as torrent_file:
        torrent_file.write(data)
    plugins.process_on_new_torrent(new_torrent, plugin)
    return new_torrent


def main():
    plugins.load(settings["plugins"])

    shows_settings = settings["shows"]
    torrents_list_path = shows_settings["list_path"]
    save_as_tamplate = shows_settings["save_as"]
    torrents_list = load_torrents_list(torrents_list_path)
    new_torrents_list = []

    plugins.process_on_start()

    for torrent in torrents_list:
        new_torrent = torrent
        try:
            new_torrent = process_torrent(torrent, save_as_tamplate)
        except Exception as e:
            logger.warning('Torrent processing failure ({}): {}'.format(
                torrent, e
            ))
        new_torrents_list.append(new_torrent)

    plugins.process_on_finish()

    save_torrents_list(new_torrents_list, torrents_list_path)


def setup_logging():
    logging_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=logging_format, level=logging.DEBUG)


if __name__ == '__main__':
    setup_logging()
    main()
