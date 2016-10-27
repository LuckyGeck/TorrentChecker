# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------
# Name:        EmailNotification plugin
# Purpose:
#
# Author:      Sychev Pavel
#
# Created:     15.05.2012
# Copyright:   (c) Sychev Pavel 2012
# Licence:     GPL
#----------------------------

import base


class email_notif(base.onNewEpisodePlugin, base.onFinishPlugin):
    plugin_name = 'mailer'
    active = False

# Current mail bodies
    mail_body = ''
    simple_body = ''

# Table row
    table_template = u'''<tr>
    <td>Updated <b>{}</b></td>
    <td>{}</td>
    <td><a href="{}">{}</td>
    </tr>'''

# Credits
    fromMail = ''
    fromPassword = ''
    toMail = ''

    def __init__(self, settings):
        try:
            self.active = settings[self.key('active')] == '1'
            self.fromMail = settings[self.key('fromMail')]
            self.fromPassword = settings[self.key('fromPassword')]
            self.toMail = settings[self.key('toMail')]
        except Exception as e:
            self.logError("Wrong settings file.", e)
            self.active = False

    def onNewEpisodeProcess(self, torrID, descr, pluginObj):
        stroka = u'Updated [{}] {}'.format(torrID, descr)
        try:
            print stroka.encode("utf-8")
        except Exception as e:
            print "Updated [{}] ***encoding_error***".format(torrID)

        if self.active:
            self.simple_body = self.simple_body + \
                u'Updated {} [{}]\n'.format(torrID, descr)
            fullDscr = pluginObj.grabDescr(torrID)
            url = pluginObj.getTopicURL(torrID)
            self.mail_body = self.mail_body + \
                self.table_template.format(torrID, descr, url, fullDscr)

    def onFinishProcess(self, torrentQueue, newTorrentQueue):
        if self.mail_body != u'' and self.active:
            try:
                import mailer
                mailer.sendEmail(self.fromMail, self.fromPassword, self.toMail,
                                 mailer.build_table(self.mail_body),
                                 self.simple_body)
            except Exception as e:
                self.logError("Some error in mail sending.", e)

if __name__ == '__main__':
    print "Email sender plugin"
