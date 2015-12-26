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


class DecaParser:
    def __init__(self):
        self.jsonData = []
        self.items = []

    def getProducts(self):
        with open(Utils.getConfig()['subcatFile']) as json_file:
            self.jsonData = json.load(json_file)
        for cat in self.jsonData:
            print cat['url']
            try:
                self.parse(cat['subId'], cat['url'].encode('utf-8') + "/I-Page1_10000")
            except urllib2.HTTPError as httpError:
                print httpError
                if str(httpError.code)[0] == '5':
                    self.parse(cat['subId'], cat['url'].encode('utf-8') + "/I-Page1_10000")
        self.items = sorted(self.items, key=lambda k: (k['id']))
        Utils.deleteDuplicates(self.items)
        Utils.saveJsonFile(Utils.getConfig()['productFile'], self.items)

    def parse(self, subId, url):
        content = urllib2.urlopen(url).read()
        response = html.fromstring(content)
        for sel in response.xpath('//li[@class="product product_normal"]'):
            try:
                item = {'id': sel.xpath('@data-product-id')[0], 'price': sel.xpath('@data-product-price')[0],
                        'url': sel.xpath('div//a[@class="product_name"]/@href')[0],
                        'avail': sel.xpath('div//p[@class="product_info_dispo"]/a/@class')[0], 'cat': subId}
                # item['name'] = sel.xpath('@data-product-name')[0]
                # item['descr'] = sel.xpath('div//img/@alt').extract()[0]
                try:
                    item['oldPr'] = sel.xpath('div//span[@class="old_price left "]/text()')[0]
                    item['disc'] = sel.xpath('div//span[@class="oldPrice-percentage"]/text()')[0]
                except IndexError:
                    # print "Item without discount: "+item['id']+" "+item['name']
                    pass
                self.items.append(item)
            except IndexError:
                print "Skipped item: " + item['id']
                continue


if __name__ == "__main__":
    proc = DecaParser()
    proc.getProducts()
    print "Done"
