# -*- coding: utf-8 -*-

# Author:       Sychev Pavel, Volosatov Nikolay
# Created:      18.03.2012
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL

import base
import urllib
import re


class NNMClub(base.ServerPlugin):
    tracker_host = 'nnmclub.to'

    @staticmethod
    def get_plugin_name():
        return 'nnm-club'

    def get_server_name(self):
        return 'nnm-club', 'nnmclub'

    def get_auth_params(self):
        return urllib.urlencode({
            'username': self.login,
            'password': self.password,
            'autologin': 'on',
            'redirect': '',
            'login': '%C2%F5%EE%E4'
        })

    def is_authorized(self, opener):
        template = 'http://{}/forum/watched_topics.php'
        url = template.format(self.tracker_host)
        response = opener.open(url)
        return response.geturl() == url

    def authorize(self, opener):
        login_page = 'http://{}/forum/login.php'.format(self.tracker_host)
        opener.open(login_page, self.get_auth_params()).read()

    def load_description(self, torrent_id):
        url = self.get_topic_url(torrent_id)
        data = self.opener.open(url).read()
        title_tag = re.search(r"<h1 style=.*", data).group()
        title = re.split(r"<[^>]*>", title_tag)[2]
        return title.decode("cp1251")

    def get_topic_url(self, torrent_id):
        return 'http://{}/forum/viewtopic.php?t={}'.format(
            self.tracker_host, torrent_id)

    def load_torrent(self, torrent_id):
        self.ensure_authorization()
        self.log_debug('Loading torrent {}'.format(torrent_id))
        topic_url = self.get_topic_url(torrent_id)
        data = self.opener.open(topic_url).read()
        download_url = re.search(r'download\.php\?id=[^"]*', data).group()

        url = 'http://{}/forum/{}'.format(self.tracker_host, download_url)
        data = self.opener.open(url).read()
        return data


if __name__ == '__main__':
    print 'NNM-Club Plugin'
