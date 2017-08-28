# -*- coding: utf-8 -*-

# Author:       Nikolay Volosatov
# Created:      03.01.2017
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL
import logging

from plugins.base import BasePlugin, ServerPlugin, OnStartPlugin, Torrent, \
    OnNewTorrentPlugin, OnFinishPlugin


logger = logging.getLogger(__name__)


def _load_modules():
    import os
    import sys
    import importlib.util
    modules = []
    plugins_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(plugins_dir)

    for path in os.listdir(plugins_dir):
        filename, file_extension = os.path.splitext(path)
        if file_extension == '.py':
            full_path = os.path.join(plugins_dir, path)
            module_name = filename
            if module_name not in ["base", "__init__"]:
                spec = importlib.util.spec_from_file_location(module_name,
                                                              full_path)
                module_obj = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module_obj)
                modules.append(module_obj)
    return modules


class PluginsContainer:
    def __init__(self):
        self.__all_plugins = dict()

    def load(self, settings):
        import inspect

        modules = _load_modules()
        self.__all_plugins = dict()

        for module_obj in modules:
            for elem in dir(module_obj):
                try:
                    cls = getattr(module_obj, elem)
                    if inspect.isclass(cls) and \
                            issubclass(cls, BasePlugin):
                        plugin_name = cls.get_plugin_name()
                        plugin_settings = settings.get(plugin_name, dict())
                        obj = cls(plugin_settings)
                        self.__all_plugins[plugin_name] = obj
                except Exception as e:
                    msg = "***Error while loading plugin [{}.{}]***\n{}"
                    logger.warning(msg.format(module_obj, elem, e))

    def __plugins_of_type(self, base_class):
        for plugin_name, plugin in self.__all_plugins.items():
            if plugin.active and issubclass(plugin.__class__, base_class):
                yield plugin_name, plugin

    def get_server(self, server_name):
        # type: (str) -> ServerPlugin
        """
        Returns a corresponding server plugin for a given 'server_name'.
        :param server_name: Server plugin name
        :return: Server plugin object
        """
        plugin = self.__all_plugins.get(server_name)
        is_server = issubclass(plugin.__class__, ServerPlugin)
        if plugin.active and is_server:
            return plugin

    def get_server_for_torrent(self, torrent):
        # type: (base.Torrent) -> ServerPlugin
        """
        Returns a server plugin that can process a given torrent.
        :param torrent: Torrent object
        :return: Server plugin object
        """
        server_plugins = self.__plugins_of_type(ServerPlugin)
        for plugin_name, plugin in server_plugins:
            if plugin.can_process_torrent(torrent):
                return plugin

    def process_on_start(self):
        """
        Triggers 'on_start' for all registered plugins.
        """
        on_start_plugins = self.__plugins_of_type(OnStartPlugin)
        for plugin_name, plugin in on_start_plugins:
            try:
                plugin.on_start()
            except BaseException as e:
                plugin.log_error('Error while running on_start_process', e)

    def process_on_new_torrent(self, torrent, server_plugin):
        # type: (Torrent, ServerPlugin) -> None
        """
        Triggers 'on_new_torrent' for all registered plugins.
        :param torrent: Torrent object
        :param server_plugin: Plugin that downloaded the torrent
        """
        on_new_plugins = self.__plugins_of_type(OnNewTorrentPlugin)
        for plugin_name, plugin in on_new_plugins:
            try:
                plugin.on_new_torrent(torrent, server_plugin)
            except BaseException as e:
                plugin.log_error('Error while running on_new_torrent_process',
                                 e)

    def process_on_finish(self):
        """
        Triggers 'on_finish' for all registered plugins.
        """
        on_finish_plugins = self.__plugins_of_type(OnFinishPlugin)
        for plugin_name, plugin in on_finish_plugins:
            try:
                plugin.on_finish()
            except BaseException as e:
                plugin.log_error('Error while running on_finish_process', e)


plugins = PluginsContainer()


if __name__ == '__main__':
    print("This module works as a bridge between torrent checker and plugins.")
