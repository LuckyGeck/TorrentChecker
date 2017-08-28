# -*- coding: utf-8 -*-

# Author:       Sychev Pavel, Nikolay Volosatov
# Created:      22.01.2017
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL
from urllib.request import HTTPPasswordMgrWithDefaultRealm, \
    ProxyBasicAuthHandler, ProxyHandler, build_opener, install_opener

from plugins import base


class Proxy(base.OnStartPlugin):

    def __init__(self, settings):
        base.OnStartPlugin.__init__(self, settings)
        self.url = settings['url']
        self.login = settings['login']
        self.password = settings['password']

    @staticmethod
    def get_plugin_name():
        return 'proxy'

    def on_start(self):
        pass_mgr = HTTPPasswordMgrWithDefaultRealm()
        pass_mgr.add_password(None, self.url, self.login, self.password)
        auth_info = ProxyBasicAuthHandler(pass_mgr)
        proxy_support = ProxyHandler({'http': self.url})

        opener = build_opener(proxy_support, auth_info)
        install_opener(opener)
