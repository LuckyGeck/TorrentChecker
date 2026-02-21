# -*- coding: utf-8 -*-

import pytest
from unittest.mock import MagicMock, patch

from plugins import base

# Import using importlib because the file name contains a hyphen
import importlib.util, os

_plugins_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plugins')

def _load(filename):
    path = os.path.join(_plugins_dir, filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

rutracker_mod = _load('rutracker.py')
nnm_mod = _load('nnm-club.py')

RuTracker = rutracker_mod.RuTracker
RuTrackerTorrent = rutracker_mod.RuTrackerTorrent
NNMClub = nnm_mod.NNMClub
NNMClubTorrent = nnm_mod.NNMClubTorrent

_RT_SETTINGS = {'active': True, 'debug': False, 'auth': {'login': 'u', 'password': 'p'}}
_NNM_SETTINGS = {'active': True, 'debug': False, 'auth': {'login': 'u', 'password': 'p'}}

# ---------------------------------------------------------------------------
# Minimal HTML that satisfies each tracker's regex (newlines stripped)
# ---------------------------------------------------------------------------

_RT_HTML = (
    '<tr class="tCenter hl-tr">'
    ' <a href="viewforum.php?f=2200">Action</a>'
    ' <a href="viewtopic.php?t=12345" class="t">Movie Title (2021) BDRip [1080p]</a>'
    ' <span class="tor-size"><u>1073741824</u></span>'
    ' <b class="seedmed">100</b>'
    ' </tr>'
)

_NNM_HTML = (
    '<tr class="prow0">'
    ' <td><a href="something" class="gen">Action Films</a></td>'
    ' <td><a href="viewtopic.php?t=99999">title</a>'
    ' <b>Movie Title (2021) BDRip [1080p]</b></td>'
    ' <td><a href="download.php?id=11111">dl</a></td>'
    ' <td><u>2147483648</u></td>'
    ' <td class="seedmed"><b>200</b></td>'
    ' </tr>'
)


# ---------------------------------------------------------------------------
# RuTracker
# ---------------------------------------------------------------------------

class TestRuTracker:

    def test_plugin_name(self):
        assert RuTracker.get_plugin_name() == 'rutracker'

    def test_can_process_matching_torrent(self):
        plugin = RuTracker(_RT_SETTINGS)
        t = base.Torrent.load({'tracker': 'rutracker', 'id': '1'})
        assert plugin.can_process_torrent(t) is True

    def test_cannot_process_other_tracker(self):
        plugin = RuTracker(_RT_SETTINGS)
        t = base.Torrent.load({'tracker': 'nnm-club', 'id': '1'})
        assert plugin.can_process_torrent(t) is False

    def test_get_topic_url(self):
        plugin = RuTracker(_RT_SETTINGS)
        t = base.Torrent.load({'tracker': 'rutracker', 'id': '42'})
        url = plugin.get_topic_url(t)
        assert 'rutracker.org' in url
        assert '42' in url

    def test_find_torrents_parses_html(self):
        plugin = RuTracker(_RT_SETTINGS)
        plugin.opener = MagicMock()

        response = MagicMock()
        response.read.return_value = _RT_HTML.encode('cp1251')
        plugin.opener.open.return_value = response

        with patch.object(plugin, 'ensure_authorization'):
            results = list(plugin.find_torrents('Movie Title', 'new-movie'))

        assert len(results) == 1
        t = results[0]
        assert t.id == '12345'
        assert 'Movie Title' in t.full_description
        assert t.size == '1073741824'
        assert t.seeders == '100'

    def test_find_torrents_unknown_category_returns_empty(self):
        plugin = RuTracker(_RT_SETTINGS)
        with patch.object(plugin, 'ensure_authorization'):
            results = list(plugin.find_torrents('query', 'nonexistent-category'))
        assert results == []

    def test_find_torrents_no_match_returns_empty(self):
        plugin = RuTracker(_RT_SETTINGS)
        plugin.opener = MagicMock()
        response = MagicMock()
        response.read.return_value = b'<html>no results</html>'
        plugin.opener.open.return_value = response
        with patch.object(plugin, 'ensure_authorization'):
            results = list(plugin.find_torrents('nothing', 'new-movie'))
        assert results == []


# ---------------------------------------------------------------------------
# NNMClub
# ---------------------------------------------------------------------------

class TestNNMClub:

    def test_plugin_name(self):
        assert NNMClub.get_plugin_name() == 'nnm-club'

    def test_can_process_matching_torrent(self):
        plugin = NNMClub(_NNM_SETTINGS)
        t = base.Torrent.load({'tracker': 'nnm-club', 'id': '1'})
        assert plugin.can_process_torrent(t) is True

    def test_cannot_process_other_tracker(self):
        plugin = NNMClub(_NNM_SETTINGS)
        t = base.Torrent.load({'tracker': 'rutracker', 'id': '1'})
        assert plugin.can_process_torrent(t) is False

    def test_get_topic_url(self):
        plugin = NNMClub(_NNM_SETTINGS)
        t = base.Torrent.load({'tracker': 'nnm-club', 'id': '77'})
        url = plugin.get_topic_url(t)
        assert 'nnm-club' in url
        assert '77' in url

    def test_find_torrents_parses_html(self):
        plugin = NNMClub(_NNM_SETTINGS)
        plugin.opener = MagicMock()

        response = MagicMock()
        response.read.return_value = _NNM_HTML.encode('cp1251')
        plugin.opener.open.return_value = response

        with patch.object(plugin, 'ensure_authorization'):
            results = list(plugin.find_torrents('Movie Title', 'new-movie'))

        assert len(results) == 1
        t = results[0]
        assert t.id == '99999'
        assert 'Movie Title' in t.full_description
        assert t.download_id == '11111'
        assert t.size == '2147483648'
        assert t.seeders == '200'

    def test_find_torrents_unknown_category_returns_empty(self):
        plugin = NNMClub(_NNM_SETTINGS)
        with patch.object(plugin, 'ensure_authorization'):
            results = list(plugin.find_torrents('query', 'nonexistent-category'))
        assert results == []

    def test_find_torrents_no_match_returns_empty(self):
        plugin = NNMClub(_NNM_SETTINGS)
        plugin.opener = MagicMock()
        response = MagicMock()
        response.read.return_value = b'<html>no results</html>'
        plugin.opener.open.return_value = response
        with patch.object(plugin, 'ensure_authorization'):
            results = list(plugin.find_torrents('nothing', 'new-movie'))
        assert results == []


# ---------------------------------------------------------------------------
# RuTrackerTorrent / NNMClubTorrent  (subclass initialisation)
# ---------------------------------------------------------------------------

class TestTrackerTorrentSubclasses:

    def test_rutracker_torrent_has_correct_tracker(self):
        t = RuTrackerTorrent()
        assert t.tracker == 'rutracker'

    def test_rutracker_torrent_str(self):
        t = RuTrackerTorrent()
        t.id = '1'
        t.full_description = 'Film (2020) BDRip'
        s = str(t)
        assert 'rutracker' in s
        assert '1' in s

    def test_nnm_torrent_has_correct_tracker(self):
        t = NNMClubTorrent()
        assert t.tracker == 'nnm-club'

    def test_nnm_torrent_str(self):
        t = NNMClubTorrent()
        t.id = '2'
        t.full_description = 'Film (2021) HDRip'
        s = str(t)
        assert 'nnm-club' in s
        assert '2' in s
