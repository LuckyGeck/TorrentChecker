# -*- coding: utf-8 -*-

# --------------------------------------
# Name:        EmailNotification plugin
# Purpose:
#
# Author:      Sychev Pavel
#
# Created:     15.05.2012
# Copyright:   (c) Sychev Pavel 2012
# Licence:     GPL
# --------------------------------------

import base


class EmailNotify(base.OnNewEpisodePlugin, base.OnFinishPlugin):
    # Current mail bodies
    mail_body = ''
    simple_body = ''

    # Templates
    message_template = u'Updated [{torrent_id}] {description}'
    table_template = u'''<tr>
    <td>Updated <b>{torrent_id}</b></td>
    <td>{description}</td>
    <td><a href="{url}">{full_description}</td>
    </tr>'''

    # Credentials
    from_mail = ''
    from_password = ''
    to_mail = ''

    def __init__(self, settings):
        base.OnNewEpisodePlugin.__init__(self, settings)
        base.OnFinishPlugin.__init__(self, settings)
        try:
            self.from_mail = settings[self.key('fromMail')]
            self.from_password = settings[self.key('fromPassword')]
            self.to_mail = settings[self.key('toMail')]
        except Exception as e:
            self.log_error("Wrong settings file.", e)
            self.active = False

    def get_plugin_name(self):
        return 'mailer'

    def on_new_episode_process(self, torrent_id, description, plugin_obj):
        message = self.message_template.format(**locals())
        try:
            print message.encode("utf-8")
        except Exception as e:
            self.log_error("encoding_error", e)

        if self.active:
            self.simple_body += message + '\n'
            full_description = plugin_obj.grabDescr(torrent_id)
            url = plugin_obj.getTopicURL(torrent_id)
            self.mail_body += self.table_template.format(**locals())

    def on_finish_process(self, torrent_queue, new_torrent_queue):
        if self.active and self.mail_body != u'':
            try:
                import mailer
                mailer.send_email(self.from_mail, self.from_password,
                                  self.to_mail,
                                  mailer.build_table(self.mail_body),
                                  self.simple_body)
            except Exception as e:
                self.log_error("Some error in mail sending.", e)


if __name__ == '__main__':
    print "Email sender plugin"
