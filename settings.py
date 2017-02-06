# -*- coding: utf-8 -*-

# Author:       Nikolay Volosatov
# Created:      05.02.2017
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL

import json


def load_settings():
    import os
    dir = os.path.dirname(os.path.realpath(__file__))
    settings_file_path = os.path.join(dir, 'settings.json')
    with open(settings_file_path) as settings_file:
        return json.load(settings_file)

settings = load_settings()
