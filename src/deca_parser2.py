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
import time
import urllib2
import re

from lxml import html
from utils import Utils
from get_subcategories import GetSubcategories


class DecaParser2:
    def __init__(self):
        self.items = []
        self.counter = 0

    def getProducts(self):
        with open(Utils.getConfig()['subcatFile']) as json_file:
            jsonData = json.load(json_file)
        self.getProductsByCat(jsonData)
        self.items = sorted(self.items, key=lambda k: (k['id']))
        # Utils.saveJsonFile(Utils.getConfig()['subcatFile'], jsonData)
        Utils.deleteDuplicates(self.items)
        Utils.saveJsonFile(Utils.getConfig()['productFile'], self.items)

    def getProductsByCat(self, subcat):
        for index, cat in enumerate(subcat):
            print cat['url']
            self.counter = 0
            url = "https://www.decathlon.pl/pl/getAjaxListProductNextPage?uriPage=/C-{}/I-Page1_3600".format(cat['subId'])
            print(url)
            while True:
                try:
                    self.parse(cat['subId'], url)
                    break
                except EmptyPayload:
                    print('Empty payload!')
                    time.sleep(3)
                    continue
            # page = 0
            # while True:
            #     page += 1
            #     if page == 1:
            #         url = "http://www.decathlon.pl/C-{}".format(cat['subId'])
            #     else:
            #         url = "http://www.decathlon.pl/pl/getAjaxListProductNextPage?uriPage=/C-{}/I-Page{}_40".format(cat['subId'], page)
            #     # print url
            #     try:
            #         self.parse(cat['subId'], url)
            #     except urllib2.HTTPError as httpError:
            #         print httpError
            #         print url
            #         if str(httpError.code)[0] == '5':
            #             self.parse(cat['subId'], url)
            #         else:
            #             break
            #     except IndexError:
            #         if page == 1:
            #             print 'Primary category: '+url
            #         #     urlCat = "{}/pl/getSubNavigationMenu?primaryCategoryId={}".format(
            #         #         Utils.getConfig()['siteURL'], cat['subId'])
            #         #     print "*** Let's try to seek deeper {}".format(url)
            #         #     dataCat = GetSubcategories.getThirdLevelCat([urlCat])
            #         #     subcat[index+1:index+1] = dataCat
            #         #     self.getProductsByCat(dataCat)
            #         break
            print "{} {}".format(cat['url'].encode('utf-8'), self.counter)

    def parse(self, subId, url):
        productCnt = 0
        # content = urllib2.urlopen(url).read()
        content = Utils.safe_call(url)
        content = content.rstrip()
        if not content:
            raise EmptyPayload
        response = html.fromstring(content)

        for sel in response.xpath('//div[@data-product-id]'):
            if not sel.attrib['data-product-id']:
                continue
            if 'data-product-availability' not in sel.attrib or sel.attrib['data-product-availability'] == 0:
                print('Not available https://decathlon.pl/{}'.format(sel.attrib['data-product-href']))
                continue
            item = {'id': int(sel.attrib['data-product-id']), 'price': float(sel.attrib['data-product-price']),
                    'cat': subId, 'url': sel.attrib['data-product-href'], 'img': sel.attrib['data-product-picture-url']}
            try:
                old_price = sel.attrib['data-product-crossed-price']
                item['oldPr'] = float(''.join(filter(lambda x: x.isdigit() or x=='.', old_price)))
                item['disc'] = int(filter(str.isdigit, sel.attrib['data-product-price-percent']))
            except KeyError:
                # print "Item without discount: "+item['id']+" "+item['name']
                pass
            #print(item)
            self.items.append(item)
            productCnt += 1
            self.counter += 1

        for sel in response.xpath('//li[@data-product-id]'):
            if not sel.attrib['data-product-id']:
                continue
            if 'data-product-availability' not in sel.attrib or sel.attrib['data-product-availability'] == 0:
                print('Not available http://decathlon.pl/{}'.format(sel.attrib['data-product-href']))
                continue
            item = {'id': int(sel.attrib['data-product-id']), 'price': float(sel.attrib['data-product-price']),
                    'cat': subId, 'url': str(sel.xpath('a[contains(@class, "thumbnail-link")]/@href')[0]), 'img': sel.attrib['data-product-imgurl']}
            try:
                old_price = sel.xpath('.//span[contains(@class, "old-price crossed")]/text()')[0].strip()
                if not old_price:
                    raise IndexError
                item['oldPr'] = float(''.join(filter(lambda x: x.isdigit() or x == '.', old_price)))
                discount = sel.xpath('.//span[@class="old-price-percentage"]/text()')[0].strip()
                item['disc'] = int(filter(str.isdigit, discount))
            except IndexError:
                # print "Item without discount: "+item['id']+" "+item['name']
                pass
            self.items.append(item)
            productCnt += 1
            self.counter += 1


class EmptyPayload(Exception):
    pass


if __name__ == "__main__":
    proc = DecaParser2()
    proc.getProducts()
    print "Done"
