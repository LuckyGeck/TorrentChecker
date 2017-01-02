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

from plugins import *
from codecs import open
import json
import sys
from settings import settings
from log import ErrorFile

sys.stderr = ErrorFile(settings["error_log.saveas"])


def check_torrent_and_download(torrent_id, last_md5, file_dir, plugin):
    file_name = file_dir % torrent_id
    try:
        (md5, data) = plugin.load_torrent(torrent_id)
        if md5 != last_md5:
            with open(file_name, 'wb') as torrent_file:
                torrent_file.write(data)
            return md5
    except Exception as e:
        plugin.log_error(
            'Some network error while downloading torrent file', e)
    return last_md5


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
                             indent=2, encoding=encoding, ensure_ascii=False)
    with open(path, 'w', 'utf8') as torrents_file:
        torrents_file.write(json_string)


def set_proxy(url, login, password):
    import urllib2
    pass_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    pass_mgr.add_password(None, url, login, password)
    authinfo = urllib2.ProxyBasicAuthHandler(pass_mgr)
    proxy_support = urllib2.ProxyHandler({'http': url})

    opener = urllib2.build_opener(proxy_support, authinfo)
    urllib2.install_opener(opener)


def process_on_load_plugins(plugins, torrents_list, new_torrents_list):
    for plugin in plugins:
        try:
            plugin.on_load_process(torrents_list, new_torrents_list)
        except Exception as e:
            plugin.log_error('Error while running on_load_process', e)


def process_on_new_episode_occurred(plugins,
                                    torrent_id, description, server_plugin):
    for plugin in plugins:
        try:
            plugin.on_new_episode_process(torrent_id,
                                          description, server_plugin)
        except Exception as e:
            plugin.log_error('Error while running on_new_episode_process', e)


def process_on_finish_plugins(plugins, torrents_list, new_torrents_list):
    for plugin in plugins:
        try:
            plugin.on_finish_process(torrents_list, new_torrents_list)
        except Exception as e:
            plugin.log_error('Error while running on_finish_process', e)


def main():
    servers = {}  # <-- server plugins

    # PluginsLists:
    on_load_plugins = []
    on_new_episode_plugins = []
    on_finish_plugins = []

    reload_plugins(servers,
                   on_load_plugins, on_new_episode_plugins, on_finish_plugins,
                   settings)

    torrents_list_path = settings["torrents.list"]

    encoding = settings.get("torrents.list_enc", "cp1251")

    torrents_list = load_torrents_list(torrents_list_path, encoding)
    new_torrents_list = []

    process_on_load_plugins(on_load_plugins, torrents_list, new_torrents_list)

    if settings.get("proxy.active", '0') == '1':
        try:
            set_proxy(settings["proxy.url"],
                      settings["proxy.login"],
                      settings["proxy.password"])
        except:
            pass

    for key in torrents_list:
        # onServerPlugin
        # ---PROCESSING---
        if key["tracker"] not in servers:
            print "No such server handler: serv_name={}".format(key["tracker"])
            continue

        plugin = servers[key["tracker"]]

        old_md5 = key.get("hash", "")
        save_as = settings[key["tracker"]+'.saveas']
        new_md5 = check_torrent_and_download(key["id"],  old_md5,
                                             save_as, plugin)
        # ---END-PROCESSING---

        if new_md5 != old_md5:  # onNewEpisode
            process_on_new_episode_occurred(on_new_episode_plugins,
                                            key["id"], key["descr"], plugin)

        new_torrents_list.append(
            {
                "tracker": key["tracker"],
                "id": key["id"],
                "hash": new_md5,
                "descr": key["descr"]
            }
        )

    # onFinish
    process_on_finish_plugins(on_finish_plugins,
                              torrents_list, new_torrents_list)

    save_torrents_list(new_torrents_list, torrents_list_path, encoding)

if __name__ == '__main__':
    main()
