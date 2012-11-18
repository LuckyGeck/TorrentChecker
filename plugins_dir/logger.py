# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
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
    useJson = False # text repr by default
    logList = []

    def __init__(self, settings):
        try:
           self.active = (settings.has_key('%s.active'%self.plugin_name) and settings['%s.active'%self.plugin_name] == '1')
           self.useJson = (settings.has_key('%s.json_instead_of_text'%self.plugin_name) and settings['%s.json_instead_of_text'%self.plugin_name] == '1')
           self.logPath = settings['logger.saveas']
        except Exception as e:
            print u"[%s plugin] Wrong settings file!\t***%s***"%(self.plugin_name,e)
            self.active = False

    def onNewEpisodeProcess(self, torrID, descr, grabDescrFunction, pluginObj):
        if self.active:
            try:
                if self.useJson:
                    self.logList.append(
                        {
                            "time": int(time()),
                            "id": torrID,
                            "shortDescr": descr,
                            "fullDescr": grabDescrFunction(torrID),
                            "tracker": pluginObj.plugin_name
                        }
                    )
                else:
                    timeStr = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                    stroka = u'[%s] --- Updated [%s] %s\n'%(timeStr, torrID, descr.decode("cp1251"))
                    self.logList.append(stroka)
            except Exception as e:
                print u"[%s plugin] Error while adding to log!\n***%s***"%(self.plugin_name,e)
            

    def onFinishProcess(self, torrentQueue, newTorrentQueue):
        if self.logList and self.active:
            try:
                if self.useJson:
                    from json import dumps,loads
                    try:
                        oldLogContent = loads(codecs.open(self.logPath, 'r', 'utf-8').read())
                    except:
                        oldLogContent = []
                    newLogList = oldLogContent+self.logList
                    logText = dumps(newLogList, indent = 2, encoding="cp1251", ensure_ascii=False)
                    f = codecs.open(self.logPath, 'w', 'utf-8')
                    f.write(logText)
                    f.close()
                else:
                    f = codecs.open(self.logPath, 'a', "utf-8")
                    f.writelines(self.logList)
                    f.close()
            except Exception as e:
                print u'[%s plugin] Some error in log saving.\n*** %s ***'%(self.plugin_name,e)

if __name__ == '__main__':
    print "Logging plugin"
