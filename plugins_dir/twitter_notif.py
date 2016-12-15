# -*- coding: utf-8 -*-

#----------------------------------------
# Name:        TwitterNotification plugin
# Purpose:
#
# Author:      Sychev Pavel
#
# Created:     15.05.2012
# Copyright:   (c) Sychev Pavel 2012
# Licence:     GPL
#----------------------------------------

import base


class twitter_notif(base.onNewEpisodePlugin):
    plugin_name = 'twitter'
    active = False
    msg = ''

    def __init__(self, settings):
        try:
            self.active = settings[self.key('active')] == '1'
            self.msg = settings[self.key('msg')]
        except Exception as e:
            self.logError("Wrong settings file.", e)
            self.active = False

    def onNewEpisodeProcess(self, torrID, descr, pluginObj):
        if self.active:
            try:
                import os
                url = pluginObj.getTopicURL(torrID)
                message = self.msg % descr
                os.system('ttytter -status="{}"'.format(message))
            except Exception as e:
                self.logError("Some error in twit sending.", e)

if __name__ == '__main__':
    print 'TwitterNotification Plugin'
