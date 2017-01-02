# -*- coding: utf-8 -*-

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
