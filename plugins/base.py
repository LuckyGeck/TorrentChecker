# -*- coding: utf-8 -*-


class BasePlugin:
    active = False

    def __init__(self, settings):
        self.active = settings.get(self.key('active'), '0') == '1'
        self.debug = settings.get(self.key('debug'), '0') == '1'

    def key(self, key_name):
        return "{}.{}".format(self.get_plugin_name(), key_name)

    def log_message(self, message):
        print "[{} plugin] {}".format(self.get_plugin_name(), message)

    def log_debug(self, message):
        if self.debug:
            self.log_message(message)

    def log_error(self, message, error):
        print "[{} plugin] {}\n*** {} ***".format(
            self.get_plugin_name(), message, error)

    def get_plugin_name(self):
        return ''


class ServerPlugin(BasePlugin):
    login = ''
    password = ''
    opener = None
    filename_template = '%s.torrent'

    def __init__(self, settings):
        BasePlugin.__init__(self, settings)
        self.login = settings.get(self.key('login'))
        self.password = settings.get(self.key('password'))
        self.filename_template = settings.get(self.key('saveas'))

    def get_server_name(self):
        pass

    def get_auth(self):
        return None

    def get_topic_url(self, torrent_id):
        pass

    def authorize(self):
        if not self.opener:
            self.opener = self.get_auth()

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
