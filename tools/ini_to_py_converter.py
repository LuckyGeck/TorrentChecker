# -*- coding: utf-8 -*-

import json
import string
from codecs import open


def readSettings(path):
    settings = {}
    fileSettings = open(path, 'r')
    info = fileSettings.readline()
    while (info != ''):
        if string.strip(info) == '':
            info = fileSettings.readline()
            continue
        (first, second) = string.split(string.strip(info), '=', 2)
        settings[first] = second
        info = fileSettings.readline()
    fileSettings.close()
    return settings


def main():
    resultList = readSettings("settings.ini")
    jsonString = json.dumps(resultList,
                            indent=2, encoding="utf-8", ensure_ascii=False)
    text = "settings = {}" .format(jsonString)
    open("settings.py", "w").write(text)

if __name__ == '__main__':
    main()
