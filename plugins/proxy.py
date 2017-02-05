# -*- coding: utf-8 -*-

# Author:       Sychev Pavel, Nikolay Volosatov
# Created:      22.01.2017
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL

import base


class Proxy(base.OnStartPlugin):

    def __init__(self, settings):
        base.OnStartPlugin.__init__(self, settings)
        self.url = settings['url']
        self.login = settings['login']
        self.password = settings['password']

    @staticmethod
    def get_plugin_name():
        return 'proxy'

    def on_start_process(self):
        import urllib2
        pass_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        pass_mgr.add_password(None, self.url, self.login, self.password)
        auth_info = urllib2.ProxyBasicAuthHandler(pass_mgr)
        proxy_support = urllib2.ProxyHandler({'http': self.url})

        opener = urllib2.build_opener(proxy_support, auth_info)
        urllib2.install_opener(opener)
