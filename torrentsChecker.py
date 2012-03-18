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
#!/usr/bin/env python
import string
import os
import sys
import imp
from plugins import *
from inspect import isclass

mail_body = ''
simple_body = ''

servers = {}
settings = {}

def readSettings(path):
    global settings
    fileSettings = open(path, 'r')
    info = fileSettings.readline()
    while (info != ''):
        if string.strip(info) == '':
            info = fileSettings.readline()
            continue
        (first,second) = string.split(string.strip(info), '=', 2)
        settings[first] = second
        info = fileSettings.readline()
    # (login,password) = string.split(s, ':')
    fileSettings.close()
    pass

def checkTorrentAndDownload(torrID, lastmd5, fileDir, plugin):
    fileName = fileDir%torrID
    (md5,data) = plugin.getTorrent(torrID)
    if md5 != lastmd5 :
        f = open(fileName, 'wb')
        f.write(data)
        f.close()
        return md5
    return lastmd5
    pass

def loadTorrentsList(path):
    fileT = open(path, 'r')
    retList = []
    torLines = fileT.readlines()
    for s in torLines:
        s = s.strip()
        t = s.split(':',3)
        try:
            retList.append(t)
        except:
            pass
            #retList.append(t[0], t[1], '', '')
    fileT.close()
    return retList

def saveTorrentsList(torrentQueue, torLstPath):
    f = open(torLstPath, 'w')
    for key in torrentQueue:
        f.write('%s:%s:%s:%s\r\n'%key)
    f.close()
    pass

def log(str, path):
    f = open(path, 'a')
    f.write(str)
    f.close()

def addToEmail(torrID, descr, fullDescr=''):
    print('Updated ['+torrID+'] %s'%descr)
    global mail_body
    global simple_body
    simple_body = simple_body + 'Updated '+torrID+'['+descr+']\n'
    mail_body = mail_body + '<tr><td>Updated <b>'+torrID+'</b></td>\n<td>'+descr + '</td>\n<td>'+fullDescr+'</td></tr>\n\n'
    pass

def setProxy(url, login, password):
    passmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passmgr.add_password(None, url , login, password)
    authinfo = urllib2.ProxyBasicAuthHandler(passmgr)
    proxy_support = urllib2.ProxyHandler({'http' : url})

    opener = urllib2.build_opener(proxy_support, authinfo)
    urllib2.install_opener(opener)

def main():
    global servers
    global settings

    reloadPlugins(servers)
    dirPath = os.path.dirname(__file__)
    settingPath = os.path.join(dirPath, "settings.ini")
    readSettings(settingPath)

    torLstPath = settings["torrents.list"]

    if settings.has_key("proxy.active") and (settings["proxy.active"] == '1'):
        setProxy(settings["proxy.url"], settings["proxy.login"], settings["proxy.password"])

    torrentQueue = loadTorrentsList(torLstPath)
    newTorrentQueue = []
    for key in torrentQueue:

        (old_md5, descr) = key[2:]
        serv = key[0]
        torrID = key[1]

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
        if new_md5 != old_md5:
            addToEmail(torrID, descr, plugin.grabDescr(torrID))
            if settings.has_key('twitter.active') and settings['twitter.active'] == '1':
                os.system('ttytter -status="'+settings['twitter.msg']%descr + '"')

        newTorrentQueue.append((serv, torrID, new_md5, descr))

    saveTorrentsList(newTorrentQueue, torLstPath)

    if settings.has_key('mailer.active') and settings['mailer.active'] == '1':
        if mail_body != '':
            import mailer
            mailer.sendEmail(settings['mailer.fromMail'], settings['mailer.fromPassword'], settings['mailer.toMail'], mailer.build_table(mail_body), simple_body)
    pass

if __name__ == '__main__':
    main()
