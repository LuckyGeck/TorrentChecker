# -*- coding: utf-8 -*-

# ---------------------------------------
# Name:        Logging plugin
# Purpose:     Plugin for torrentChecker
#
# Author:      Sychev Pavel
#
# Created:     31.05.2012
# Copyright:   (c) Sychev Pavel 2012
# Licence:     GPL
# ---------------------------------------

import base
from time import gmtime, strftime, time
import codecs


class Logger(base.OnNewEpisodePlugin, base.OnFinishPlugin):
    log_path = 'logger.log'
    use_json = False  # text repr by default
    log_list = []

    def __init__(self, settings):
        base.OnNewEpisodePlugin.__init__(self, settings)
        base.OnFinishPlugin.__init__(self, settings)
        try:
            self.log_path = settings[self.key('saveas')]
            self.use_json = settings[self.key('json_instead_of_text')]
        except Exception as e:
            self.log_error("Wrong settings file.", e)
            self.active = False

    def get_plugin_name(self):
        return 'logger'

    def on_new_episode_process(self, torrent_id, description, plugin_obj):
        if self.use_json:
            self.log_list.append({
                "time": int(time()),
                "id": torrent_id,
                "shortDescr": description,
                "fullDescr": plugin_obj.load_description(torrent_id),
                "url": plugin_obj.get_topic_url(torrent_id),
                "tracker": plugin_obj.get_plugin_name()
            })
        else:
            time_str = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            template = u'[{}] --- Updated [{}] {}\n'
            log_line = template.format(
                time_str, torrent_id, description
            )
            self.log_list.append(log_line)

    def on_finish_process(self):
        if self.log_list:
            if self.use_json:
                from json import dumps, loads
                old_log_content = []
                try:
                    old_log_content = loads(
                        codecs.open(self.log_path, 'r', 'utf-8').read())
                except:
                    pass
                new_log_list = old_log_content + self.log_list
                log_text = dumps(new_log_list, indent=2, encoding='cp1251',
                                 ensure_ascii=False)
                f = codecs.open(self.log_path, 'w', 'utf-8')
                f.write(log_text)
                f.close()
            else:
                f = codecs.open(self.log_path, 'a', 'utf-8')
                f.writelines(self.log_list)
                f.close()

if __name__ == '__main__':
    print "Logging plugin"
