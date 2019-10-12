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
import re

from lxml import html
from utils import Utils
from get_subcategories import GetSubcategories


class DecaParser:
    def __init__(self):
        self.items = []
        self.counter = 0

    def getProducts(self):
        with open(Utils.getConfig()['subcatFile']) as json_file:
            jsonData = json.load(json_file)
        self.getProductsByCat(jsonData)
        self.items = sorted(self.items, key=lambda k: (k['id']))
        Utils.saveJsonFile(Utils.getConfig()['subcatFile'], jsonData)
        Utils.deleteDuplicates(self.items)
        Utils.saveJsonFile(Utils.getConfig()['productFile'], self.items)

    def getProductsByCat(self, subcat):
        for index, cat in enumerate(subcat):
            #print cat['url']
            self.counter = 0
            page = 0
            while True:
                page += 1
                url = cat['url'].encode('utf-8') + "/I-Page{}_40".format(page)
                print url
                try:
                    self.parse(cat['subId'], url)
                except urllib2.HTTPError as httpError:
                    print httpError
                    if str(httpError.code)[0] == '5':
                        self.parse(cat['subId'], url)
                    else:
                        break
                except IndexError:
                    if page == 1:
                        urlCat = "{}/pl/getSubNavigationMenu?primaryCategoryId={}".format(
                            Utils.getConfig()['siteURL'], cat['subId'])
                        print "We need to go deeper"
                        dataCat = GetSubcategories.getThirdLevelCat([urlCat])
                        subcat[index+1:index+1] = dataCat
                        self.getProductsByCat(dataCat)
                    break
            print "*** {} {}\n".format(cat['url'].encode('utf-8'), self.counter)

    def parse(self, subId, url):
        productCnt = 0
        content = urllib2.urlopen(url).read()
        response = html.fromstring(content)
        response.xpath('//li[@class="product product_normal"]')[0]
        for sel in response.xpath('//li[@class="product product_normal"]'):
            try:
                item = {}
                item['id'] = sel.xpath('@data-product-id')[0]
            except IndexError:
                print "Skipped wrong category"
                continue
            try:
                item['price'] = sel.xpath('@data-product-price')[0]
                item['url'] = sel.xpath('div//a[@class="product_name"]/@href')[0]
                #item['avail'] = sel.xpath('div//p[@class="product_info_dispo"]/a/@class')[0],
                item['cat'] = subId
                # item['name'] = sel.xpath('@data-product-name')[0]
                # item['descr'] = sel.xpath('div//img/@alt').extract()[0]
                try:
                    item['oldPr'] = sel.xpath('div//span[@class="old_price"]/text()')[0]
                    item['oldPr'] = re.match('([0-9,]+)', item['oldPr']).group(1)
                    item['oldPr'] = float(''.join(item['oldPr'].split()).replace(",", "."))
                    item['disc'] = int(re.findall(r'\d+', sel.xpath('div//span[@class="oldPrice-percentage"]/text()')[0])[0])
                except IndexError:
                    # print "Item without discount: "+item['id']+" "+item['name']
                    pass
                self.items.append(item)
                productCnt += 1
                self.counter += 1
            except IndexError:
                print "Skipped item: " + item['id']
                continue
        #print "Product read: {}".format(productCnt)

if __name__ == "__main__":
    proc = DecaParser()
    proc.getProducts()
    print "Done"
