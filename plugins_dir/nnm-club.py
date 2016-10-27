# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------
# Name:        NNM-Club Grabber plugin
# Purpose:     Get new episodes of serials from NNM-Club.RU
#
# Author:      Sychev Pavel, Volosatov Nikolay
#
# Created:     18.03.2012
# Copyright:   (c) Sychev Pavel 2012
# Licence:     GPL
#----------------------------

import base
import urllib2
import urllib
import cookielib
import string
import hashlib
import os
import re


class nnmclub(base.serverPlugin):

    plugin_name = 'nnm-club'
    post_params = ''
    tracker_host = 'nnmclub.to'

    def buildPostParams(self):
        post_params = urllib.urlencode({
            'username': self.login,
            'password': self.password,
            'autologin': 'on',
            'redirect': '',
            'login': '%C2%F5%EE%E4'
        })
        return post_params

################# OVERDRIVEN METHODS #######################

    def getAuth(self):
        self.post_params = self.buildPostParams()
        loginPage = 'http://{}/forum/login.php'.format(self.tracker_host)

        c = cookielib.MozillaCookieJar('./cookies.txt')
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(c))
        opener.open(loginPage, self.post_params)
        data = opener.open(loginPage, self.post_params).read()
        print('NNM-Club: auth - ok!')
        return opener

    def grabDescr(self, torrID):  # we get full description (grab the page)
        url = self.getTopicURL(torrID)
        data = self.opener.open(url, self.post_params).read()
        first = re.search(r"<h1 style=.*", data).group()
        second = re.split(r"<[^>]*>", first)[2]
        return second.decode("cp1251")

    def getTopicURL(self, torrID):
        return 'http://{}/forum/viewtopic.php?t={}'.format(
            self.tracker_host, torrID)

    def getTorrent(self, torrID):
        url = 'http://{}/forum/viewtopic.php?t={}'.format(
            self.tracker_host, torrID)
        data = self.opener.open(url, self.post_params).read()
        downloadUrl = re.search(r'download\.php\?id=[^"]*', data).group()

        url = 'http://{}/forum/{}'.format(self.tracker_host, downloadUrl)
        data = self.opener.open(url, self.post_params).read()
        md5 = hashlib.md5()
        md5.update(data)
        return (md5.hexdigest(), data)

    def getServerName():
        return "nnm-club"

    getServerName = base.Callable(getServerName)


if __name__ == '__main__':
    print 'NNM-Club Plugin'
