# -*- coding: utf-8 -*-

import os
import sys


def reload_plugins(servers, on_load_plugins, on_new_episode_plugins,
                   on_finish_plugins, settings):
    import imp
    import inspect
    modules = []

    plugins_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(plugins_dir)

    base = imp.load_source('base', os.path.join(plugins_dir, 'base.py'))
    for file_name in os.listdir(plugins_dir):
        if file_name.endswith(".py"):
            file_path = os.path.join(plugins_dir, file_name)
            module_name = file_name[: -3]
            if module_name != "base" and module_name != "__init__":
                module_obj = imp.load_source(module_name, file_path)
                modules.append(module_obj)

    for module_obj in modules:
        for elem in dir(module_obj):
            obj = getattr(module_obj, elem)
            if inspect.isclass(obj):
                try:
                    obj = obj(settings)
                    # server plugin
                    if issubclass(obj.__class__, base.ServerPlugin):
                        server_name = obj.get_server_name()
                        if isinstance(server_name, type(())):
                            for name in server_name:
                                servers[name] = obj
                        else:
                            servers[server_name] = obj
                    else:
                        # plugin after load
                        if issubclass(obj.__class__, base.OnLoadPlugin):
                            on_load_plugins.append(obj)
                        # plugins on new episode found
                        if issubclass(obj.__class__, base.OnNewEpisodePlugin):
                            on_new_episode_plugins.append(obj)
                        # server plugin
                        if issubclass(obj.__class__, base.OnFinishPlugin):
                            on_finish_plugins.append(obj)
                except Exception as e:
                    msg = "***Error while loading plugin [{}]***\n{}"
                    print msg.format(obj.get_plugin_name(), e)

if __name__ == '__main__':
    print "This module works as a bridge between torrent checker and plugins."
