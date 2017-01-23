# -*- coding: utf-8 -*-

# ----------------------------------------------------------
# Name:        NNM-Club Grabber plugin
# Purpose:     Get new episodes of serials from NNM-Club.RU
#
# Author:      Sychev Pavel, Volosatov Nikolay
#
# Created:     18.03.2012
# Copyright:   (c) Sychev Pavel 2012
# Licence:     GPL
# ----------------------------------------------------------

import base


class Proxy(base.OnStartPlugin):

    def __init__(self, settings):
        base.OnStartPlugin.__init__(self, settings)
        self.url = settings[self.key('url')]
        self.login = settings[self.key('login')]
        self.password = settings[self.key('password')]

    def get_plugin_name(self):
        return 'proxy'

    def on_start_process(self):
        import urllib2
        pass_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        pass_mgr.add_password(None, self.url, self.login, self.password)
        auth_info = urllib2.ProxyBasicAuthHandler(pass_mgr)
        proxy_support = urllib2.ProxyHandler({'http': self.url})

        opener = urllib2.build_opener(proxy_support, auth_info)
        urllib2.install_opener(opener)
