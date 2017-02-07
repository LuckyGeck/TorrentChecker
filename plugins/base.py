# -*- coding: utf-8 -*-

# Author:       Sychev Pavel, Nikolay Volosatov
# Created:      18.03.2012
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL

import sys
from abc import ABCMeta, abstractmethod
import urllib2
import cookielib


class BasePlugin(object):
    __metaclass__ = ABCMeta

    def __init__(self, settings):
        self.active = settings.get('active', False)
        self.debug = settings.get('debug', False)

    def log_message(self, message, is_error=False):
        msg = "[{} plugin] {}\n".format(self.get_plugin_name(), message)
        if is_error:
            sys.stderr.write(msg)
        else:
            sys.stdout.write(msg)

    def log_debug(self, message):
        if self.debug:
            self.log_message('[debug] {}'.format(message), True)

    def log_error(self, message, error):
        msg = "{}\n*** {} ***".format(message, error)
        self.log_message(msg, True)

    @staticmethod
    @abstractmethod
    def get_plugin_name():
        return ''


class ServerPlugin(BasePlugin):

    def __init__(self, settings):
        BasePlugin.__init__(self, settings)
        auth_settings = settings.get('auth', dict())
        self.login = auth_settings.get('login')
        self.password = auth_settings.get('password')

        plugin_name = self.get_plugin_name()
        default_cookies_file = './{}.cookies.txt'.format(plugin_name)
        self.cookies_file = settings.get('cookies_file', default_cookies_file)

        self.opener = None
        self.cookies = None

    def ensure_cookies_initialization(self):
        if self.cookies:
            return
        cookies = cookielib.LWPCookieJar(self.cookies_file)
        try:
            cookies.load()
        except Exception as e:
            pass
        self.cookies = cookies

    def ensure_opener_initialization(self):
        if self.opener:
            return
        cookies_processor = urllib2.HTTPCookieProcessor(self.cookies)
        self.opener = urllib2.build_opener(cookies_processor)

    def ensure_authorization(self):
        self.ensure_cookies_initialization()
        self.ensure_opener_initialization()
        if self.is_authorized(self.opener):
            return
        self.log_debug('Auth...')
        self.authorize(self.opener)
        if not self.is_authorized(self.opener):
            raise Exception('Not authorized')
        self.log_debug('Auth - ok!')
        self.cookies.save()

    @abstractmethod
    def get_server_name(self):
        pass

    @abstractmethod
    def is_authorized(self, opener):
        return False

    @abstractmethod
    def authorize(self, opener):
        pass

    @abstractmethod
    def get_topic_url(self, torrent_id):
        pass

    @abstractmethod
    def load_description(self, torrent_id):
        pass

    @abstractmethod
    def load_torrent(self, torrent_id):
        pass

    @abstractmethod
    def find_torrents(self, query, type="movie"):
        pass


class OnStartPlugin(BasePlugin):

    @abstractmethod
    def on_start_process(self):
        raise NotImplementedError


class OnNewTorrentPlugin(BasePlugin):

    @abstractmethod
    def on_new_torrent_process(self, torrent_id, description, plugin_obj):
        raise NotImplementedError


class OnFinishPlugin(BasePlugin):

    @abstractmethod
    def on_finish_process(self):
        raise NotImplementedError
