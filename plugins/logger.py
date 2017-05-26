# -*- coding: utf-8 -*-

# Author:       Sychev Pavel
# Created:      31.05.2012
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL

from time import gmtime, strftime, time
import codecs

import base


class Logger(base.OnNewTorrentPlugin, base.OnFinishPlugin):

    def __init__(self, settings):
        base.OnNewTorrentPlugin.__init__(self, settings)
        base.OnFinishPlugin.__init__(self, settings)
        self.log_path = settings['save_as']
        self.use_json = settings['use_json']
        self.log_list = []

    @staticmethod
    def get_plugin_name():
        return 'logger'

    def on_new_torrent(self, torrent, plugin_obj):
        if self.use_json:
            self.log_list.append({
                "time": int(time()),
                "id": torrent.id,
                "shortDescr": torrent.description,
                "fullDescr": plugin_obj.load_description(torrent),
                "url": plugin_obj.get_topic_url(torrent),
                "tracker": plugin_obj.get_plugin_name()
            })
        else:
            time_str = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            template = u'[{}] --- Updated [{}] {}\n'
            log_line = template.format(
                time_str, torrent.id, torrent.description
            )
            self.log_list.append(log_line)

    def on_finish(self):
        if len(self.log_list) == 0:
            return
        if self.use_json:
            from json import dumps, loads
            old_log_content = []
            try:
                old_log_content = loads(
                    codecs.open(self.log_path, 'r', 'utf-8').read())
            except:
                pass
            new_log_list = old_log_content + self.log_list
            log_text = dumps(new_log_list, indent=2, ensure_ascii=False)
            f = codecs.open(self.log_path, 'w', 'utf-8')
            f.write(log_text)
            f.close()
        else:
            f = codecs.open(self.log_path, 'a', 'utf-8')
            f.writelines(self.log_list)
            f.close()

if __name__ == '__main__':
    print "Logging plugin"
