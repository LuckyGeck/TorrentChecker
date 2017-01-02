# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# Name:        RuTracker Grabber plugin
# Purpose:     Get new episodes of serials from RuTracker.ORG
#
# Author:      Sychev Pavel
#
# Created:     28.02.2012
# Copyright:   (c) Sychev Pavel 2012
# Licence:     GPL
# -------------------------------------------------------------------------

import base
import urllib2
import urllib
import cookielib
import hashlib
import re


class RuTracker(base.ServerPlugin):

    post_params = ''
    tracker_host = 'rutracker.org'
    re_title = re.compile(r"<h1 class=[^>]*><a href[^>]*>(?P<name>.*)</a")
    re_tags = re.compile(r"<[^>].*?>")
    re_quot = re.compile(r"&quot;")

    def get_plugin_name(self):
        return 'rutracker'

    def get_server_name(self):
        return self.get_plugin_name()

    def get_auth_params(self):
        return urllib.urlencode({
            'login_username': self.login,
            'login_password': self.password,
            'login': '%C2%F5%EE%E4'
        })

    def get_auth(self):
        loginPage = 'http://login.{}/forum/login.php'.format(self.tracker_host)
        cookies = cookielib.MozillaCookieJar('./cookies.txt')
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
        opener.open(loginPage, self.get_auth_params()).read()
        print('Rutracker: auth - ok!')
        return opener

    def load_description(self, torrent_id):
        url = self.get_topic_url(torrent_id)
        data = self.opener.open(url, self.post_params).read()
        title = re.search(self.re_title, data).group("name")
        title = re.sub(self.re_tags, "", title)
        title = re.sub(self.re_quot, '"', title)
        return title.decode("cp1251")

    def get_topic_url(self, torrent_id):
        return u'http://{}/forum/viewtopic.php?t={}'.format(
            self.tracker_host, torrent_id)

    def load_torrent(self, torrent_id):
        url = 'http://dl.{}/forum/dl.php?t={}'.format(
            self.tracker_host, torrent_id)
        data = self.opener.open(url, self.post_params).read()
        md5 = hashlib.md5()
        md5.update(data)
        return md5.hexdigest(), data


if __name__ == '__main__':
    print 'RuTracker Plugin'
