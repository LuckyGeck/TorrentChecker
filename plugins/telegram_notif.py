# -*- coding: utf-8 -*-

# -----------------------------------------
# Name:        TelegramNotification plugin
# Purpose:
#
# Author:      Nikolay Volosatov
#
# Created:     27.10.2016
# Copyright:   (c) Nikolay Volosatov 2016
# Licence:     GPL
# -----------------------------------------

import base


class TelegramNotify(base.OnNewEpisodePlugin):
    msg = ''
    token = ''
    username = ''
    chat_id = 0

    def __init__(self, settings):
        base.OnNewEpisodePlugin.__init__(self, settings)
        try:
            self.msg = settings[self.key('msg')]
            self.token = settings[self.key('token')]
            self.username = settings[self.key('username')]
            self.chat_id = settings[self.key('chat_id')]
        except Exception as e:
            self.log_error("Wrong settings file.", e)
            self.active = False

    def get_plugin_name(self):
        return 'telegram'

    def on_new_episode_process(self, torrent_id, description, plugin_obj):
        if self.active:
            try:
                import telegram
                bot = telegram.Bot(token=self.token)
                url = plugin_obj.get_topic_url(torrent_id)
                msg = self.msg % (description, url)
                bot.sendMessage(chat_id=self.chat_id, text=msg)
            except Exception as e:
                self.log_error("Some error in message sending.", e)


def start_bot(token, username):
    from telegram.ext import Updater, CommandHandler
    updater = Updater(token)

    def echo(bot, update):
        chat = update.message.chat
        if chat['username'] == username:
            msg = 'Your chat_id is "{}"'.format(chat['id'])
            update.message.reply_text(msg)
            exit(0)
    handler = CommandHandler("torrents", echo)

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