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

import json
import urllib2
from lxml import html
from utils import Utils


class GetSubcategories:
    def __init__(self):
        self.catUrl = []

    def getCategories(self):
        categories = []
        content = urllib2.urlopen(Utils.getConfig()['siteURL']).read()
        response = html.fromstring(content)
        for cat in response.xpath('//li/@primarycategoryid'):
            if cat not in categories:
                categories.append(cat)
        for cat in categories:
            url = "{}/pl/getSubNavigationMenu?primaryCategoryId=".format(Utils.getConfig()['siteURL']) + cat
            self.catUrl.append(url)

    def getSubcategories(self):
        dataCat = []
        for url in self.catUrl:
            content = urllib2.urlopen(url).read()
            jsonData = json.loads(content)
            for cat in jsonData['category']['categories']:
                for subcat in cat['categories']:
                    data = {'id': long(cat['id']), 'name': cat['label'], 'subId': long(subcat['id']),
                            'subName': subcat['label'], 'url': Utils.getConfig()['siteURL'] + subcat['uri']}
                    dataCat.append(data)
        Utils.renameFile(Utils.getConfig()['subcatFile'])
        Utils.saveJsonFile(Utils.getConfig()['subcatFile'], dataCat)


if __name__ == "__main__":
    proc = GetSubcategories()
    proc.getCategories()
    proc.getSubcategories()
    print "Done"
