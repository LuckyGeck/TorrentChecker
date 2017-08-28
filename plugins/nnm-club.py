# -*- coding: utf-8 -*-

# Author:       Sychev Pavel, Volosatov Nikolay
# Created:      18.03.2012
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL

import re
from urllib.parse import urlencode

from plugins import base


class NNMClubTorrent(base.Torrent):

    def __init__(self):
        base.Torrent.__init__(self)
        self.group = None  # type: str
        self.download_id = None  # type: str
        self.seeders = 0
        self.size = 0
        self.tracker = NNMClub.get_plugin_name()

    def __str__(self):
        return '[{}.{}] {}'.format(self.tracker, self.id,
                                   self.full_description)


class NNMClub(base.ServerPlugin):
    tracker_host = 'nnm-club.name'
    tracker_encoding = "cp1251"
    re_search_item = re.compile(r'<tr\s*class="prow\d+">'
                                r'.+?<a.*?class="gen"'
                                r'.*?>(?P<group>.*?)<\/a>'
                                r'.+?viewtopic\.php\?t=(?P<id>\d+)'
                                r'.+?<b>(?P<full_description>.*?)<\/b>'
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

    def can_process_torrent(self, torrent):
        return torrent.tracker == self.get_plugin_name()

    def is_authorized(self, opener):
        template = 'http://{}/forum/watched_topics.php'
        url = template.format(self.tracker_host)
        response = opener.open(url)
        response_url = response.geturl()
        self.log_debug('Auth is {} == {}'.format(response_url, url))
        return response_url == url

    def authorize(self, opener):
        login_page = 'http://{}/forum/login.php'.format(self.tracker_host)
        auth_params = urlencode({
            'username': self.login,
            'password': self.password,
            'autologin': 'on',
            'redirect': '',
            'login': '%C2%F5%EE%E4'
        }).encode()
        opener.open(login_page, auth_params).read()

    def load_description(self, torrent):
        url = self.get_topic_url(torrent)
        data = self.opener.open(url).read().decode(self.tracker_encoding)
        title_tag = re.search(r"<h1 style=.*", data).group()
        title = re.split(r"<[^>]*>", title_tag)[2]
        return title

    def get_topic_url(self, torrent):
        return 'http://{}/forum/viewtopic.php?t={}'.format(
            self.tracker_host, torrent.id)

    def load_torrent_data(self, torrent):
        self.ensure_authorization()
        download_id = None
        if issubclass(torrent.__class__, NNMClubTorrent):
            download_id = torrent.download_id
        if not download_id:
            self.log_debug('Fetching download ID for {}'.format(torrent.id))
            topic_url = self.get_topic_url(torrent)
            data = self.opener.open(topic_url).read()\
                .decode(self.tracker_encoding)
            match = re.search(r'download\.php\?id=(?P<id>[^"]*)', data)
            if match:
                download_id = match.groupdict()["id"]
        if not download_id:
            self.log_debug('Download ID not found')
            return None
        self.log_debug('Loading torrent {}'.format(torrent.id))
        url_template = 'http://{}/forum/download.php?id={}'
        url = url_template.format(self.tracker_host, download_id)
        data = self.opener.open(url).read()
        self.log_debug('Torrent {} size: {}'.format(torrent.id, len(data)))
        return data

    def __search_url(self, query, types):
        url_query = urlencode([
            ('nm', query),
            ('o', 10),
        ] + [('f[]', t) for t in types])
        url_template = 'http://{}/forum/tracker.php?{}'
        return url_template.format(self.tracker_host, url_query)

    def __load_search_page(self, query, category):
        filter_types = self.filter_types.get(category)
        if not filter_types:
            msg_template = 'Unknown category: {} not in {}'
            self.log_debug(msg_template.format(category,
                                               self.filter_types.keys()))
            return ''
        self.ensure_authorization()
        url = self.__search_url(query, filter_types)
        self.log_debug('Search URL: {}'.format(url))
        page_data = self.opener.open(url).read()
        page = page_data.decode(self.tracker_encoding, 'ignore')
        page = page.replace('\n', ' ')
        return page

    def find_torrents(self, query, category="new-movie"):
        page = self.__load_search_page(query, category)
        for match in self.re_search_item.finditer(page):
            torrent_dict = match.groupdict()
            torrent = NNMClubTorrent.load(torrent_dict)
            yield torrent


if __name__ == '__main__':
    print('NNM-Club Plugin')
