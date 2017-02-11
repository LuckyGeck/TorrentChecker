# -*- coding: utf-8 -*-

# Author:       Sychev Pavel, Nikolay Volosatov
# Created:      18.03.2012
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL

import sys
from abc import ABCMeta, abstractmethod
import urllib2
import cookielib


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
        import hashlib
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

        self.opener = None  # type: urllib2.OpenerDirector
        self.cookies = None  # type: cookielib.FileCookieJar

    def __ensure_cookies_initialization(self):
        if self.cookies:
            return
        cookies = cookielib.LWPCookieJar(self.cookies_file)
        try:
            cookies.load()
        except Exception as e:
            pass
        self.cookies = cookies

    def __ensure_opener_initialization(self):
        if self.opener:
            return
        cookies_processor = urllib2.HTTPCookieProcessor(self.cookies)
        self.opener = urllib2.build_opener(cookies_processor)

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
        Check if torrent could be processed with this plugin
        :param torrent: Torrent object
        :return: True if torrent could be processed with this plugin
        """
        pass

    @abstractmethod
    def is_authorized(self, opener):
        # type: (urllib2.OpenerDirector) -> bool
        """
        Check authorization status(usually by trying to load resource not
        allowed for guests)
        :param opener: URL opener for network operations
        :return: True if authorised
        """
        return False

    @abstractmethod
    def authorize(self, opener):
        # type: (urllib2.OpenerDirector) -> None
        """
        Perform authorization at torrent tracker
        :param opener: URL opener for network operations
        """
        pass

    @abstractmethod
    def get_topic_url(self, torrent):
        # type: (Torrent) -> str
        """
        Return absolute URL of torrent(topic)
        :param torrent: Torrent object
        :return: URL string
        """
        pass

    @abstractmethod
    def load_description(self, torrent):
        # type: (Torrent) -> str
        """
        Load torrent description(title of a topic)
        :param torrent: Torrent object
        :return: Description string
        """
        pass

    @abstractmethod
    def load_torrent_data(self, torrent):
        # type: (Torrent) -> str
        """
        Load torrent file
        :param torrent: Torrent object
        :return: Data of torrent file in string representation and
            updated torrent state object
        """
        pass

    @abstractmethod
    def find_torrents(self, query, category="new-movie"):
        """
        Return torrents matching query and with specific type.
        :param query: Query string for search
        :param category: Category of torrent (see server plugins)
        :return Generator with matching torrent objects
        """
        pass


class OnStartPlugin(BasePlugin):
    """
    Base class for plugins that implement on-start logic like
    something that is should be done before torrents checking process.
    """

    @abstractmethod
    def on_start_process(self):
        """
        Called in the beginning of main process.
        """
        pass


class OnNewTorrentPlugin(BasePlugin):
    """
    Base class for plugins that handle a fact of new torrents downloading.
    """

    @abstractmethod
    def on_new_torrent_process(self, torrent, plugin_obj):
        # type: (Torrent, ServerPlugin) -> None
        """
        Called when new torrent downloaded.
        :param torrent: Torrent object
        :param plugin_obj: Server plugin that downloaded the torrent
        :type plugin_obj: ServerPlugin
        """
        pass


class OnFinishPlugin(BasePlugin):
    """
    Base class for plugins that have something to do in the end.
    """

    @abstractmethod
    def on_finish_process(self):
        """
        Called in the end of the main process.
        """
        pass
