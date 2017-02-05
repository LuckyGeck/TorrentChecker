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


class TwitterNotify(base.OnNewTorrentPlugin):
    message_template = ''

    def __init__(self, settings):
        base.OnNewTorrentPlugin.__init__(self, settings)
        self.message_template = settings['message_template']

    @staticmethod
    def get_plugin_name():
        return 'twitter'

    def on_new_torrent_process(self, torrent_id, description, plugin_obj):
        try:
            import os
            message = self.message_template % description
            os.system('ttytter -status="{}"'.format(message))
        except Exception as e:
            self.log_error("Some error in twit sending.", e)

if __name__ == '__main__':
    print 'TwitterNotification Plugin'
