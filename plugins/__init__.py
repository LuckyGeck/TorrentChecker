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
        self.on_start_plugins = []
        self.on_new_torrent_plugins = []
        self.on_finish_plugins = []

    def _add(self, obj):
        if not obj.active:
            return
        # server plugin
        if issubclass(obj.__class__, self.base.ServerPlugin):
            server_name = obj.get_server_name()
            if not isinstance(server_name, type(())):
                server_name = [server_name]
            for name in server_name:
                self.servers[name] = obj
        else:
            # plugin after start
            if issubclass(obj.__class__, self.base.OnStartPlugin):
                self.on_start_plugins.append(obj)
            # plugins on new episode found
            if issubclass(obj.__class__, self.base.OnNewTorrentPlugin):
                self.on_new_torrent_plugins.append(obj)
            # server plugin
            if issubclass(obj.__class__, self.base.OnFinishPlugin):
                self.on_finish_plugins.append(obj)

    def load(self, settings):
        import inspect

        modules, self.base = _load_modules()
        self.servers = dict()
        self.on_start_plugins = []
        self.on_new_episode_plugins = []
        self.on_finish_plugins = []

        for module_obj in modules:
            for elem in dir(module_obj):
                try:
                    cls = getattr(module_obj, elem)
                    if inspect.isclass(cls) and \
                            issubclass(cls, self.base.BasePlugin):
                        plugin_name = cls.get_plugin_name()
                        plugin_settings = settings.get(plugin_name, dict())
                        obj = cls(plugin_settings)
                        self._add(obj)
                except Exception as e:
                    msg = "***Error while loading plugin [{}.{}]***\n{}"
                    print msg.format(module_obj, elem, e)

    def process_on_start(self):
        for plugin in self.on_start_plugins:
            try:
                plugin.on_start_process()
            except BaseException as e:
                plugin.log_error('Error while running on_load_process', e)

    def process_on_new_torrent(self, torrent_id, description, server_plugin):
        for plugin in self.on_new_torrent_plugins:
            try:
                plugin.on_new_torrent_process(torrent_id, description,
                                              server_plugin)
            except BaseException as e:
                plugin.log_error('Error while running on_new_torrent_process',
                                 e)

    def process_on_finish(self):
        for plugin in self.on_finish_plugins:
            try:
                plugin.on_finish_process()
            except BaseException as e:
                plugin.log_error('Error while running on_finish_process', e)


plugins = PluginsContainer()


if __name__ == '__main__':
    print "This module works as a bridge between torrent checker and plugins."
