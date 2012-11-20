# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
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

## Current mail bodies
    mail_body = ''
    simple_body = ''

## Table row
    table_template = u'<tr><td>Updated <b>%s</b></td>\n<td>%s</td>\n<td>%s</td></tr>\n\n'

## Credits
    fromMail = ''
    fromPassword = ''
    toMail = ''

    def __init__(self, settings):
        try:
           self.active = (settings.has_key('%s.active'%self.plugin_name) and settings['%s.active'%self.plugin_name] == '1')
           self.fromMail = settings['mailer.fromMail']
           self.fromPassword = settings['mailer.fromPassword']
           self.toMail = settings['mailer.toMail']
        except:
            print u"[%s plugin] Wrong settings file!"%self.plugin_name
            self.active = False

    def onNewEpisodeProcess(self, torrID, descr, grabDescrFunction, pluginObj):
        stroka = u'Updated [%s] %s'%(torrID,descr)
        try:
            print stroka.encode("utf-8")
        except Exception as e:
            print "Updated [%s] ***encoding_error***"%torrID

        if self.active: 
            self.simple_body = self.simple_body + u'Updated %s [%s]\n'%(torrID, descr)
            fullDscr = grabDescrFunction(torrID)
            self.mail_body = self.mail_body + self.table_template%(torrID, descr, fullDscr)

    def onFinishProcess(self, torrentQueue, newTorrentQueue):
        if self.mail_body != u'' and self.active:
            try:
                import mailer
                mailer.sendEmail(self.fromMail, self.fromPassword, self.toMail, mailer.build_table(self.mail_body), self.simple_body)
            except Exception as e:
                print u'[%s plugin] Some error in mail sending.\n*** %s ***'%(self.plugin_name,e)

if __name__ == '__main__':
    print "Email sender plugin"
