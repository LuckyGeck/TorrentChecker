# -*- coding: utf-8 -*-

# Author:       Nikolay Volosatov
# Created:      05.02.2017
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL


def load_settings():
    import os
    import json
    current_dir = os.path.dirname(os.path.realpath(__file__))
    settings_file_path = os.path.join(current_dir, 'settings.json')
    return json.load(open(settings_file_path, 'r'))

settings = load_settings()
