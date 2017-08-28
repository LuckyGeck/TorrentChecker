#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author:       Sychev Pavel
# Created:      28.08.2017
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL
import datetime
import os
from time import sleep

from shows_updater import main as shows_updater
from new_movies_tracker import main as new_movies_tracker


SLEEP_TIME = datetime.timedelta(
    seconds=int(os.environ.get('SLEEP_TIME', '3600'))
)


def main():
    try:
        while True:
            print(datetime.datetime.now())

            print('Updating shows')
            shows_updater()

            print('Loading new movies')
            new_movies_tracker()

            print('Sleep for {}'.format(SLEEP_TIME))
            sleep(SLEEP_TIME.total_seconds())
    except KeyboardInterrupt:
        return

if __name__ == '__main__':
    main()
