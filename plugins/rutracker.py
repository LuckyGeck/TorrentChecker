# -*- coding: utf-8 -*-

# Author:       Sychev Pavel
# Created:      28.02.2012
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL

import base
import urllib
import re


class RuTracker(base.ServerPlugin):
    tracker_host = 'rutracker.org'
    re_title = re.compile(r"<h1 class=[^>]*>\s*<a[^>]+>\s*(?P<name>.*)</a")
    re_tags = re.compile(r"<[^>].*?>")
    re_quot = re.compile(r"&quot;")

    @staticmethod
    def get_plugin_name():
        return 'rutracker'

    def get_server_name(self):
        return self.get_plugin_name()

    def get_auth_params(self):
        return urllib.urlencode({
            'login_username': self.login,
            'login_password': self.password,
            'login': '%E2%F5%EE%E4'
        })

    def is_authorized(self, opener):
        template = 'http://{}/forum/privmsg.php?folder=inbox'
        url = template.format(self.tracker_host)
        response = opener.open(url)
        response_url = response.geturl()
        self.log_debug('Auth is {} == {}'.format(response_url, url))
        return response_url == url

    def authorize(self, opener):
        login_url = 'http://{}/forum/login.php'.format(self.tracker_host)
        opener.open(login_url, self.get_auth_params()).read()

    def load_description(self, torrent_id):
        url = self.get_topic_url(torrent_id)
        data = self.opener.open(url).read()
        title = re.search(self.re_title, data).group("name")
        title = re.sub(self.re_tags, "", title)
        title = re.sub(self.re_quot, '"', title)
        return title.decode("cp1251")

    def get_topic_url(self, torrent_id):
        return 'http://{}/forum/viewtopic.php?t={}'.format(
            self.tracker_host, torrent_id)

    def load_torrent(self, torrent_id):
        self.ensure_authorization()
        self.log_debug('Loading torrent {}'.format(torrent_id))
        url = 'http://{}/forum/dl.php?t={}'.format(
            self.tracker_host, torrent_id)
        data = self.opener.open(url).read()
        self.log_debug('Torrent {} size: {}'.format(torrent_id, len(data)))
        return data


if __name__ == '__main__':
    print 'RuTracker Plugin'
