# -*- coding: utf-8 -*-

# Author:       Nikolay Volosatov
# Created:      27.10.2016
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL

import asyncio

from plugins import base


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
        from telegram import Bot
        url = plugin_obj.get_topic_url(torrent)
        randomized_url = '{}&rnd={}'.format(url, rnd_str())
        msg_args = torrent.dump()
        msg_args.update({
            "url": randomized_url,
        })
        msg = self.message_template.format(**msg_args)

        async def _send():
            async with Bot(self.token) as bot:
                await bot.send_message(chat_id=self.chat_id, text=msg)

        asyncio.run(_send())


def start_bot(token, username):
    from telegram.ext import Application, CommandHandler

    async def echo(update, context):
        chat = update.message.chat
        if chat.username == username:
            msg = 'Your chat_id is "{}"'.format(chat.id)
            await update.message.reply_text(msg)

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("torrents", echo))
    print('Waiting for command "/torrents"...')
    app.run_polling()


def main():
    import sys
    token, username = None, None
    try:
        token = sys.argv[1]
        username = sys.argv[2]
    except:
        print('Usage: telegram_notif.py [token] [username]')
        exit(2)
    start_bot(token, username)


if __name__ == '__main__':
    main()
