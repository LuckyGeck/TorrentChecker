# -*- coding: utf-8 -*-

import hashlib
import io
import sys
import pytest
from unittest.mock import patch

from plugins.base import (
    Torrent, BasePlugin, ServerPlugin,
    OnStartPlugin, OnNewTorrentPlugin, OnFinishPlugin,
)


# ---------------------------------------------------------------------------
# Concrete stubs required to instantiate abstract classes
# ---------------------------------------------------------------------------

class _ConcreteServer(ServerPlugin):
    @staticmethod
    def get_plugin_name():
        return 'stub-server'

    def can_process_torrent(self, torrent):
        return torrent.tracker == 'stub-server'

    def is_authorized(self, opener):
        return True

    def authorize(self, opener):
        pass

    def get_topic_url(self, torrent):
        return 'http://example.com/{}'.format(torrent.id)

    def load_description(self, torrent):
        return 'Stub Description'

    def load_torrent_data(self, torrent):
        return b'stub data'

    def find_torrents(self, query, category='new-movie'):
        return iter([])


_SERVER_SETTINGS = {'active': True, 'debug': False, 'auth': {'login': 'u', 'password': 'p'}}


# ---------------------------------------------------------------------------
# Torrent
# ---------------------------------------------------------------------------

class TestTorrent:

    def test_load_from_dict_sets_all_fields(self):
        d = {
            'tracker': 'rutracker',
            'id': '123',
            'description': 'Test Movie',
            'full_description': 'Test Movie (2021) BDRip',
            'hash': 'abc123',
        }
        t = Torrent.load(d)
        assert t.tracker == 'rutracker'
        assert t.id == '123'
        assert t.description == 'Test Movie'
        assert t.full_description == 'Test Movie (2021) BDRip'
        assert t.hash == 'abc123'

    def test_load_preserves_extra_fields(self):
        t = Torrent.load({'tracker': 'rt', 'id': '1', 'seeders': '42'})
        assert t.seeders == '42'

    def test_dump_returns_copy_of_dict(self):
        t = Torrent()
        t.tracker = 'rt'
        t.id = '5'
        d = t.dump()
        assert d['tracker'] == 'rt'
        assert d['id'] == '5'
        # Mutating the dump must not affect the torrent
        d['tracker'] = 'other'
        assert t.tracker == 'rt'

    def test_copy_is_independent(self):
        t = Torrent.load({'tracker': 'rt', 'id': '7', 'description': 'A'})
        t2 = t.copy()
        t2.id = '999'
        t2.description = 'B'
        assert t.id == '7'
        assert t.description == 'A'

    def test_update_hash_for_data_produces_md5(self):
        t = Torrent()
        data = b'some torrent bytes'
        t.update_hash_for_data(data)
        assert t.hash == hashlib.md5(data).hexdigest()

    def test_update_hash_changes_on_different_data(self):
        t = Torrent()
        t.update_hash_for_data(b'data-v1')
        h1 = t.hash
        t.update_hash_for_data(b'data-v2')
        assert t.hash != h1

    def test_str_formats_correctly(self):
        t = Torrent()
        t.tracker = 'rt'
        t.id = '42'
        t.description = 'My Show S01E01'
        assert str(t) == '[rt.42] My Show S01E01'

    def test_load_then_dump_roundtrip(self):
        d = {'tracker': 'rt', 'id': '1', 'description': 'd',
             'full_description': 'fd', 'hash': 'h'}
        assert Torrent.load(d).dump() == d


# ---------------------------------------------------------------------------
# BasePlugin (via concrete subclass)
# ---------------------------------------------------------------------------

class TestBasePlugin:

    def test_active_defaults_to_false(self):
        plugin = _ConcreteServer({'auth': {}})
        assert plugin.active is False

    def test_active_reads_from_settings(self):
        plugin = _ConcreteServer({'active': True, 'auth': {}})
        assert plugin.active is True

    def test_debug_defaults_to_false(self):
        plugin = _ConcreteServer({'auth': {}})
        assert plugin.debug is False

    def test_log_message_writes_to_stdout(self):
        plugin = _ConcreteServer({'active': True, 'auth': {}})
        buf = io.StringIO()
        with patch('sys.stdout', buf):
            plugin.log_message('hello')
        assert 'hello' in buf.getvalue()
        assert plugin.get_plugin_name() in buf.getvalue()

    def test_log_message_error_writes_to_stderr(self):
        plugin = _ConcreteServer({'active': True, 'auth': {}})
        buf = io.StringIO()
        with patch('sys.stderr', buf):
            plugin.log_message('oops', is_error=True)
        assert 'oops' in buf.getvalue()

    def test_log_debug_only_when_debug_enabled(self):
        plugin = _ConcreteServer({'active': True, 'debug': False, 'auth': {}})
        buf = io.StringIO()
        with patch('sys.stderr', buf):
            plugin.log_debug('secret')
        assert 'secret' not in buf.getvalue()

    def test_log_debug_prints_when_debug_true(self):
        plugin = _ConcreteServer({'active': True, 'debug': True, 'auth': {}})
        buf = io.StringIO()
        with patch('sys.stderr', buf):
            plugin.log_debug('detail')
        assert 'detail' in buf.getvalue()

    def test_log_error_writes_to_stderr(self):
        plugin = _ConcreteServer({'active': True, 'auth': {}})
        buf = io.StringIO()
        err = ValueError('boom')
        with patch('sys.stderr', buf):
            plugin.log_error('Something failed', err)
        output = buf.getvalue()
        assert 'Something failed' in output
        assert 'boom' in output


# ---------------------------------------------------------------------------
# ServerPlugin
# ---------------------------------------------------------------------------

class TestServerPlugin:

    def test_reads_login_and_password_from_auth(self):
        plugin = _ConcreteServer({
            'active': True,
            'auth': {'login': 'myuser', 'password': 'secret'},
        })
        assert plugin.login == 'myuser'
        assert plugin.password == 'secret'

    def test_default_cookies_file_name(self):
        plugin = _ConcreteServer({'active': True, 'auth': {}})
        assert 'stub-server' in plugin.cookies_file

    def test_custom_cookies_file(self):
        plugin = _ConcreteServer({
            'active': True,
            'auth': {},
            'cookies_file': '/tmp/custom.cookies',
        })
        assert plugin.cookies_file == '/tmp/custom.cookies'

    def test_can_process_torrent_matching(self):
        plugin = _ConcreteServer(_SERVER_SETTINGS)
        t = Torrent.load({'tracker': 'stub-server', 'id': '1'})
        assert plugin.can_process_torrent(t) is True

    def test_can_process_torrent_not_matching(self):
        plugin = _ConcreteServer(_SERVER_SETTINGS)
        t = Torrent.load({'tracker': 'other', 'id': '1'})
        assert plugin.can_process_torrent(t) is False


# ---------------------------------------------------------------------------
# Abstract enforcement
# ---------------------------------------------------------------------------

class TestAbstractEnforcement:

    def test_cannot_instantiate_server_plugin_without_implementing_all(self):
        class Incomplete(ServerPlugin):
            @staticmethod
            def get_plugin_name():
                return 'x'
            # missing all abstract methods

        with pytest.raises(TypeError):
            Incomplete({'auth': {}})

    def test_cannot_instantiate_on_start_plugin_without_on_start(self):
        class Incomplete(OnStartPlugin):
            @staticmethod
            def get_plugin_name():
                return 'x'

        with pytest.raises(TypeError):
            Incomplete({})

    def test_cannot_instantiate_on_new_torrent_plugin_without_on_new_torrent(self):
        class Incomplete(OnNewTorrentPlugin):
            @staticmethod
            def get_plugin_name():
                return 'x'

        with pytest.raises(TypeError):
            Incomplete({})

    def test_cannot_instantiate_on_finish_plugin_without_on_finish(self):
        class Incomplete(OnFinishPlugin):
            @staticmethod
            def get_plugin_name():
                return 'x'

        with pytest.raises(TypeError):
            Incomplete({})
