# -*- coding: utf-8 -*-

# ----------------------------------------------------------
# Name:        Error logging plugin
# Purpose:     Plugin for torrentChecker
#
# Author:      Sychev Pavel, Volosatov Nikolay
#
# Created:     22.01.2017
# Copyright:   (c) Sychev Pavel 2012
# Licence:     GPL
# ----------------------------------------------------------

import base
from time import gmtime, strftime


class ErrorFile:

    def __init__(self, path):
        self.launch_time = strftime("%H:%M:%S %d-%m-%Y", gmtime())
        self.path = path
        self.out = open(path, "a")
        self.print_warn = True

    def write(self, *args):
        if self.print_warn:
            self.print_warn = False
            self.out.write(
                "\n\t[***] Error at [{}]\n".format(self.launch_time))
            print "Error occured! Terminating..."
            print "See error info in [{}]".format(self.path)

        self.out.write(*args)


class ErrorLog(base.OnStartPlugin):

    def __init__(self, settings):
        base.OnStartPlugin.__init__(self, settings)
        self.save_as = settings['save_as']

    @staticmethod
    def get_plugin_name():
        return 'error_log'

    def on_start_process(self):
        import sys
        sys.stderr = ErrorFile(self.save_as)
