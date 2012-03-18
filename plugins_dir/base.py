class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable

class baseplugin():
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
