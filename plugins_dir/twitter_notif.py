#-------------------------------------------------------------------------------
# Name:        TwitterNotification plugin
# Purpose:
#
# Author:      Sychev Pavel
#
# Created:     15.05.2012
# Copyright:   (c) Sychev Pavel 2012
# Licence:     GPL
#----------------------------

# -*- coding: utf-8 -*-

import base

class twitter_notif(base.onNewEpisodePlugin):
    plugin_name = 'twitter'
    active = False
    msg = ''

    def __init__(self, settings):
        try:
            self.active = (settings.has_key('%s.active'%self.plugin_name) and settings['%s.active'%self.plugin_name] == '1')
            self.msg = settings['%s.msg'%self.plugin_name]
        except:
            print "[%s plugin] Wrong settings file!"%self.plugin_name
            self.active = False

    def onNewEpisodeProcess(self, torrID, descr, grabDescrFunction, pluginObj):
        if self.active:
            try:
                import os
                os.system('ttytter -status="%s"'%(msg%descr))
            except:
                print '[%s plugin] Some error in twit sending.'%self.plugin_name
if __name__ == '__main__':
    print 'TwitterNotification PLugin'
