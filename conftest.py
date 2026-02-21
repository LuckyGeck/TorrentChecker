import sys
import os
import types

# Ensure the project root is on sys.path for all test imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Inject a stub 'settings' module before any test file imports it.
# This avoids requiring a real settings.json file to run the test suite.
_TEST_SETTINGS = {
    "shows": {
        "save_as": "./[{tracker}].t{id}.torrent",
        "list_path": "./shows.json",
    },
    "movies": {
        "save_as": "./[{tracker}].movie.t{id}.torrent",
        "db_path": "./movies.json",
        "tracker": "nnm-club",
        "category": "new-movie",
        "min_seeders": 400,
        "min_size": 2_300_000_000,
    },
    "plugins": {},
}

_settings_stub = types.ModuleType("settings")
_settings_stub.settings = _TEST_SETTINGS
sys.modules.setdefault("settings", _settings_stub)
