# -*- coding: utf-8 -*-

import pytest
from unittest.mock import MagicMock, patch, call

from plugins import PluginsContainer
from plugins import base


# ---------------------------------------------------------------------------
# Concrete stubs
# ---------------------------------------------------------------------------

def _make_server(name, active=True):
    class _S(base.ServerPlugin):
        @staticmethod
        def get_plugin_name():
            return name

        def can_process_torrent(self, t):
            return t.tracker == name

        def is_authorized(self, o):
            return True

        def authorize(self, o):
            pass

        def get_topic_url(self, t):
            return ''

        def load_description(self, t):
            return ''

        def load_torrent_data(self, t):
            return b''

        def find_torrents(self, q, c='new-movie'):
            return iter([])

    return _S({'active': active, 'debug': False, 'auth': {}})


def _make_on_start(name, active=True):
    class _P(base.OnStartPlugin):
        @staticmethod
        def get_plugin_name():
            return name

        def on_start(self):
            pass

    return _P({'active': active, 'debug': False})


def _make_on_new(name, active=True):
    class _P(base.OnNewTorrentPlugin):
        @staticmethod
        def get_plugin_name():
            return name

        def on_new_torrent(self, torrent, plugin_obj):
            pass

    return _P({'active': active, 'debug': False})


def _make_on_finish(name, active=True):
    class _P(base.OnFinishPlugin):
        @staticmethod
        def get_plugin_name():
            return name

        def on_finish(self):
            pass

    return _P({'active': active, 'debug': False})


def _container_with(plugins_dict):
    c = PluginsContainer()
    c._PluginsContainer__all_plugins = plugins_dict
    return c


# ---------------------------------------------------------------------------
# get_server
# ---------------------------------------------------------------------------

class TestGetServer:

    def test_returns_active_server_plugin(self):
        server = _make_server('rt', active=True)
        c = _container_with({'rt': server})
        assert c.get_server('rt') is server

    def test_returns_none_for_inactive_server(self):
        server = _make_server('rt', active=False)
        c = _container_with({'rt': server})
        assert c.get_server('rt') is None

    def test_returns_none_for_unknown_name(self):
        c = _container_with({})
        with pytest.raises((AttributeError, KeyError)):
            c.get_server('nonexistent')


# ---------------------------------------------------------------------------
# get_server_for_torrent
# ---------------------------------------------------------------------------

class TestGetServerForTorrent:

    def test_returns_matching_server(self):
        s1 = _make_server('rt', active=True)
        s2 = _make_server('nnm', active=True)
        c = _container_with({'rt': s1, 'nnm': s2})
        torrent = base.Torrent.load({'tracker': 'nnm', 'id': '1'})
        assert c.get_server_for_torrent(torrent) is s2

    def test_returns_none_when_no_match(self):
        s = _make_server('rt', active=True)
        c = _container_with({'rt': s})
        torrent = base.Torrent.load({'tracker': 'other', 'id': '1'})
        assert c.get_server_for_torrent(torrent) is None

    def test_skips_inactive_server(self):
        s = _make_server('rt', active=False)
        c = _container_with({'rt': s})
        torrent = base.Torrent.load({'tracker': 'rt', 'id': '1'})
        assert c.get_server_for_torrent(torrent) is None


# ---------------------------------------------------------------------------
# process_on_start
# ---------------------------------------------------------------------------

class TestProcessOnStart:

    def test_calls_on_start_for_active_plugins(self):
        p = _make_on_start('ep', active=True)
        p.on_start = MagicMock()
        c = _container_with({'ep': p})
        c.process_on_start()
        p.on_start.assert_called_once()

    def test_skips_inactive_plugins(self):
        p = _make_on_start('ep', active=False)
        p.on_start = MagicMock()
        c = _container_with({'ep': p})
        c.process_on_start()
        p.on_start.assert_not_called()

    def test_logs_error_and_continues_on_exception(self):
        p1 = _make_on_start('p1', active=True)
        p2 = _make_on_start('p2', active=True)
        p1.on_start = MagicMock(side_effect=RuntimeError('fail'))
        p2.on_start = MagicMock()
        c = _container_with({'p1': p1, 'p2': p2})
        c.process_on_start()  # must not raise
        p2.on_start.assert_called_once()


# ---------------------------------------------------------------------------
# process_on_new_torrent
# ---------------------------------------------------------------------------

class TestProcessOnNewTorrent:

    def test_calls_on_new_torrent_for_active_plugins(self):
        p = _make_on_new('np', active=True)
        p.on_new_torrent = MagicMock()
        server = _make_server('rt')
        torrent = base.Torrent.load({'tracker': 'rt', 'id': '1'})
        c = _container_with({'np': p})
        c.process_on_new_torrent(torrent, server)
        p.on_new_torrent.assert_called_once_with(torrent, server)

    def test_skips_inactive_plugins(self):
        p = _make_on_new('np', active=False)
        p.on_new_torrent = MagicMock()
        server = _make_server('rt')
        torrent = base.Torrent.load({'tracker': 'rt', 'id': '1'})
        c = _container_with({'np': p})
        c.process_on_new_torrent(torrent, server)
        p.on_new_torrent.assert_not_called()

    def test_continues_on_exception(self):
        p1 = _make_on_new('p1', active=True)
        p2 = _make_on_new('p2', active=True)
        p1.on_new_torrent = MagicMock(side_effect=RuntimeError('fail'))
        p2.on_new_torrent = MagicMock()
        server = _make_server('rt')
        torrent = base.Torrent.load({'tracker': 'rt', 'id': '1'})
        c = _container_with({'p1': p1, 'p2': p2})
        c.process_on_new_torrent(torrent, server)
        p2.on_new_torrent.assert_called_once()


# ---------------------------------------------------------------------------
# process_on_finish
# ---------------------------------------------------------------------------

class TestProcessOnFinish:

    def test_calls_on_finish_for_active_plugins(self):
        p = _make_on_finish('fp', active=True)
        p.on_finish = MagicMock()
        c = _container_with({'fp': p})
        c.process_on_finish()
        p.on_finish.assert_called_once()

    def test_skips_inactive_plugins(self):
        p = _make_on_finish('fp', active=False)
        p.on_finish = MagicMock()
        c = _container_with({'fp': p})
        c.process_on_finish()
        p.on_finish.assert_not_called()

    def test_continues_on_exception(self):
        p1 = _make_on_finish('p1', active=True)
        p2 = _make_on_finish('p2', active=True)
        p1.on_finish = MagicMock(side_effect=RuntimeError('fail'))
        p2.on_finish = MagicMock()
        c = _container_with({'p1': p1, 'p2': p2})
        c.process_on_finish()
        p2.on_finish.assert_called_once()
