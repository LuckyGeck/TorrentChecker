# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:        TelegramNotification plugin
# Purpose:
#
# Author:      Nikolay Volosatov
#
# Created:     27.10.2016
# Copyright:   (c) Nikolay Volosatov 2016
# Licence:     GPL
#----------------------------

import base

class telegram_notif(base.onNewEpisodePlugin):
    plugin_name = 'telegram'
    active = False
    msg = ''
    token = ''
    username = ''
    chat_id = 0

    def __init__(self, settings):
        try:
            self.active = settings.get('%s.active'%self.plugin_name, '0') == '1'
            self.msg = settings['%s.msg'%self.plugin_name]
            self.token = settings['%s.token'%self.plugin_name]
            self.username = settings['%s.username'%self.plugin_name]
            self.chat_id = settings['%s.chat_id'%self.plugin_name]
        except:
            print "[%s plugin] Wrong settings file!"%self.plugin_name
            self.active = False

    def onNewEpisodeProcess(self, torrID, descr, grabDescrFunction, pluginObj):
        if self.active:
            try:
                import telegram
                bot = telegram.Bot(token=self.token)
                bot.sendMessage(chat_id=self.chat_id, text=self.msg%descr)
            except:
                print '[%s plugin] Some error in twit sending.'%self.plugin_name

def echoChatID(bot, update, username):
    chat = update.message.chat
    if chat['username'] == username:
        update.message.reply_text('Your chat_id is "%s"'%chat['id'])
        exit(0)

def start_bot(token, username):
    from telegram.ext import Updater, Filters, CommandHandler
    updater = Updater(token)
    handler = CommandHandler("torrents", lambda b,u: echoChatID(b,u,username))
    updater.dispatcher.add_handler(handler)
    updater.start_polling()
    print('Waiting for command "/torrents"...')
    updater.idle()

def main():
    import sys
    token, username = None, None
    try:
        token = sys.argv[1]
        username = sys.argv[2]
    except:
        print 'Usage: telegram_notif.py [token] [username]'
        exit(2)
    start_bot(token, username)

if __name__ == '__main__':
    main()
