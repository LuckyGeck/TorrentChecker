# -*- coding: utf-8 -*-


class Callable:

    def __init__(self, anycallable):
        self.__call__ = anycallable


class serverPlugin():
    login = ''
    password = ''
    opener = ''
    plugin_name = ''

    def getServerName():
        pass

    getServerName = Callable(getServerName)

    def __init__(self, settings):
        self.login = settings[self.plugin_name+".login"]
        self.password = settings[self.plugin_name+".password"]
        self.opener = self.getAuth()
        pass

    def getAuth(self):
        pass

    def grabDescr(self, torrID):
        pass

    def getTorrent(self, torrID):
        pass

### ADDITIONAL PLUGINS ###


class abstractAdditionalPlugin():
    plugin_name = ''

    def __init__(self, settings):
        # just a stub
        # you can get your plugins settings, if needed
        pass

    def key(self, postfix):
        return self.plugin_name+".login"

    def logMessage(self, message):
        print "[{} plugin] {}".format(self.plugin_name, message)

    def logError(self, message, error):
        print "[{} plugin] {}\n*** {} ***".format(
            self.plugin_name, message, error)

    def getPluginName(self):
        return self.plugin_name


class onLoadPlugin(abstractAdditionalPlugin):

    def onLoadProcess(self, torrentQueue, newTorrentQueue):
        # here should be your work done
        raise NotImplementedError
        pass


class onNewEpisodePlugin(abstractAdditionalPlugin):

    def onNewEpisodeProcess(self, torrID, descr, grabDescrFunction, pluginObj):
        # here should be your work done
        raise NotImplementedError
        pass


class onFinishPlugin(abstractAdditionalPlugin):

    def onFinishProcess(self, torrentQueue, newTorrentQueue):
        # here should be your work done
        raise NotImplementedError
        pass
