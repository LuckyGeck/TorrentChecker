# -*- coding: utf-8 -*-

# Author:       Nikolay Volosatov
# Created:      27.10.2016
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL

import base


def rnd_str(str_len=6):
    import random
    import string
    digits = string.ascii_uppercase + string.digits
    return ''.join(random.choice(digits) for _ in range(str_len))


class TelegramNotify(base.OnNewTorrentPlugin):

    def __init__(self, settings):
        base.OnNewTorrentPlugin.__init__(self, settings)
        self.message_template = settings['message_template']
        self.token = settings['token']
        self.username = settings['username']
        self.chat_id = settings['chat_id']

    @staticmethod
    def get_plugin_name():
        return 'telegram'

    def on_new_torrent(self, torrent, plugin_obj):
        import telegram
        bot = telegram.Bot(token=self.token)
        url = plugin_obj.get_topic_url(torrent.id)
        randomized_url = '{}&rnd={}'.format(url, rnd_str())
        msg_args = torrent.dump()
        msg_args.update({
            "url": randomized_url,
        })
        msg = self.message_template.format(**msg_args)
        bot.sendMessage(chat_id=self.chat_id, text=msg)


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
