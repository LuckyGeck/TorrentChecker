# -*- coding: utf-8 -*-

# Author:       Sychev Pavel, Nikolay Volosatov
# Created:      18.03.2012
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL

import hashlib
import logging
from abc import ABCMeta, abstractmethod
from http.cookiejar import LWPCookieJar, FileCookieJar
from urllib.request import OpenerDirector, HTTPCookieProcessor, build_opener


class Torrent(object):
    """
    Representation of torrent state
    """

    def __init__(self):
        self.tracker = None  # type: str
        self.id = None  # type: str
        self.description = None  # type: str
        self.full_description = None  # type: str
        self.hash = None  # type: str

    @classmethod
    def load(cls, torrent_dict):
        # type: (dict) -> Torrent
        torrent = cls()
        torrent.__dict__.update(torrent_dict)
        return torrent

    def dump(self):
        # type: () -> dict
        return self.__dict__.copy()

    def copy(self):
        # type: () -> Torrent
        return self.load(self.dump())

    def update_hash_for_data(self, data):
        md5 = hashlib.md5()
        md5.update(data)
        self.hash = md5.hexdigest()

    def __str__(self):
        return '[{}.{}] {}'.format(self.tracker, self.id, self.description)


class BasePlugin(object):
    """
    Base class for all plugins
    """
    __metaclass__ = ABCMeta

    def __init__(self, settings):
        self.active = settings.get('active', False)
        self.debug = settings.get('debug', False)
        self._logger = logging.getLogger(self.get_plugin_name())

    def log_message(self, message, level=logging.INFO):
        self._logger.log(level, message)

    def log_debug(self, message):
        if self.debug:
            self.log_message(message, logging.DEBUG)

    def log_error(self, message, error):
        msg = "{}\n*** {} ***".format(message, error)
        self.log_message(msg, logging.WARNING)

    @staticmethod
    @abstractmethod
    def get_plugin_name():
        return ''


class ServerPlugin(BasePlugin):
    """
    Base class for torrent tracker integration plugins
    """

    def __init__(self, settings):
        BasePlugin.__init__(self, settings)
        auth_settings = settings.get('auth', dict())
        self.login = auth_settings.get('login')
        self.password = auth_settings.get('password')

        plugin_name = self.get_plugin_name()
        default_cookies_file = './{}.cookies.txt'.format(plugin_name)
        self.cookies_file = settings.get('cookies_file', default_cookies_file)

        self.opener = None  # type: OpenerDirector
        self.cookies = None  # type: FileCookieJar

    def __ensure_cookies_initialization(self):
        if self.cookies:
            return
        cookies = LWPCookieJar(self.cookies_file)
        try:
            cookies.load()
        except Exception as e:
            pass
        self.cookies = cookies

    def __ensure_opener_initialization(self):
        if self.opener:
            return
        cookies_processor = HTTPCookieProcessor(self.cookies)
        self.opener = build_opener(cookies_processor)

    def ensure_authorization(self):
        self.__ensure_cookies_initialization()
        self.__ensure_opener_initialization()
        if self.is_authorized(self.opener):
            return
        self.log_debug('Auth...')
        self.authorize(self.opener)
        if not self.is_authorized(self.opener):
            raise Exception('Not authorized')
        self.log_debug('Auth - ok!')
        self.cookies.save()

    @abstractmethod
    def can_process_torrent(self, torrent):
        # type: (Torrent) -> bool
        """
        Checks if the torrent can be processed by a current plugin.
        :param torrent: Torrent object
        :return: True if torrent can be processed by a current plugin
        """
        pass

    @abstractmethod
    def is_authorized(self, opener):
        # type: (OpenerDirector) -> bool
        """
        Checks authorization status (usually by trying to load resource not
        allowed for guests).
        :param opener: URL opener for network operations
        :return: True if authorised
        """
        return False

    @abstractmethod
    def authorize(self, opener):
        # type: (OpenerDirector) -> None
        """
        Authorizes on a torrent tracker.
        :param opener: URL opener for network operations
        """
        pass

    @abstractmethod
    def get_topic_url(self, torrent):
        # type: (Torrent) -> str
        """
        Returns absolute URL for a torrent(topic)
        :param torrent: Torrent object
        :return: URL string
        """
        pass

    @abstractmethod
    def load_description(self, torrent):
        # type: (Torrent) -> str
        """
        Loads a description for a given torrent (a title of a corresponding
        topic).
        :param torrent: Torrent object
        :return: Description string
        """
        pass

    @abstractmethod
    def load_torrent_data(self, torrent):
        # type: (Torrent) -> str
        """
        Loads a contents of a given torrent file from a remote server.
        :param torrent: Torrent object
        :return: Data of torrent file in string representation
        """
        pass

    @abstractmethod
    def find_torrents(self, query, category="new-movie"):
        """
        Returns torrents, that match a given query and are within a given
        category.
        :param query: Search string
        :param category: Category of torrent (see server plugins)
        :return Generator with matching torrent objects
        """
        pass


class OnStartPlugin(BasePlugin):

    @abstractmethod
    def on_start(self):
        """
        Does some preparations before the torrents' checking process.
        """
        pass


class OnNewTorrentPlugin(BasePlugin):

    @abstractmethod
    def on_new_torrent(self, torrent, plugin_obj):
        # type: (Torrent, ServerPlugin) -> None
        """
        Calls when new torrent downloaded.
        :param torrent: Torrent object
        :param plugin_obj: Server plugin that downloaded the torrent
        """
        pass


class OnFinishPlugin(BasePlugin):

    @abstractmethod
    def on_finish(self):
        """
        Does some cleanup after the main workflow has ended.
        """
        pass
