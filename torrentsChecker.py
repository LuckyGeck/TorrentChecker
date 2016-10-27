#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# Name:        TorrentChecker
# Purpose:     Get new episodes of serials from different torrent trackers
#
# Author:      Sychev Pavel
#
# Created:     28.02.2012
# Copyright:   (c) Sychev Pavel 2012
# Licence:     GPL
#-------------------------------------------------------------------------

from plugins import *
from codecs import open
import json
import sys
from settings import settings
from errLog import err_file

sys.stderr = err_file(settings["error_log.saveas"])


def checkTorrentAndDownload(torrID, lastmd5, fileDir, plugin):
    fileName = fileDir % torrID
    try:
        (md5, data) = plugin.getTorrent(torrID)

        if md5 != lastmd5:
            f = open(fileName, 'wb')
            f.write(data)
            f.close()
            return md5
    except:
        msg = "[{} plugin] Some network error while downloading torrent file."
        print msg.format(plugin.plugin_name)
    return lastmd5
    pass


def loadTorrentsList(path, encoding):
    retList = []
    try:
        lines = open(path, 'r', 'utf8').read()
        retList = json.loads(lines)
    except:
        pass
    return retList


def saveTorrentsList(torrentQueue, torLstPath, encoding):
    jsonString = json.dumps(torrentQueue,
                            indent=2, encoding=encoding, ensure_ascii=False)
    open(torLstPath, 'w', 'utf8').write(jsonString)


def setProxy(url, login, password):
    import urllib2
    passmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passmgr.add_password(None, url, login, password)
    authinfo = urllib2.ProxyBasicAuthHandler(passmgr)
    proxy_support = urllib2.ProxyHandler({'http': url})

    opener = urllib2.build_opener(proxy_support, authinfo)
    urllib2.install_opener(opener)


def processOnLoadPlugins(onLoadPlugins, torrentQueue, newTorrentQueue):
    for plg in onLoadPlugins:
        try:
            plg.onLoadProcess(torrentQueue, newTorrentQueue)
        except Exception as e:
            msg = "[{}] Error while running onLoadPlugin!\n*** {} ***"
            print msg.format(plg.plugin_name, e)


def onNewEpisodeOccurred(onNewEpisodePlugins, torrID, descr,
                         grabDescrFunction, server_plugin):
    for plg in onNewEpisodePlugins:
        try:
            plg.onNewEpisodeProcess(
                torrID, descr, grabDescrFunction, server_plugin)
        except Exception as e:
            msg = "[{}] Error while running onNewEpisodePlugin!\n*** {} ***"
            print msg.format(plg.plugin_name, e)


def processOnFinishPlugins(onFinishPlugins, torrentQueue, newTorrentQueue):
    for plg in onFinishPlugins:
        try:
            plg.onFinishProcess(torrentQueue, newTorrentQueue)
        except Exception as e:
            msg = "[{}] Error while running onFinishPlugin!\n*** {} ***"
            print msg.format(plg.plugin_name, e)


def main():
    servers = {}  # <-- server plugins

    # PluginsLists:
    onLoadPlugins = []
    onNewEpisodePlugins = []
    onFinishPlugins = []

    reloadPlugins(
        servers, onLoadPlugins, onNewEpisodePlugins, onFinishPlugins, settings)

    torLstPath = settings["torrents.list"]

    encoding = settings.get("torrents.list_enc", "cp1251")

    torrentQueue = loadTorrentsList(torLstPath, encoding)
    newTorrentQueue = []

    processOnLoadPlugins(onLoadPlugins, torrentQueue, newTorrentQueue)

    if settings.has_key("proxy.active") and (settings["proxy.active"] == '1'):
        setProxy(settings["proxy.url"], settings[
                 "proxy.login"], settings["proxy.password"])

    for key in torrentQueue:
        # onServerPlugin
        # ---PROCESSING---
        if servers.has_key(key["tracker"]) == False:
            print "No such server handler: serv_name={}".format(key[0])
            continue

        plug_list = servers[key["tracker"]]
        if len(plug_list) > 1:
            plugin = plug_list[1]
        else:
            plugin = plug_list[0](settings)
            plug_list.append(plugin)

        old_md5 = key.get("hash", "")
        new_md5 = checkTorrentAndDownload(
            key["id"], old_md5, settings[key["tracker"]+'.saveas'], plugin)
        # ---END-PROCESSING---

        if new_md5 != old_md5:  # onNewEpisode
            onNewEpisodeOccurred(onNewEpisodePlugins,
                                 key["id"], key["descr"],
                                 plugin.grabDescr, plugin)

        newTorrentQueue.append(
            {
                "tracker": key["tracker"],
                "id": key["id"],
                "hash": new_md5,
                "descr": key["descr"]
            }
        )

    # onFinish
    processOnFinishPlugins(onFinishPlugins, torrentQueue, newTorrentQueue)

    saveTorrentsList(newTorrentQueue, torLstPath, encoding)
    pass

if __name__ == '__main__':
    main()
