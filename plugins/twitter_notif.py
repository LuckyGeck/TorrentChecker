# -*- coding: utf-8 -*-

# ----------------------------------------
# Name:        TwitterNotification plugin
# Purpose:
#
# Author:      Sychev Pavel
#
# Created:     15.05.2012
# Copyright:   (c) Sychev Pavel 2012
# Licence:     GPL
# ----------------------------------------

import base


class TwitterNotify(base.OnNewEpisodePlugin):
    msg = ''

    def __init__(self, settings):
        base.OnNewEpisodePlugin.__init__(self, settings)
        try:
            self.msg = settings[self.key('msg')]
        except Exception as e:
            self.log_error("Wrong settings file.", e)
            self.active = False

    def get_plugin_name(self):
        return 'twitter'

    def on_new_episode_process(self, torrent_id, description, plugin_obj):
        if self.active:
            try:
                import os
                message = self.msg % description
                os.system('ttytter -status="{}"'.format(message))
            except Exception as e:
                self.log_error("Some error in twit sending.", e)

if __name__ == '__main__':
    print 'TwitterNotification Plugin'
