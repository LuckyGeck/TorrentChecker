# -*- coding: utf-8 -*-

import os
import inspect
import plugins_dir.base
import sys
import imp
from inspect import isclass

def reloadPlugins(servers, onLoadPlugins, onNewEpisodePlugins, onFinishPlugins, settings):
    modules = []

    plugins_dir_str = "plugins_dir"

    for fname in os.listdir(plugins_dir_str):

            if fname.endswith (".py"):
                module_name = fname[: -3]

                if module_name != "base" and module_name != "__init__":
                    package_obj = __import__(plugins_dir_str+ "." +  module_name)
                    modules.append (module_name)

    for modulename in modules:
        module_obj = getattr (package_obj, modulename)

        for elem in dir (module_obj):
            obj = getattr (module_obj, elem)

            if inspect.isclass(obj):
                try:
                    if issubclass(obj, plugins_dir.base.serverPlugin): #server plugin
                        serverName = obj.getServerName()
                        if (type(serverName) == type(())):
                            for name in serverName:
                                servers[name] = [obj,]
                        else:
                            servers[serverName] = [obj,]
                    elif issubclass(obj, plugins_dir.base.abstractAdditionalPlugin):
                        obj = obj(settings)
                        if issubclass(obj.__class__, plugins_dir.base.onLoadPlugin): #plugin after load
                            onLoadPlugins.append(obj)
                        if issubclass(obj.__class__, plugins_dir.base.onNewEpisodePlugin): #plugins on new episode found
                            onNewEpisodePlugins.append(obj)
                        if issubclass(obj.__class__, plugins_dir.base.onFinishPlugin): #server plugin
                            onFinishPlugins.append(obj)
                except:
                    print "***Error while loading plugin [%s]***"%obj.plugin_name
    pass

if __name__ == '__main__':
    print "This modul works as a bridge between torrent checker and plugins(server handlers)."

