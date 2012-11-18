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
from time import gmtime, strftime
class logger(base.onNewEpisodePlugin, base.onFinishPlugin):
    plugin_name = 'logger'
    active = False
    logPath = 'logger.log'
    logList = []

    def __init__(self, settings):
        try:
           self.active = (settings.has_key('%s.active'%self.plugin_name) and settings['%s.active'%self.plugin_name] == '1')
           self.logPath = settings['logger.saveas']
        except Exception as e:
            print u"[%s plugin] Wrong settings file!\t***%s***"%(self.plugin_name,e)
            self.active = False

    def onNewEpisodeProcess(self, torrID, descr, grabDescrFunction, pluginObj):
        if self.active:
            try:
                timeStr = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                stroka = u'[%s] --- Updated [%s] %s\n'%(timeStr, torrID, descr.decode("cp1251"))
                self.logList.append(stroka)
            except Exception as e:
                print u"[%s plugin] Error while adding to log!\n***%s***"%(self.plugin_name,e)
            

    def onFinishProcess(self, torrentQueue, newTorrentQueue):
        if self.logList and self.active:
            try:
                from codecs import open
                f = open(self.logPath, 'a', "utf-8")
                f.writelines(self.logList)
                f.close()
            except Exception as e:
                print u'[%s plugin] Some error in log saving.\n*** %s ***'%(self.plugin_name,e)

if __name__ == '__main__':
    print "Logging plugin"
