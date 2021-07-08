#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author:       Sychev Pavel
# Created:      28.08.2017
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL
import datetime
import os
from time import sleep

import logging

from shows_updater import main as shows_updater
from new_movies_tracker import main as new_movies_tracker


SLEEP_TIME = datetime.timedelta(
    seconds=int(os.environ.get('SLEEP_TIME', '3600'))
)
logger = logging.getLogger(__name__)


def main():
    try:
        while True:
            logger.info(datetime.datetime.now())

            logger.info('Updating shows')
            shows_updater()

            logger.info('Loading new movies')
            new_movies_tracker()

            logger.info('Sleep for {}'.format(SLEEP_TIME))
            sleep(SLEEP_TIME.total_seconds())
    except KeyboardInterrupt:
        return


def setup_logging():
    logging_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=logging_format, level=logging.DEBUG)


if __name__ == '__main__':
    setup_logging()
    main()
