﻿# -*- coding: utf-8 -*-

# Author:       Sychev Pavel
# Created:      15.05.2012
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL

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
        import os
        url = plugin_obj.get_topic_url(torrent_id)
        message_args = {
            "description": description,
            "url": url,
        }
        message = self.message_template.format(**message_args)
        os.system('ttytter -status="{}"'.format(message))

if __name__ == '__main__':
    print 'TwitterNotification Plugin'
