# -*- coding: utf-8 -*-

# Author:       Sychev Pavel, Nikolay Volosatov
# Created:      18.03.2012
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL

import urllib2
import cookielib


class BasePlugin:
    active = False
    debug = False

    def __init__(self, settings):
        self.active = settings.get('active', False)
        self.debug = settings.get('debug', False)

    def log_message(self, message):
        print "[{} plugin] {}".format(self.get_plugin_name(), message)

    def log_debug(self, message):
        if self.debug:
            self.log_message(message)

    def log_error(self, message, error):
        print "[{} plugin] {}\n*** {} ***".format(
            self.get_plugin_name(), message, error)

    @staticmethod
    def get_plugin_name():
        return ''


class ServerPlugin(BasePlugin):
    login = ''
    password = ''
    opener = None
    filename_template = '{torrent_id}.torrent'

    def __init__(self, settings):
        BasePlugin.__init__(self, settings)
        auth_settings = settings.get('auth', dict())
        self.login = auth_settings.get('login')
        self.password = auth_settings.get('password')

        plugin_name = self.__class__.get_plugin_name()
        default_cookies_file = './{}.cookies.txt'.format(plugin_name)
        self.cookies_file = settings.get('cookies_file', default_cookies_file)

    def get_server_name(self):
        pass

    def is_authorized(self, opener):

        return False

    def authorize(self, opener):
        pass

    def get_topic_url(self, torrent_id):
        pass

    def init_opener(self):
        cookies = cookielib.LWPCookieJar(self.cookies_file)
        try:
            cookies.load()
        except Exception as e:
            pass
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
        if not self.is_authorized(opener):
            self.log_debug('Auth...')
            self.authorize(opener)
            if not self.is_authorized(opener):
                raise Exception('Not authorized')
            self.log_debug('Auth - ok!')
            cookies.save()
        return opener

    def ensure_authorization(self):
        if not self.opener:
            self.opener = self.init_opener()

    def load_description(self, torrent_id):
        pass

    def load_torrent(self, torrent_id):
        pass


class OnStartPlugin(BasePlugin):
    def on_start_process(self):
        raise NotImplementedError


class OnNewTorrentPlugin(BasePlugin):
    def on_new_torrent_process(self, torrent_id, description, plugin_obj):
        raise NotImplementedError


class OnFinishPlugin(BasePlugin):
    def on_finish_process(self):
        raise NotImplementedError
