# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------
# Name:        RuTracker Grabber plugin
# Purpose:     Get new episodes of serials from RuTracker.ORG
#
# Author:      Sychev Pavel
#
# Created:     28.02.2012
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


class rutracker(base.serverPlugin):

    plugin_name = 'rutracker'
    post_params = ''
    tracker_host = 'rutracker.org'
    re_title = re.compile(r"<h1 class=[^>]*><a href[^>]*>(?P<name>.*)</a")
    re_tags = re.compile(r"<[^>].*?>")
    re_quot = re.compile(r"&quot;")

    def buildPostParams(self):
        post_params = urllib.urlencode({
            'login_username': self.login,
            'login_password': self.password,
            'login': '%C2%F5%EE%E4'
        })
        return post_params

################# OVERDRIVEN METHODS #######################

    def getAuth(self):
        self.post_params = self.buildPostParams()
        loginPage = 'http://login.{}/forum/login.php'.format(self.tracker_host)

        c = cookielib.MozillaCookieJar('./cookies.txt')
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(c))
        try:
            data = opener.open(loginPage, self.post_params).read()
            #f = open("./test.html", 'wb')
            # f.write(data)
            # f.close()
            print('Rutracker: auth - ok!')
        except Exception as e:
            print('Rutracker: auth - failed! [*** {} ***]'.format(e))
        return opener

    def grabDescr(self, torrID):  # we get full description (grab the page)
        url = u'http://{}/forum/viewtopic.php?t={}'.format(
            self.tracker_host, torrID)
        data = self.opener.open(url, self.post_params).read()
        title = re.search(self.re_title, data).group("name")
        title = re.sub(self.re_tags, "", title)
        title = re.sub(self.re_quot, '"', title)
        return title.decode("cp1251")

    def getTorrent(self, torrID):
        url = 'http://dl.{}/forum/dl.php?t={}'.format(
            self.tracker_host, torrID)
        data = self.opener.open(url, self.post_params).read()
        md5 = hashlib.md5()
        md5.update(data)
        return (md5.hexdigest(), data)

    def getServerName():
        return "rutracker"

    getServerName = base.Callable(getServerName)


if __name__ == '__main__':
    print 'Rutracker Plugin'
