# -*- coding: utf-8 -*-

import json
import pytest
from unittest.mock import MagicMock, patch

from plugins import base
from plugins.logger import Logger


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_torrent(tid='42', description='Show S01E01', tracker='rt'):
    t = base.Torrent()
    t.tracker = tracker
    t.id = tid
    t.description = description
    t.full_description = description
    t.hash = 'abc'
    return t


def _make_plugin(description='Full Title', url='http://example.com'):
    p = MagicMock()
    p.load_description.return_value = description
    p.get_topic_url.return_value = url
    p.get_plugin_name.return_value = 'rt'
    return p


def _text_logger(path):
    return Logger({'active': True, 'debug': False, 'save_as': path, 'use_json': False})


def _json_logger(path):
    return Logger({'active': True, 'debug': False, 'save_as': path, 'use_json': True})


# ---------------------------------------------------------------------------
# on_new_torrent (text mode)
# ---------------------------------------------------------------------------

class TestLoggerTextMode:

    def test_appends_entry_to_log_list(self):
        logger = _text_logger('/dev/null')
        torrent = _make_torrent()
        plugin = _make_plugin()
        logger.on_new_torrent(torrent, plugin)
        assert len(logger.log_list) == 1

    def test_entry_contains_torrent_id_and_description(self):
        logger = _text_logger('/dev/null')
        torrent = _make_torrent(tid='99', description='My Show S02E03')
        logger.on_new_torrent(torrent, _make_plugin())
        assert '99' in logger.log_list[0]
        assert 'My Show S02E03' in logger.log_list[0]

    def test_multiple_torrents_appended(self):
        logger = _text_logger('/dev/null')
        logger.on_new_torrent(_make_torrent(tid='1'), _make_plugin())
        logger.on_new_torrent(_make_torrent(tid='2'), _make_plugin())
        assert len(logger.log_list) == 2

    def test_on_finish_writes_to_file(self, tmp_path):
        path = str(tmp_path / 'test.log')
        logger = _text_logger(path)
        logger.on_new_torrent(_make_torrent(description='Show'), _make_plugin())
        logger.on_finish()
        content = open(path).read()
        assert 'Show' in content

    def test_on_finish_does_nothing_when_empty(self, tmp_path):
        path = str(tmp_path / 'empty.log')
        logger = _text_logger(path)
        logger.on_finish()  # must not raise, must not create file
        assert not (tmp_path / 'empty.log').exists()

    def test_on_finish_appends_to_existing(self, tmp_path):
        path = str(tmp_path / 'existing.log')
        open(path, 'w').write('old entry\n')
        logger = _text_logger(path)
        logger.on_new_torrent(_make_torrent(description='New Entry'), _make_plugin())
        logger.on_finish()
        content = open(path).read()
        assert 'old entry' in content
        assert 'New Entry' in content


# ---------------------------------------------------------------------------
# on_new_torrent (JSON mode)
# ---------------------------------------------------------------------------

class TestLoggerJsonMode:

    def test_appends_dict_to_log_list(self):
        logger = _json_logger('/dev/null')
        torrent = _make_torrent(tid='7', tracker='rt')
        plugin = _make_plugin(description='Full', url='http://x.com')
        logger.on_new_torrent(torrent, plugin)
        assert len(logger.log_list) == 1
        entry = logger.log_list[0]
        assert entry['id'] == '7'
        assert entry['tracker'] == 'rt'
        assert entry['shortDescr'] == 'Show S01E01'
        assert 'time' in entry

    def test_on_finish_writes_valid_json(self, tmp_path):
        path = str(tmp_path / 'log.json')
        logger = _json_logger(path)
        logger.on_new_torrent(_make_torrent(tid='5'), _make_plugin())
        logger.on_finish()
        with open(path) as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]['id'] == '5'

    def test_on_finish_merges_with_existing_json(self, tmp_path):
        path = str(tmp_path / 'log.json')
        existing = [{'id': 'old', 'time': 0, 'shortDescr': 'x', 'fullDescr': 'x', 'url': '', 'tracker': 'rt'}]
        open(path, 'w').write(json.dumps(existing))
        logger = _json_logger(path)
        logger.on_new_torrent(_make_torrent(tid='new'), _make_plugin())
        logger.on_finish()
        with open(path) as f:
            data = json.load(f)
        assert len(data) == 2
        ids = [e['id'] for e in data]
        assert 'old' in ids
        assert 'new' in ids

    def test_on_finish_handles_invalid_existing_json(self, tmp_path):
        path = str(tmp_path / 'broken.json')
        open(path, 'w').write('not json')
        logger = _json_logger(path)
        logger.on_new_torrent(_make_torrent(), _make_plugin())
        logger.on_finish()  # must not raise
        with open(path) as f:
            data = json.load(f)
        assert len(data) == 1
