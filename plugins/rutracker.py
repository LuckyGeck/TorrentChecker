# -*- coding: utf-8 -*-

# Author:       Sychev Pavel
# Created:      28.02.2012
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL

import re
import urllib

import base


class RuTrackerTorrent(base.Torrent):

    def __init__(self):
        base.Torrent.__init__(self)
        self.group = None  # type: str
        self.download_id = None  # type: str
        self.seeders = 0
        self.size = 0
        self.tracker = RuTracker.get_plugin_name()

    def __str__(self):
        return '[{}.{}] {}'.format(self.tracker, self.id,
                                   self.full_description)


class RuTracker(base.ServerPlugin):
    tracker_host = 'rutracker.org'
    re_title = re.compile(r"<h1 class=[^>]*>\s*<a[^>]+>\s*(?P<name>.*)</a")
    re_tags = re.compile(r"<[^>].*?>")
    re_quot = re.compile(r"&quot;")

    re_search_item = re.compile(r'<tr\s+class="tCenter'
                                r'.+?f=\d+">(?P<group>.+?)<\/a>'
                                r'.+?viewtopic.php\?t=(?P<id>\d+)'
                                r'[^>]+>(?P<full_description>.+?)<\/a>'
                                r'.+?tor-size.+?<u>(?P<size>\d+)<\/u>'
                                r'.+?seedmed[^>]+>(?P<seeders>\d+)<\/b>'
                                r'.+?<\/tr>')
    filter_types = {
        'new-movie': [2200],
        'screen-movie': [2200],
        '3d-movie': [352, 549, 1213, 2109, 514, 2097],
        'movie': [7, 187, 2090, 2221, 2091, 2092, 2093, 2200, 2540, 934, 505,
                  212, 2459, 1235, 185, 22, 941, 1666, 376, 124, 1543, 709,
                  1577, 511, 656, 93, 905, 1576, 101, 100, 572, 2220, 1670,
                  2198, 2199, 313, 2201, 312, 2339, 4, 2343, 930, 2365, 1900,
                  521, 2258, 208, 539, 209, 484, 822, 921, 922, 1247, 923, 924,
                  1991, 925, 1165, 1245, 928, 926, 1246, 1250, 927, 1248, 33,
                  281, 1386, 1387, 1388, 282, 599, 1105, 1389, 1391, 2491, 404,
                  1390, 1642, 893, 1478],
        'show': [9, 104, 1408, 1535, 91, 1356, 990, 856, 188, 310, 202, 935,
                 172, 805, 80, 119, 812, 175, 79, 123, 189, 842, 235, 242, 819,
                 1531, 721, 1102, 1120, 1214, 387, 1359, 271, 273, 743, 184,
                 194, 85, 1171, 1417, 1144, 595, 1288, 1605, 1694, 1690, 820,
                 625, 84, 623, 1798, 106, 166, 236, 1449, 507, 504, 536, 173,
                 918, 920, 203, 1243, 140, 636, 606, 776, 181, 1499, 81, 266,
                 252, 196, 372, 110, 193, 237, 265, 1117, 497, 121, 134, 195,
                 2366, 2401, 2390, 1669, 2391, 2392, 2407, 2393, 2370, 2394,
                 2408, 2395, 2396, 2397, 2398, 2399, 2400, 2402, 2403, 2404,
                 2405, 2406, 911, 1493, 1301, 704, 1940, 1574, 1539, 1500, 823,
                 1006, 877, 972, 781, 1300, 1803, 1298, 825, 1606, 1458, 1463,
                 1459, 1461, 718, 1498, 907, 992, 607, 594, 775, 534, 1462,
                 1678, 904, 1460, 816, 815, 325, 1457, 1692, 1540, 694, 1949,
                 1541, 1941, 1537, 2100, 717, 915, 1242, 2412, 1938, 2104,
                 1939, 2102, 2103],
    }

    @staticmethod
    def get_plugin_name():
        return 'rutracker'

    def can_process_torrent(self, torrent):
        return torrent.tracker == self.get_plugin_name()

    def is_authorized(self, opener):
        template = 'http://{}/forum/privmsg.php?folder=inbox'
        url = template.format(self.tracker_host)
        response = opener.open(url)
        response_url = response.geturl()
        self.log_debug('Auth is {} == {}'.format(response_url, url))
        return response_url == url

    def authorize(self, opener):
        login_url = 'http://{}/forum/login.php'.format(self.tracker_host)
        auth_params = urllib.urlencode({
            'login_username': self.login,
            'login_password': self.password,
            'login': '%E2%F5%EE%E4'
        })
        opener.open(login_url, auth_params).read()

    def load_description(self, torrent):
        url = self.get_topic_url(torrent)
        data = self.opener.open(url).read()
        title = re.search(self.re_title, data).group("name")
        title = re.sub(self.re_tags, "", title)
        title = re.sub(self.re_quot, '"', title)
        return title.decode("cp1251")

    def get_topic_url(self, torrent):
        return 'http://{}/forum/viewtopic.php?t={}'.format(
            self.tracker_host, torrent.id)

    def load_torrent_data(self, torrent):
        self.ensure_authorization()
        self.log_debug('Loading torrent {}'.format(torrent.id))
        url = 'http://{}/forum/dl.php?t={}'.format(
            self.tracker_host, torrent.id)
        data = self.opener.open(url).read()
        self.log_debug('Torrent {} size: {}'.format(torrent.id, len(data)))
        return data

    def __search_url(self, query, types):
        url_query = urllib.urlencode({
            'nm': query,
            'o': 10,
            's': 2,
            'f': ','.join(str(t) for t in types)
        })
        # Ordering is not working for wildcard queries at RuTracker :(
        url_template = 'http://{}/forum/tracker.php?{}'
        return url_template.format(self.tracker_host, url_query)

    def __load_page(self, query, category):
        filter_types = self.filter_types.get(category)
        if not filter_types:
            return []
        self.ensure_authorization()
        url = self.__search_url(query, filter_types)
        self.log_debug('Search URL: {}'.format(url))
        page_data = self.opener.open(url).read()
        page = page_data.decode('windows-1251', 'ignore').encode('utf8')
        page = str(page).replace('\n', '')
        return page

    def find_torrents(self, query, category="new-movie"):
        page = self.__load_page(query, category)
        for match in self.re_search_item.finditer(page):
            torrent_dict = match.groupdict()
            torrent = RuTrackerTorrent.load(torrent_dict)
            yield torrent


if __name__ == '__main__':
    print 'RuTracker Plugin'
