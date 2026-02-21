# -*- coding: utf-8 -*-

import io
import json
import pytest
from unittest.mock import MagicMock, patch, mock_open

from plugins import base
import shows_updater


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_torrent(tracker='rt', tid='1', description='Show S01E01', hash_='old'):
    t = base.Torrent()
    t.tracker = tracker
    t.id = tid
    t.description = description
    t.full_description = description
    t.hash = hash_
    return t


def _make_plugin(torrent_data=b'data', description='Full Title'):
    plugin = MagicMock()
    plugin.load_torrent_data.return_value = torrent_data
    plugin.load_description.return_value = description
    return plugin


# ---------------------------------------------------------------------------
# load_torrents_list
# ---------------------------------------------------------------------------

class TestLoadTorrentsList:

    def test_returns_list_of_torrent_objects(self, tmp_path):
        data = [{'tracker': 'rt', 'id': '5', 'description': 'Show',
                 'full_description': 'Show S01', 'hash': 'abc'}]
        path = tmp_path / 'shows.json'
        path.write_text(json.dumps(data))
        result = shows_updater.load_torrents_list(str(path))
        assert len(result) == 1
        assert isinstance(result[0], base.Torrent)
        assert result[0].tracker == 'rt'
        assert result[0].id == '5'

    def test_empty_list(self, tmp_path):
        path = tmp_path / 'shows.json'
        path.write_text('[]')
        result = shows_updater.load_torrents_list(str(path))
        assert result == []

    def test_multiple_torrents(self, tmp_path):
        data = [
            {'tracker': 'rt', 'id': '1', 'description': 'A', 'full_description': 'A', 'hash': 'h1'},
            {'tracker': 'nnm', 'id': '2', 'description': 'B', 'full_description': 'B', 'hash': 'h2'},
        ]
        path = tmp_path / 'shows.json'
        path.write_text(json.dumps(data))
        result = shows_updater.load_torrents_list(str(path))
        assert len(result) == 2
        assert result[1].tracker == 'nnm'


# ---------------------------------------------------------------------------
# save_torrents_list
# ---------------------------------------------------------------------------

class TestSaveTorrentsList:

    def test_writes_json_file(self, tmp_path):
        t1 = _make_torrent(tracker='rt', tid='10')
        t2 = _make_torrent(tracker='nnm', tid='20')
        path = tmp_path / 'out.json'
        shows_updater.save_torrents_list([t1, t2], str(path))
        saved = json.loads(path.read_text())
        assert len(saved) == 2
        assert saved[0]['tracker'] == 'rt'
        assert saved[0]['id'] == '10'
        assert saved[1]['tracker'] == 'nnm'

    def test_roundtrip(self, tmp_path):
        t = _make_torrent(tracker='rt', tid='99', description='My Show')
        path = tmp_path / 'rt.json'
        shows_updater.save_torrents_list([t], str(path))
        loaded = shows_updater.load_torrents_list(str(path))
        assert loaded[0].tracker == 'rt'
        assert loaded[0].id == '99'
        assert loaded[0].description == 'My Show'


# ---------------------------------------------------------------------------
# process_torrent
# ---------------------------------------------------------------------------

class TestProcessTorrent:

    def test_unchanged_torrent_returns_original(self, tmp_path):
        data = b'torrent bytes'
        torrent = _make_torrent(hash_=None)
        import hashlib
        torrent.hash = hashlib.md5(data).hexdigest()
        plugin = _make_plugin(torrent_data=data)

        with patch('shows_updater.plugins') as mock_plugins:
            mock_plugins.get_server_for_torrent.return_value = plugin
            result = shows_updater.process_torrent(torrent, str(tmp_path / '{id}.torrent'))

        assert result is torrent
        mock_plugins.process_on_new_torrent.assert_not_called()

    def test_changed_torrent_saves_file_and_notifies(self, tmp_path):
        torrent = _make_torrent(hash_='stale-hash')
        new_data = b'updated torrent bytes'
        plugin = _make_plugin(torrent_data=new_data, description='Updated Title')

        template = str(tmp_path / '{id}.torrent')
        with patch('shows_updater.plugins') as mock_plugins:
            mock_plugins.get_server_for_torrent.return_value = plugin
            result = shows_updater.process_torrent(torrent, template)

        assert result is not torrent
        assert result.hash != 'stale-hash'
        assert result.full_description == 'Updated Title'
        mock_plugins.process_on_new_torrent.assert_called_once()
        saved_path = tmp_path / '1.torrent'
        assert saved_path.exists()
        assert saved_path.read_bytes() == new_data

    def test_no_plugin_raises(self):
        torrent = _make_torrent()
        with patch('shows_updater.plugins') as mock_plugins:
            mock_plugins.get_server_for_torrent.return_value = None
            with pytest.raises(Exception, match='No such server handler'):
                shows_updater.process_torrent(torrent, '/tmp/{id}.torrent')
