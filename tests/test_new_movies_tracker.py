# -*- coding: utf-8 -*-

import json
import pytest
from unittest.mock import MagicMock, patch

from plugins import base
import new_movies_tracker
from new_movies_tracker import Movie, NewMoviesTracker


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_torrent(full_description, seeders=500, size=3_000_000_000, tracker='nnm-club'):
    t = base.Torrent()
    t.tracker = tracker
    t.id = '123'
    t.description = 'Test Movie'
    t.full_description = full_description
    t.hash = None
    t.seeders = str(seeders)
    t.size = str(size)
    return t


_SETTINGS = {
    'save_as': '/tmp/{tracker}.{id}.torrent',
    'db_path': '/tmp/movies.json',
    'tracker': 'nnm-club',
    'category': 'new-movie',
    'min_seeders': 400,
    'min_size': 2_000_000_000,
}


# ---------------------------------------------------------------------------
# Movie parsing
# ---------------------------------------------------------------------------

class TestMovie:

    def test_parses_full_description(self):
        torrent = _make_torrent('Inception / Inception (2010) BDRip [1080p]')
        m = Movie(torrent)
        assert m.year == '2010'
        assert m.name == 'Inception'
        assert m.orig_name == 'Inception'

    def test_parses_bilingual_name(self):
        torrent = _make_torrent('Начало / Inception (2010) BDRip [1080p]')
        m = Movie(torrent)
        assert m.name == 'Начало'
        assert m.orig_name == 'Inception'

    def test_parses_quality_bdrip(self):
        torrent = _make_torrent('The Matrix / The Matrix (1999) BDRip [720p/x264]')
        m = Movie(torrent)
        assert m.quality == 'BDRip'

    def test_parses_quality_with_codec(self):
        torrent = _make_torrent('Test Movie (2020) BDRip [1080p/x265]')
        m = Movie(torrent)
        assert m.codec == '1080p'
        assert m.codec_q == 'x265'

    def test_parses_quality_with_multi_slash_codec(self):
        # codec_q captures everything after the first '/' up to ']'
        torrent = _make_torrent('Test Movie (2020) BDRip [1080p/x265/HDR]')
        m = Movie(torrent)
        assert m.codec == '1080p'
        assert m.codec_q == 'x265/HDR'

    def test_str_includes_year_and_name(self):
        torrent = _make_torrent('Movie Title (2021) HDRip [720p]')
        m = Movie(torrent)
        s = str(m)
        assert '2021' in s
        assert 'Movie Title' in s

    def test_seeders_and_size_converted_to_int(self):
        torrent = _make_torrent('Film (2022) BDRip', seeders=150, size=1_500_000_000)
        m = Movie(torrent)
        assert m.seeders == 150
        assert m.size == 1_500_000_000


# ---------------------------------------------------------------------------
# NewMoviesTracker._NewMoviesTracker__process_torrent
# ---------------------------------------------------------------------------

class TestNewMoviesTrackerProcess:

    def _tracker(self, db=None, extra_settings=None):
        settings = dict(_SETTINGS)
        if extra_settings:
            settings.update(extra_settings)
        t = NewMoviesTracker(settings)
        t.loaded_movies_db = db if db is not None else []
        return t

    def _plugin(self, data=b'x'):
        p = MagicMock()
        p.load_torrent_data.return_value = data
        p.get_topic_url.return_value = 'http://example.com/1'
        return p

    def test_skips_existing_movie(self, capsys):
        torrent = _make_torrent('The Matrix / The Matrix (1999) BDRip [720p]')
        tracker = self._tracker(db=['The Matrix'])
        plugin = self._plugin()
        tracker._NewMoviesTracker__process_torrent(torrent, plugin)
        plugin.load_torrent_data.assert_not_called()

    def test_skips_below_min_seeders(self):
        torrent = _make_torrent('Low Seed Film (2020) BDRip', seeders=10)
        tracker = self._tracker(extra_settings={'min_seeders': 400, 'min_size': None})
        plugin = self._plugin()
        tracker._NewMoviesTracker__process_torrent(torrent, plugin)
        plugin.load_torrent_data.assert_not_called()

    def test_skips_below_min_size(self):
        torrent = _make_torrent('Tiny Film (2020) BDRip', size=100)
        tracker = self._tracker(extra_settings={'min_seeders': None, 'min_size': 2_000_000_000})
        plugin = self._plugin()
        tracker._NewMoviesTracker__process_torrent(torrent, plugin)
        plugin.load_torrent_data.assert_not_called()

    def test_downloads_new_qualifying_torrent(self, tmp_path):
        torrent = _make_torrent('New Film (2023) BDRip [1080p]', seeders=500, size=3_000_000_000)
        settings = dict(_SETTINGS)
        settings['save_as'] = str(tmp_path / '{tracker}.{id}.torrent')
        tracker = NewMoviesTracker(settings)
        tracker.loaded_movies_db = []
        plugin = self._plugin(data=b'torrent bytes')
        with patch('new_movies_tracker.plugins') as mock_plugins:
            tracker._NewMoviesTracker__process_torrent(torrent, plugin)
        plugin.load_torrent_data.assert_called_once_with(torrent)
        assert 'New Film' in tracker.loaded_movies_db

    def test_no_min_filters_allows_anything(self, tmp_path):
        torrent = _make_torrent('Tiny Film (2020) BDRip', seeders=1, size=1)
        settings = dict(_SETTINGS)
        settings['save_as'] = str(tmp_path / '{tracker}.{id}.torrent')
        settings['min_seeders'] = None
        settings['min_size'] = None
        tracker = NewMoviesTracker(settings)
        tracker.loaded_movies_db = []
        plugin = self._plugin()
        with patch('new_movies_tracker.plugins'):
            tracker._NewMoviesTracker__process_torrent(torrent, plugin)
        plugin.load_torrent_data.assert_called_once()
