# -*- coding: utf-8 -*-

import json
from codecs import open

titleTuple = ("tracker", "id", "hash", "descr")


def loadTorrentsList(torLines):
    retList = []
    for s in torLines:
        s = s.strip()
        t = s.split(':', 3)
        try:
            retList.append(t)
        except:
            pass
    return retList


def lineToDict(line):
    return dict(zip(titleTuple, line))


def main():
    lines = loadTorrentsList(open("torrents.lst", 'r', 'cp1251').readlines())
    resultList = []
    for line in lines:
        resultList.append(lineToDict(line))
    jsonString = json.dumps(resultList,
                            indent=2, encoding="cp1251", ensure_ascii=False)
    open("torrents.json", "w", "utf8").write(jsonString)

if __name__ == '__main__':
    main()
