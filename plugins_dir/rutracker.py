#-------------------------------------------------------------------------------
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

class rutracker(base.baseplugin):

    plugin_name = 'rutracker'
    post_params = ''

    def buildPostParams(self):
        post_params = urllib.urlencode({
        'login_username' : self.login,
        'login_password' : self.password,
        'login' : '%C2%F5%EE%E4'
        })
        return post_params

################# OVERDRIVEN METHODS #######################

    def getAuth(self):
        self.post_params = self.buildPostParams()
        loginPage='http://login.rutracker.org/forum/login.php'

        c = cookielib.MozillaCookieJar('./cookies.txt')
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(c))
        data = opener.open(loginPage, self.post_params).read()
        #f = open("./test.html", 'wb')
        #f.write(data)
        #f.close()
        print('Rutracker: auth - ok!')
        return opener

    def grabDescr(self, torrID): # we get full description (grab the page)
        url = 'http://rutracker.org/forum/viewtopic.php?t=%s'%torrID
        data = self.opener.open(url, self.post_params).read()
        first = re.search(r"<h1 class=.*", data).group()
        second = re.split(r"<[^>]*>", first)[2]
        return second

    def getTorrent(self, torrID):
        url = 'http://dl.rutracker.org/forum/dl.php?t=%s'%torrID
        data = self.opener.open(url, self.post_params).read()
        md5 = hashlib.md5()
        md5.update(data)
        return (md5.hexdigest(), data)

    def getServerName():
        return "rutracker"
    getServerName = base.Callable(getServerName)


if __name__ == '__main__':
    print 'Rutracker Plugin'
