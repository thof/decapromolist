# -*- coding: utf-8 -*-
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

from __future__ import print_function
import json
# import MySQLdb as mdb
import mysql.connector
import sys
import datetime
import urllib2
from lxml import html
from utils import Utils
from process_data import ProcessData


class PrepareResults:
    dateFormatted = datetime.datetime.now().strftime("%d.%m.%Y")
    datePrevProcFormatted = datetime.date.fromordinal(datetime.date.today().toordinal() - 1).strftime("%d.%m.%Y")
    dateTime = datetime.datetime.now().strftime("%Y-%m-%d 00:00:01")
    # dateTime = "2019-11-18 00:00:01"
    SPACES = "  "

    def __init__(self):
        self.products = []
        Utils.renameFile(Utils.getConfig()['decapromolistMDFile'])
        self.mdFile = open(Utils.getConfig()['decapromolistMDFile'],'w')
        with open(Utils.getConfig()['subcatFile']) as jsonFile:
            self.subcatData = json.load(jsonFile)

    @staticmethod
    def operationToDescr(argument, prevPrice):
        switcher = {
            0: "Nowa",
            1: "Wyższa cena z " + prevPrice,
            2: "Niższa cena z " + prevPrice,
            3: "Wycofana",
            4: "Powrót",
            5: "Powrót z wyższą ceną z " + prevPrice,
            6: "Powrót z niższą ceną z " + prevPrice,
            7: "Obniżka"
        }
        return switcher.get(argument, "Error")

    def getPrevProcDate(self):
        # get date of the previous processing
        try:
            # con = mdb.connect(Utils.getConfig()['host'], Utils.getConfig()['user'],
            #                   Utils.getConfig()['passwd'], Utils.getConfig()['dbname'])
            # cur = con.cursor(mdb.cursors.DictCursor)
            con = mysql.connector.connect(host=Utils.getConfig()['host'], user=Utils.getConfig()['user'],
                                          passwd=Utils.getConfig()['passwd'], database=Utils.getConfig()['dbname'])
            cur = con.cursor(dictionary=True)
            cur.execute("SELECT last_date FROM product_promo WHERE last_date < \"{}\" ORDER BY last_date DESC LIMIT 1"
                        .format(self.dateTime))
            row = cur.fetchone()
            self.datePrevProcFormatted = row['last_date'].strftime('%d.%m.%Y')
        except mysql.connector.Error, e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            sys.exit(1)
        finally:
            if con:
                con.close()

    def preparePromoList(self):
        try:
            # con = mdb.connect(Utils.getConfig()['host'], Utils.getConfig()['user'],
            #                   Utils.getConfig()['passwd'], Utils.getConfig()['dbname'])
            # cur = con.cursor(mdb.cursors.DictCursor)
            con = mysql.connector.connect(host=Utils.getConfig()['host'], user=Utils.getConfig()['user'],
                                          passwd=Utils.getConfig()['passwd'], database=Utils.getConfig()['dbname'])
            cur = con.cursor(dictionary=True)
            #             cur.execute('SELECT p1.* FROM product_price p1 LEFT JOIN product_price p2 \
            #                         ON (p1.id = p2.id AND p1.price > p2.price) WHERE p2.price IS NULL')
            # get all products from DB
            cur.execute("SELECT * FROM product_price")
            productPriceDB = cur.fetchall()
            productPriceDB = sorted(productPriceDB, key=lambda k: (k['date'], k['price']))
            Utils.deleteDuplicates(productPriceDB)
            # get promoted products added today but skip discontinued items
            cur.execute(
                    'SELECT * FROM product_promo WHERE operation != {} AND last_date > \"{}\" ORDER BY '
                    'operation ASC, discount DESC'.format(
                            ProcessData.PROD_WITHDRAW, self.dateTime))
            productPromoDB = cur.fetchall()

            print("#decapromolist lista promowanych produktów (delta {}-{}):".format(self.datePrevProcFormatted,
                                                                             self.dateFormatted), file=self.mdFile)

            index_tmp=0
            for cat in self.subcatData:
                # checked whether the list contains at least one product belonging to processed subcategory
                rowCat = next((row for row in productPromoDB if row['category'] == cat['subId']), None)
                if rowCat is None:
                    continue
                else:
                    catStr = "\nKategoria: " + cat['subName'].encode('utf-8')
                    # catStr = "\nKategoria: " + cat['name'].encode('utf-8') + "->" + cat['subName'].encode('utf-8')
                # process promoted items
                for row in productPromoDB:
                    # when a product doesn't belong to considered subcategory skip to the next one
                    if row['category'] != cat['subId']:
                        continue

                    index_tmp=index_tmp+1
                    if index_tmp == 308:
                        print('break')
                    print(index_tmp)
                    product = self.process_item(row, cat)
                    if not product:
                        continue

                    # additional check to be sure that the current price is the lowest to this day
                    # (checking "price history")
                    prodLowestPrice = next((prodLowestPrice for prodLowestPrice in productPriceDB if
                                            prodLowestPrice['id'] == row['id'] and prodLowestPrice['price'] < row[
                                                'price']), None)
                    if prodLowestPrice is not None:
                        # text = text + " [Regularna cena była niższa {} w dn. {}]".format(prodLowestPrice['price'],
                        #                                                                  prodLowestPrice['date'])
                        product['rp'] = prodLowestPrice['price']
                        product['rd'] = prodLowestPrice['date'].strftime("%d.%m.%Y")

                    self.products.append(product)
        except mysql.connector.Error, e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            sys.exit(1)
        finally:
            if con:
                con.close()

    def prepareRegularList(self):
        try:
            # con = mdb.connect(Utils.getConfig()['host'], Utils.getConfig()['user'],
            #                   Utils.getConfig()['passwd'], Utils.getConfig()['dbname'])
            # cur = con.cursor(mdb.cursors.DictCursor)
            con = mysql.connector.connect(host=Utils.getConfig()['host'], user=Utils.getConfig()['user'],
                                          passwd=Utils.getConfig()['passwd'], database=Utils.getConfig()['dbname'])
            cur = con.cursor(dictionary=True)
            # get all products from DB collected today
            cur.execute("SELECT * FROM product_price WHERE date = \"{}\"".format(self.dateTime[:10]))
            productCurrentPrice = cur.fetchall()

            ids = ''
            for prod in productCurrentPrice:
                ids = ids + str(prod['id']) + ','
            ids = ids[:-1]
            # get all products from DB for IDs fetched in the previous query with date different from today
            cur.execute("SELECT * FROM product_price WHERE date != \"{}\" AND id IN ({})".format(self.dateTime[:10], ids))
            productPrevPrice = cur.fetchall()

            print("\n\nLista przecenionych produktów (delta {}-{}):\n".format(self.datePrevProcFormatted,
                                                                            self.dateFormatted), file=self.mdFile)

            productFinal = []
            # looking for products for which current price is lower than the last one
            for prod in productCurrentPrice:
                prodLast = next((row for row in productPrevPrice if row['id'] == prod['id']), None)
                if prodLast is not None and prod['price'] < prodLast['price']:
                    prod['discount'] = int((1 - prod['price'] / prodLast['price']) * 100)
                    # don't take into account when the discount is 10% or less
                    if not(prod['discount'] >= 10 or prodLast['price'] >=999):
                        continue
                    prod['prev_price'] = prodLast['price']
                    prod['old_price'] = prodLast['price']
                    prod['operation'] = 7
                    productFinal.append(prod)
            productFinal = sorted(productFinal, key=lambda k: (k['discount'], k['price']), reverse=True)

            # prepare information to be printed in a readable form
            for prod in productFinal:
                cat = next((row for row in self.subcatData if row['subId'] == prod['category']), None)
                product = self.process_item(prod, cat)
                if not product:
                    continue

                # additional check to be sure that the current price is the lowest to this day
                # (checking "price history")
                prodLowestPrice = next(
                        (row for row in productPrevPrice if row['id'] == prod['id'] and row['price'] < prod['price']),
                        None)
                if prodLowestPrice is not None:
                    # text = text + " [Regularna cena była niższa {} w dn. {}]".format(prodLowestPrice['price'],
                    #                                                                  prodLowestPrice['date'])
                    product['rp'] = prodLowestPrice['price']
                    product['rd'] = prodLowestPrice['date'].strftime("%d.%m.%Y")
                self.products.append(product)
        except mysql.connector.Error, e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            sys.exit(1)
        finally:
            if con:
                con.close()

    def process_item(self, row, cat):
        product = {}
        male = ["męsk", "mesk"]
        female = ["damsk", "kobie"]
        junior = ["junior", "dziec"]
        juniorYear = ["lat", "ans", "maluszk"]

        url = Utils.getConfig()['siteURL'] + row['url']
        img = Utils.getConfig()['siteURL'] + row['img']
        content = Utils.safe_call(url)
        response = html.fromstring(content)

        # get product information
        nameCheck = ''
        namePosStart = content.find('tc_vars')
        if namePosStart != -1:
            namePosEnd = content.find('/*', namePosStart)
            nameCheck = content[namePosStart:namePosEnd]
            nameCheck = nameCheck.lower()

        # get the product name
        try:
            name = response.xpath('//span[@id="productName"]')[0].text
            if name == name.upper():
                name = name.title().encode('utf-8')
            else:
                name = name.encode('utf-8')
            print(name + " " + url.encode('utf-8'))
        except IndexError:
            print("\Invalid product: {}".format(url))
            return None

        # when a product is out of stock then skip to the next one
        outOfStock = response.xpath('//link[@href="http://schema.org/OutOfStock"]')
        if outOfStock:
            print("Out of stock")
            return None

        # quite vague method to determine the sex
        # (in most cases it works just fine, i.e. when the description is correct)
        label = ''
        labelPosStart = content.find('tc_vars["product_breadcrumb_label"]')
        if labelPosStart != -1:
            labelPosEnd = content.find('");', labelPosStart)
            label = content[labelPosStart + 49:labelPosEnd]
            label = label.lower()
        nameLower = name.lower()
        if any(substring in label for substring in male) == True or \
                any(substring in nameLower for substring in male) == True or \
                any(substring in nameCheck for substring in male) == True:
            sex = "M"
        elif any(substring in label for substring in female) == True or \
                any(substring in nameLower for substring in female) == True or \
                any(substring in nameCheck for substring in female) == True:
            sex = "F"
        elif any(substring in label for substring in junior) == True or \
                any(substring in nameLower for substring in junior) == True or \
                any(substring in nameCheck for substring in junior) == True:
            sex = "J"
        else:
            sex = "U"
        # get list of available sizes
        sizeList = ''
        # product['sz'] = []
        for size in response.xpath('//li[@class=" available"]'):
            sizeStr = size.xpath('a')[0].text
            sizeList = sizeList + sizeStr.strip() + ', '
            # product['sz'].append(sizeStr)
        sizeListLower = sizeList.lower()
        if any(substring in sizeListLower for substring in juniorYear):
            sex = "J"

        if cat['subName'] == cat['subName'].upper():
            cat['subName'] = cat['subName'].title()

        product['sz'] = " " + sizeList[:-2]
        product['sx'] = sex
        product['nm'] = "{}<br><a href=\"{}\"><img src=\"{}\"></a>".format(name, url, img)
        product['sc'] = cat['subName'].encode('utf-8')
        product['pr'] = row['price']
        product['op'] = row['old_price']
        product['dc'] = row['discount']
        product['pp'] = row['prev_price']
        product['or'] = self.operationToDescr(row['operation'], str(row['prev_price']))
        return product

    def finish(self):
        print("Więcej informacji: https://github.com/thof/decapromolist#decapromolist"+self.SPACES, file=self.mdFile)
        print("PayPal: _decapromolist@gmail.com_ (w razie gdyby ktoś chciał wspomóc projekt)"+self.SPACES, file=self.mdFile)
        self.mdFile.close()
        Utils.renameFile(Utils.getConfig()['decapromolistFile'])
        Utils.saveJsonFile(Utils.getConfig()['decapromolistFile'], self.products)


if __name__ == "__main__":
    res = PrepareResults()
    res.getPrevProcDate()
    res.preparePromoList()
    res.prepareRegularList()
    res.finish()
