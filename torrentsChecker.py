#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        TorrentChecker
# Purpose:     Get new episodes of serials from different torrent trackers
#
# Author:      Sychev Pavel
#
# Created:     28.02.2012
# Copyright:   (c) Sychev Pavel 2012
# Licence:     GPL
#-------------------------------------------------------------------------------

from plugins import *
from codecs import open
import string
import os
import sys
import codecs
from errLog import err_file

#sys.stdout = open('/root/torrents_checker.log', 'a')
sys.stderr = err_file("/shares/Scripts/python/torrentChecker/error.log")

def readSettings(path, settings):
    fileSettings = open(path, 'r', 'utf-8')
    info = fileSettings.readline()
    while (info != ''):
        if string.strip(info) == '':
            info = fileSettings.readline()
            continue
        (first, second) = string.split(string.strip(info), '=', 2)
        settings[first] = second
        info = fileSettings.readline()
    # (login,password) = string.split(s, ':')
    fileSettings.close()

def checkTorrentAndDownload(torrID, lastmd5, fileDir, plugin):
    fileName = fileDir%torrID
    try:
        (md5,data) = plugin.getTorrent(torrID)

        if md5 != lastmd5 :
            f = open(fileName, 'wb')
            f.write(data)
            f.close()
            return md5
    except:
        print "[%s plugin] Some network error while downloading torrent file."%plugin.plugin_name
    return lastmd5
    pass

def loadTorrentsList(path, encoding):
    fileT = open(path, 'r', encoding)# 'utf-8')
    retList = []
    torLines = fileT.readlines()
    for s in torLines:
        s = s.strip()
        t = s.split(':',3)
        try:
            retList.append(t)
        except:
            pass
    fileT.close()
    return retList

def saveTorrentsList(torrentQueue, torLstPath, encoding):
    f = open(torLstPath, 'w', encoding)
    for key in torrentQueue:
        f.write(u'%s:%s:%s:%s\r\n'%key)
    f.close()
    pass

def setProxy(url, login, password):
    passmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passmgr.add_password(None, url , login, password)
    authinfo = urllib2.ProxyBasicAuthHandler(passmgr)
    proxy_support = urllib2.ProxyHandler({'http' : url})

    opener = urllib2.build_opener(proxy_support, authinfo)
    urllib2.install_opener(opener)

def processOnLoadPlugins(onLoadPlugins, torrentQueue, newTorrentQueue):
    for plg in onLoadPlugins:
        try:
            plg.onLoadProcess(torrentQueue,newTorrentQueue)
        except Exception as e:
            print "[%s plugin] *** Error while running onLoadPlugin! *** \n*** %s ***"%(plg.plugin_name,e)

def onNewEpisodeOccurred(onNewEpisodePlugins, torrID, descr, grabDescrFunction, server_plugin):
    try:
        descr = descr.encode("cp1251")
    except Exception as e:
        print "[onNewEpisodeOccurred] Convertion error!\n*** %s ***"%e
        return
    for plg in onNewEpisodePlugins:
        try:
            plg.onNewEpisodeProcess(torrID, descr, grabDescrFunction, server_plugin)
        except Exception as e:
            print "[%s plugin] *** Error while running onNewEpisodePlugin! *** \n*** %s ***"%(plg.plugin_name,e)

def processOnFinishPlugins(onFinishPlugins, torrentQueue, newTorrentQueue):
    for plg in onFinishPlugins:
        try:
            plg.onFinishProcess(torrentQueue,newTorrentQueue)
        except Exception as e:
            print "[%s plugin] *** Error while running onFinishPlugin! *** \n*** %s ***"%(plg.plugin_name,e)
def main():
    servers = {} #<-- server plugins
    settings = {}

    #PluginsLists:
    onLoadPlugins = []
    onNewEpisodePlugins = []
    onFinishPlugins = []

    dirPath = os.path.dirname(__file__)
    settingPath = os.path.join(dirPath, "settings.ini")
    readSettings(settingPath, settings)

    reloadPlugins(servers, onLoadPlugins, onNewEpisodePlugins, onFinishPlugins, settings)

    torLstPath = settings["torrents.list"]

    encoding = "cp1251"
    if settings.has_key("torrents.list_enc"):
        encoding = settings["torrents.list_enc"]

    torrentQueue = loadTorrentsList(torLstPath, encoding)
    newTorrentQueue = []

    processOnLoadPlugins(onLoadPlugins, torrentQueue, newTorrentQueue)

    if settings.has_key("proxy.active") and (settings["proxy.active"] == '1'):
        setProxy(settings["proxy.url"], settings["proxy.login"], settings["proxy.password"])

    for key in torrentQueue:

        (old_md5, descr) = key[2:]
        serv = key[0]
        torrID = key[1]

        #onServerPlugin
        ##---PROCESSING---
        if servers.has_key(key[0]) == False:
            print "No such server handler: serv_name=%s"%key[0]
            continue

        plug_list = servers[key[0]]
        if len(plug_list)>1:
            plugin = plug_list[1]
        else:
            plugin = plug_list[0](settings)
            plug_list.append(plugin)

        new_md5 = checkTorrentAndDownload(torrID, old_md5, settings[serv+'.saveas'], plugin)
        ##---END-PROCESSING---

        if new_md5 != old_md5: #onNewEpisode
            onNewEpisodeOccurred(onNewEpisodePlugins, torrID, descr, plugin.grabDescr, plugin)

        newTorrentQueue.append((serv, torrID, new_md5, descr))

    #onFinish
    processOnFinishPlugins(onFinishPlugins, torrentQueue, newTorrentQueue)

    saveTorrentsList(newTorrentQueue, torLstPath, encoding)
    pass

if __name__ == '__main__':
    main()
