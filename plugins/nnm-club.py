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
    search_item_re = re.compile(r'<tr\s*class="prow\d+">'
                                r'.+?<a.*?class="gen"'
                                r'.*?>(?P<group>.*?)<\/a>'
                                r'.+?viewtopic\.php\?t=(?P<id>\d+)'
                                r'.+?<b>(?P<name>.*?)<\/b>'
                                r'.+?download\.php\?id=(?P<download_id>\d+)'
                                r'.+?<u>(?P<size>\d+)<\/u>'
                                r'.+?seedmed.+?<b>(?P<seeders>\d+)<\/b>.+?'
                                r'.+?tr>')
    filter_types = {
        'new-movie': [218, 270],
        'screen-movie': [217],
        '3d-movie': [888, 889, 891, 1211],
        'movie': [216, 270, 218, 219, 954, 266, 318, 320, 677, 1177, 319, 678,
                  885, 908, 909, 910, 911, 912, 220, 221, 222, 882, 224, 225,
                  226, 227, 682, 694, 884, 693, 913, 228, 1150, 254, 321, 255,
                  906, 256, 257, 258, 883, 955, 905, 271, 1210, 264, 265, 272,
                  1262],
        'show': [1219, 1221, 1220, 768, 779, 778, 788, 1288, 787, 1196, 1141,
                 777, 786, 803, 776, 785, 1265, 1289, 774, 775, 1242, 1140,
                 782, 773, 1142, 784, 1195, 772, 771, 783, 1144, 804, 1290,
                 770, 922, 780, 781, 769, 799, 800, 791, 798, 797, 790, 793,
                 794, 789, 796, 792, 795],
    }

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
        response_url = response.geturl()
        self.log_debug('Auth is {} == {}'.format(response_url, url))
        return response_url == url

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
        self.log_debug('Fetching download URL for {}'.format(torrent_id))
        topic_url = self.get_topic_url(torrent_id)
        data = self.opener.open(topic_url).read()
        download_url = re.search(r'download\.php\?id=[^"]*', data).group()
        self.log_debug('Loading torrent {}'.format(torrent_id))
        url = 'http://{}/forum/{}'.format(self.tracker_host, download_url)
        data = self.opener.open(url).read()
        self.log_debug('Torrent {} size: {}'.format(torrent_id, len(data)))
        return data

    def search_url(self, query, types):
        url_query = urllib.urlencode([
            ('nm', query),
            ('o', 10),
        ] + [('f[]', t) for t in types])
        url_template = 'http://{}/forum/tracker.php?{}'
        return url_template.format(self.tracker_host, url_query)

    def find_torrents(self, query, type="movie"):
        filter_types = self.filter_types.get(type)
        if not filter_types:
            return []
        self.ensure_authorization()
        url = self.search_url(query, filter_types)
        self.log_debug('Search URL: {}'.format(url))
        page_data = self.opener.open(url).read()
        page = page_data.decode('windows-1251', 'ignore').encode('utf8')
        page = str(page).replace('\n', '')
        torrents = []
        for match in self.search_item_re.finditer(page):
            torrent = match.groupdict()
            torrents.append(torrent)
        return torrents


if __name__ == '__main__':
    print 'NNM-Club Plugin'
