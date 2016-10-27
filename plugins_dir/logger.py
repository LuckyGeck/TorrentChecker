# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------
# Name:        Logging plugin
# Purpose:     Plugin for torrentChecker
#
# Author:      Sychev Pavel
#
# Created:     31.05.2012
# Copyright:   (c) Sychev Pavel 2012
# Licence:     GPL
#----------------------------

import base
from time import gmtime, strftime, time
import codecs


class logger(base.onNewEpisodePlugin, base.onFinishPlugin):
    plugin_name = 'logger'
    active = False
    logPath = 'logger.log'
    useJson = False  # text repr by default
    logList = []

    def __init__(self, settings):
        try:
            self.active = settings[self.key('active')]
            self.useJson = settings[self.key('json_instead_of_text')]
            self.logPath = settings[self.key('saveas')]
        except Exception as e:
            self.logError("Wrong settings file.", e)
            self.active = False

    def onNewEpisodeProcess(self, torrID, descr, pluginObj):
        if self.active:
            try:
                if self.useJson:
                    self.logList.append(
                        {
                            "time": int(time()),
                            "id": torrID,
                            "shortDescr": descr,
                            "fullDescr": pluginObj.grabDescr(torrID),
                            "url": pluginObj.getTopicURL(torrID),
                            "tracker": pluginObj.plugin_name
                        }
                    )
                else:
                    timeStr = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                    logLineTemplate = u'[{}] --- Updated [{}] {}\n'
                    logLine = logLineTemplate.format(timeStr, torrID, descr)
                    self.logList.append(logLine)
            except Exception as e:
                self.logError("Error while adding to log.", e)

    def onFinishProcess(self, torrentQueue, newTorrentQueue):
        if self.logList and self.active:
            try:
                if self.useJson:
                    from json import dumps, loads
                    try:
                        oldLogContent = loads(
                            codecs.open(self.logPath, 'r', 'utf-8').read())
                    except:
                        oldLogContent = []
                    newLogList = oldLogContent+self.logList
                    logText = dumps(newLogList, indent=2, encoding="cp1251",
                                    ensure_ascii=False)
                    f = codecs.open(self.logPath, 'w', 'utf-8')
                    f.write(logText)
                    f.close()
                else:
                    f = codecs.open(self.logPath, 'a', "utf-8")
                    f.writelines(self.logList)
                    f.close()
            except Exception as e:
                self.logError("Some error in log saving.", e)

if __name__ == '__main__':
    print "Logging plugin"
