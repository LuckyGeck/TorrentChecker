# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------
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
            self.active = settings[self.key('active')]
            self.msg = settings[self.key('msg')]
            self.token = settings[self.key('token')]
            self.username = settings[self.key('username')]
            self.chat_id = settings[self.key('chat_id')]
        except Exception as e:
            self.logError("Wrong settings file.", e)
            self.active = False

    def onNewEpisodeProcess(self, torrID, descr, pluginObj):
        if self.active:
            try:
                import telegram
                bot = telegram.Bot(token=self.token)
                url = pluginObj.getTopicURL(torrID)
                msg = self.msg % (descr, url)
                bot.sendMessage(chat_id=self.chat_id, text=msg)
            except Exception as e:
                self.logError("Some error in message sending.", e)


def echoChatID(bot, update, username):
    chat = update.message.chat
    if chat['username'] == username:
        update.message.reply_text('Your chat_id is "{}"'.format(chat['id']))
        exit(0)


def start_bot(token, username):
    from telegram.ext import Updater, Filters, CommandHandler
    updater = Updater(token)
    echoFunc = lambda b, u: echoChatID(b, u, username)
    handler = CommandHandler("torrents", echoFunc)
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
