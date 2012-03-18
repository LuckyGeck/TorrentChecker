import os
import inspect
import plugins_dir.base
import sys
import imp
from inspect import isclass

def reloadPlugins(servers):
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
                if issubclass(obj, plugins_dir.base.baseplugin):
                    serverName = obj.getServerName()
                    if (type(serverName) == type(())):
                        for name in serverName:
                            servers[name] = [obj,]
                    else:
                        servers[serverName] = [obj,]
    pass

if __name__ == '__main__':
    print "This modul works as a bridge between torrent checker and plugins(server handlers)."

