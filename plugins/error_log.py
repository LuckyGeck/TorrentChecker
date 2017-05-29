# -*- coding: utf-8 -*-

# Author:       Sychev Pavel, Volosatov Nikolay
# Created:      22.01.2017
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL

from time import gmtime, strftime

import base


class ErrorFile:

    def __init__(self, path, print_warn=True):
        self.launch_time = strftime("%H:%M:%S %d-%m-%Y", gmtime())
        self.path = path
        self.out = open(path, "a")
        self.print_warn = print_warn

    def write(self, *args):
        if self.print_warn:
            self.print_warn = False
            self.out.write("\n\t[***] Error at '{}'\n"
                           .format(self.launch_time))
            print "Error occurred! See '{}'".format(self.path)

        self.out.write(*args)


class ErrorLog(base.OnStartPlugin):

    def __init__(self, settings):
        base.OnStartPlugin.__init__(self, settings)
        self.save_as = settings['save_as']
        self.print_warn = settings['print_warn']

    @staticmethod
    def get_plugin_name():
        return 'error_log'

    def on_start(self):
        import sys
        sys.stderr = ErrorFile(self.save_as, self.print_warn)
