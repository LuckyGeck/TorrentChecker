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
import urllib2
import urllib
import cookielib
import hashlib
import re


class NNMClub(base.ServerPlugin):
    post_params = ''
    tracker_host = 'nnmclub.to'

    def get_plugin_name(self):
        return 'nnm-club'

    def get_server_name(self):
        return self.get_plugin_name()

    def get_auth_params(self):
        return urllib.urlencode({
            'username': self.login,
            'password': self.password,
            'autologin': 'on',
            'redirect': '',
            'login': '%C2%F5%EE%E4'
        })

    def get_auth(self):
        login_page = 'http://{}/forum/login.php'.format(self.tracker_host)
        cookies = cookielib.MozillaCookieJar('./cookies.txt')
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
        opener.open(login_page, self.get_auth_params()).read()
        print('NNM-Club: auth - ok!')
        return opener

    def load_description(self, torrent_id):
        url = self.get_topic_url(torrent_id)
        data = self.opener.open(url, self.post_params).read()
        title_tag = re.search(r"<h1 style=.*", data).group()
        title = re.split(r"<[^>]*>", title_tag)[2]
        return title.decode("cp1251")

    def get_topic_url(self, torrent_id):
        return 'http://{}/forum/viewtopic.php?t={}'.format(
            self.tracker_host, torrent_id)

    def load_torrent(self, torrent_id):
        topic_url = self.get_topic_url(torrent_id)
        data = self.opener.open(topic_url, self.post_params).read()
        download_url = re.search(r'download\.php\?id=[^"]*', data).group()

        url = 'http://{}/forum/{}'.format(self.tracker_host, download_url)
        data = self.opener.open(url, self.post_params).read()
        md5 = hashlib.md5()
        md5.update(data)
        return md5.hexdigest(), data


if __name__ == '__main__':
    print 'NNM-Club Plugin'
