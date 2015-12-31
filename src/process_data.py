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
import re
import MySQLdb as mdb
import sys
import datetime
import time
from utils import Utils


class ProcessData:
    def __init__(self):
        self.products = []
        self.dateTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # self.dateTime = "2015-08-26 20:50:00"

    PROD_NEW = 0
    PROD_HIGHER_PRICE = 1
    PROD_LOWER_PRICE = 2
    PROD_WITHDRAW = 3
    PROD_RETURN = 4
    PROD_RETURN_HIGHER_PRICE = 5
    PROD_RETURN_LOWER_PRICE = 6
    PROD_NOT_AVAIL = "infobulle dispo dispo-03"

    def parseFile(self):
        print 'Parsing product file...'
        productsRegular = []
        productsPromo = []
        # open products file and process items
        with open(Utils.getConfig()['productFile']) as json_file:
            json_data = json.load(json_file)
        for item in json_data:
            product = {}
            # not available products are omitted
            if item['avail'] == self.PROD_NOT_AVAIL:
                continue
            product['id'] = long(item['id'])
            product['price'] = float(item['price'])
            product['category'] = item['cat']
            # product['name'] = data['name'].encode('utf-8')
            product['url'] = item['url'].encode('utf-8')
            # in case of regular product add it to separate table
            if item.get('oldPr', None) is None:
                product['date'] = self.dateTime[:10]
                productsRegular.append(product)
            else:
                product['old_price'] = item['oldPr']
                product['discount'] = item['disc']
                # product['description'] = data['descr'].encode('utf-8')
                product['url'] = item['url'].encode('utf-8')
                productsPromo.append(product)
        self.updateRegularProducts(productsRegular)
        self.updatePromoProducts(productsPromo)
        Utils.renameFile(Utils.getConfig()['productFile'])

    def updateRegularProducts(self, productRegular):
        print 'Updating prices for regular products...'
        try:
            con = mdb.connect(Utils.getConfig()['host'], Utils.getConfig()['user'],
                              Utils.getConfig()['passwd'], Utils.getConfig()['dbname'])
            cur = con.cursor(mdb.cursors.DictCursor)
            # select the most recent records for each product
            start = time.time()
            # ids = ''
            # for prod in productRegular:
            #     ids = ids + str(prod['id']) + ','
            # ids = ids[:-1]
            # cur.execute("SELECT p1.* FROM product_price p1 LEFT JOIN product_price p2 \
            #             ON (p1.id = p2.id AND p1.date < p2.date) WHERE p2.date IS NULL AND p1.id IN ({})".format(ids))
            cur.execute("SELECT * FROM product_price")
            productRegularDB = cur.fetchall()
            end = time.time()
            print "Query time: {}".format(end - start)
            # sort by date (descending) and by product ID
            productRegularDB = sorted(productRegularDB, key=lambda k: (k['date']), reverse=True)
            productRegularDB = sorted(productRegularDB, key=lambda k: (k['id']))
            Utils.deleteDuplicates(productRegularDB)
            idArray = Utils.buildArray(productRegularDB)

            for product in productRegular:
                index = Utils.binarySearch(idArray, product['id'])
                # insert a new product record if it hasn't occurred before or the price has changed 
                if index == -1 or productRegularDB[index]['price'] != product['price']:
                    cur.execute("INSERT INTO product_price (id, date, price, category, url) \
                    VALUES ({}, \"{}\", {}, {}, \"{}\")".format(product['id'], product['date'], product['price'],
                                                                product['category'], product['url']))
        except mdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            sys.exit(1)
        finally:
            if con:
                con.close()

    def updatePromoProducts(self, productsPromo):
        print 'Updating prices for promoted products...'
        try:
            con = mdb.connect(Utils.getConfig()['host'], Utils.getConfig()['user'],
                              Utils.getConfig()['passwd'], Utils.getConfig()['dbname'])
            cur = con.cursor(mdb.cursors.DictCursor)
            # get records for promoted products
            cur.execute('SELECT * FROM product_promo')
            productPromoDB = cur.fetchall()
            productPromoDB = sorted(productPromoDB, key=lambda k: (k['id']))
            prodBool = [False] * len(productPromoDB)
            idArray = Utils.buildArray(productPromoDB)

            for product in productsPromo:
                index = Utils.binarySearch(idArray, product['id'])
                if index == -1:
                    # insert a new record
                    cur.execute("INSERT INTO product_promo (id, category, price, old_price, discount, first_date, \
                        last_date, operation, prev_price, url) \
                        VALUES ({},{},{},{},{},\"{}\",\"{}\",{},{},\"{}\")".format(product['id'],
                                                                                   product['category'],
                                                                                   product['price'],
                                                                                   product['old_price'],
                                                                                   product['discount'],
                                                                                   self.dateTime, self.dateTime,
                                                                                   self.PROD_NEW, 0.0, product['url']))
                else:
                    # update existing record
                    prodBool[index] = True
                    # determine type of operation
                    if productPromoDB[index]['operation'] == self.PROD_WITHDRAW:
                        if productPromoDB[index]['price'] == product['price']:
                            product['operation'] = self.PROD_RETURN
                        elif productPromoDB[index]['price'] > product['price']:
                            product['operation'] = self.PROD_RETURN_LOWER_PRICE
                        elif productPromoDB[index]['price'] < product['price']:
                            product['operation'] = self.PROD_RETURN_HIGHER_PRICE
                    elif productPromoDB[index]['price'] > product['price']:
                        product['operation'] = self.PROD_LOWER_PRICE
                    elif productPromoDB[index]['price'] < product['price']:
                        product['operation'] = self.PROD_HIGHER_PRICE

                    product['operation'] = product.get('operation', None)
                    if product['operation'] is not None:
                        cur.execute("UPDATE product_promo SET category={}, price={}, old_price={}, \
                            discount={}, last_date=\"{}\", operation={}, prev_price={}, url=\"{}\" WHERE id={}".format(
                                product['category'],
                                product['price'], product['old_price'], product['discount'], self.dateTime,
                                product['operation'],
                                productPromoDB[index]['price'], product['url'], product['id']))

            for index, boolVal in enumerate(prodBool):
                # additionally record with discontinued promo should be marked
                if boolVal is False and productPromoDB[index]['operation'] != self.PROD_WITHDRAW:
                    cur.execute(
                            "UPDATE product_promo SET category={}, last_date=\"{}\", operation={} WHERE id={}".format(
                                    productPromoDB[index]['category'], self.dateTime,
                                    self.PROD_WITHDRAW, productPromoDB[index]['id']))
        except mdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            sys.exit(1)
        finally:
            if con:
                con.close()


if __name__ == "__main__":
    proc = ProcessData()
    proc.parseFile()
    print "Done"
