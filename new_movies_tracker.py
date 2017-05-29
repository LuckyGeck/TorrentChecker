#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author:       Nikolay Volosatov
# Created:      06.02.2017
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL

import json
import re

from plugins import plugins, base
from settings import settings


class Movie(object):
    full_re = re.compile(r'(?P<name>.*?)\s+'
                         r'\((?P<year>[12]\d+)\)\s+'
                         r'(?P<quality>.*)')
    quality_re = re.compile(r'(?P<quality>[^\s]+)'
                            r'(\s+\[(?P<codec>[^\]/]+)'
                            r'(/(?P<codec_q>[^\]]+))?\])?'
                            r'(\s+\[(?P<line>Line)\])?')

    def __init__(self, torrent):
        self.torrent = torrent
        self.seeders = int(torrent.seeders)
        self.size = int(torrent.size)
        full_description = torrent.full_description
        full_match = self.full_re.search(full_description)
        if full_match:
            full = full_match.groupdict()
            self.full_name = full["name"]
            self.year = full["year"]
            full_quality = full["quality"]
            names = map(lambda s: s.strip(), self.full_name.split('/'))
            self.orig_name = names[-1]
            self.name = names[0]
            quality_dict = self.quality_re.search(full_quality).groupdict()
            if quality_dict:
                self.quality = quality_dict['quality']
                self.codec = quality_dict['codec']
                self.codec_q = quality_dict['codec_q']

    def __str__(self):
        fmt = '{year} {size:5.2f}Gb {seeders:5}  {quality:9} {name}'
        return fmt.format(
            year=self.year,
            size=float(self.size) / (1 << 30),
            seeders=self.seeders,
            quality=self.codec_q or self.quality,
            name=self.orig_name
        )


class NewMoviesTracker(object):

    def __init__(self, settings):
        self.save_as_template = settings['save_as']
        self.db_path = settings['db_path']
        self.tracker = settings['tracker']
        self.category = settings['category']
        self.min_seeders = settings.get('min_seeders')
        self.min_size = settings.get('min_size')
        self.loaded_movies_db = []

    def __load_db(self):
        self.loaded_movies_db = []
        try:
            self.loaded_movies_db = json.load(open(self.db_path, 'r'))
        except:
            pass

    def __save_db(self):
        json.dump(self.loaded_movies_db, open(self.db_path, 'w'), indent=4)

    def __load_torrent(self, torrent, plugin):
        data = plugin.load_torrent_data(torrent)
        torrent.update_hash_for_data(data)
        file_name = self.save_as_template.format(**torrent.dump())
        with open(file_name, 'wb') as torrent_file:
            torrent_file.write(data)

    def __process_torrent(self, torrent, plugin):
        movie = Movie(torrent)
        key = movie.orig_name.decode('utf8')
        if key in self.loaded_movies_db:
            print '[!exst]', movie
            return
        if self.min_seeders and movie.seeders < self.min_seeders:
            print '[!seed]', movie
            return
        if self.min_size and movie.size < self.min_size:
            print '[!size]', movie
            return

        print '      +', movie
        self.__load_torrent(torrent, plugin)
        plugins.process_on_new_torrent(torrent, plugin)
        self.loaded_movies_db.append(key)

    def process(self):
        self.__load_db()
        plugins.process_on_start()

        plugin = plugins.get_server(self.tracker)
        torrents = plugin.find_torrents('', self.category)
        for torrent in torrents:
            self.__process_torrent(torrent, plugin)

        self.__save_db()
        plugins.process_on_finish()


def main():
    plugins.load(settings["plugins"])
    tracker = NewMoviesTracker(settings["movies"])
    tracker.process()

if __name__ == '__main__':
    main()
