# Copyright (C) 2015 https://github.com/thof
#
# This file is part of decapromolist.
#
# decapromolist is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import json
import datetime
from bisect import bisect_left


class Utils:
    def __init__(self):
        pass

    config = {}
    CONF_FILE = "../config/config.json"
    dateTime = datetime.datetime.now().strftime("%d%m%Y")

    @staticmethod
    def getConfig():
        if Utils.config == {}:
            Utils.loadConfig()
        return Utils.config

    @staticmethod
    def loadConfig():
        with open(Utils.CONF_FILE) as json_file:
            Utils.config = json.load(json_file)

    @staticmethod
    def renameFile(filename):
        dotPos = filename.rfind('.')
        newFilename = filename[:dotPos] + "_" + Utils.dateTime + "." + filename[dotPos+1:]
        # newFilename = filename.split('.')[0] + "_" + Utils.dateTime + "." + filename.split('.')[1]
        try:
            os.rename(filename, newFilename)
        except OSError as oe:
            print oe

    @staticmethod
    def saveJsonFile(filename, content):
        with open(filename, 'w') as outfile:
            json.dump(content, outfile)  # sort_keys = True, indent = 4

    @staticmethod
    def buildArray(ilist):
        array = []
        for item in ilist:
            array.append(item['id'])
        return array

    @staticmethod
    def binarySearch(a, x, lo=0, hi=None):
        hi = hi or len(a)
        pos = bisect_left(a, x, lo, hi)
        return pos if pos != hi and a[pos] == x else -1

    @staticmethod
    def deleteDuplicates(items):
        i = 1
        while i < len(items):
            if items[i]['id'] == items[i - 1]['id']:
                items.pop(i)
                i -= 1
            i += 1
