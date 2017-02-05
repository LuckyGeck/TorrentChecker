# -*- coding: utf-8 -*-

# Author:       Sychev Pavel
# Created:      15.05.2012
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL

import base


class EmailNotify(base.OnNewTorrentPlugin, base.OnFinishPlugin):
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
    smtp_host = ''
    login = ''
    password = ''
    from_mail = ''
    to_mail = ''

    def __init__(self, settings):
        base.OnNewTorrentPlugin.__init__(self, settings)
        base.OnFinishPlugin.__init__(self, settings)
        smtp_settings = settings['smtp']
        self.smtp_host = smtp_settings['host']
        self.is_ssl = smtp_settings['ssl']
        self.is_tls = smtp_settings['tls']
        self.login = smtp_settings['login']
        self.password = smtp_settings['password']

        self.from_mail = settings['from_mail']
        self.to_mail = settings['to_mail']

    @staticmethod
    def get_plugin_name():
        return 'mailer'

    def on_new_torrent_process(self, torrent_id, description, plugin_obj):
        message = self.message_template.format(**locals())

        self.simple_body += message + '\n'
        full_description = plugin_obj.load_description(torrent_id)
        url = plugin_obj.get_topic_url(torrent_id)
        body = self.table_template.format(**locals()).encode('utf-8')
        self.mail_body += body

    def on_finish_process(self):
        if len(self.mail_body) == 0:
            self.log_debug('Nothing to send')
            return
        from plugins.utils import mailer
        full_body = mailer.build_table(self.mail_body)
        mailer.send_email(self.smtp_host, self.is_ssl, self.is_tls,
                          self.login, self.password, self.from_mail,
                          self.to_mail, full_body, self.simple_body)
        self.log_debug('Email sent')


if __name__ == '__main__':
    print "Email sender plugin"
