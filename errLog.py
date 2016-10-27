# -*- coding: utf-8 -*-

from time import gmtime, strftime


class err_file():

    def __init__(self, path):
        self.launchTime = strftime("%H:%M:%S %d-%m-%Y", gmtime())
        self.path = path
        self.out = open(path, "a")
        self.printWarn = True

    def write(self, *args):
        if self.printWarn:
            self.printWarn = False
            self.out.write("\n\t[***] Error at [{}]\n".format(self.launchTime))
            print "Error occured! Terminating..."
            print "See error info in [{}]".format(self.path)

        self.out.write(*args)

#import sys
#sys.stderr = err_file("error.txt")
