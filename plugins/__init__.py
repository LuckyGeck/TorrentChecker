# -*- coding: utf-8 -*-


def _load_modules():
    import os
    import sys
    import imp
    modules = []
    plugins_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(plugins_dir)

    base = imp.load_source('base', os.path.join(plugins_dir, 'base.py'))
    for path in os.listdir(plugins_dir):
        filename, file_extension = os.path.splitext(path)
        if file_extension == '.py':
            full_path = os.path.join(plugins_dir, path)
            module_name = filename
            if module_name not in ["base", "__init__"]:
                module_obj = imp.load_source(module_name, full_path)
                modules.append(module_obj)
    return modules, base


class PluginsContainer:
    def __init__(self):
        self.base = None
        self.servers = dict()
        self.on_load_plugins = []
        self.on_new_episode_plugins = []
        self.on_finish_plugins = []

    def _add(self, obj):
        if obj.active:
            # server plugin
            if issubclass(obj.__class__, self.base.ServerPlugin):
                server_name = obj.get_server_name()
                if not isinstance(server_name, type(())):
                    server_name = [server_name]
                for name in server_name:
                    self.servers[name] = obj
            else:
                # plugin after load
                if issubclass(obj.__class__, self.base.OnLoadPlugin):
                    self.on_load_plugins.append(obj)
                # plugins on new episode found
                if issubclass(obj.__class__, self.base.OnNewEpisodePlugin):
                    self.on_new_episode_plugins.append(obj)
                # server plugin
                if issubclass(obj.__class__, self.base.OnFinishPlugin):
                    self.on_finish_plugins.append(obj)

    def load(self, settings):
        import inspect

        modules, self.base = _load_modules()
        self.servers = dict()
        self.on_load_plugins = []
        self.on_new_episode_plugins = []
        self.on_finish_plugins = []

        for module_obj in modules:
            try:
                for elem in dir(module_obj):
                    obj = getattr(module_obj, elem)
                    if inspect.isclass(obj) and \
                            issubclass(obj, self.base.BasePlugin):
                        obj = obj(settings)
                        self._add(obj)
            except Exception as e:
                msg = "***Error while loading plugin [{}]***\n{}"
                print msg.format(module_obj, e)

    def process_on_load_plugins(self):
        for plugin in self.on_load_plugins:
            try:
                plugin.on_load_process()
            except Exception as e:
                plugin.log_error('Error while running on_load_process', e)

    def process_on_new_episode_occurred(self,
                                        torrent_id, description,
                                        server_plugin):
        for plugin in self.on_new_episode_plugins:
            try:
                plugin.on_new_episode_process(torrent_id,
                                              description, server_plugin)
            except Exception as e:
                plugin.log_error('Error while running on_new_episode_process',
                                 e)

    def process_on_finish_plugins(self):
        for plugin in self.on_finish_plugins:
            try:
                plugin.on_finish_process()
            except Exception as e:
                plugin.log_error('Error while running on_finish_process', e)


plugins = PluginsContainer()


if __name__ == '__main__':
    print "This module works as a bridge between torrent checker and plugins."
