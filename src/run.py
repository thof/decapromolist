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

from get_subcategories import GetSubcategories
from deca_parser import DecaParser
from process_data import ProcessData
from prepare_results import PrepareResults
from github_comm import GithubComm


class Run:
    def __init__(self):
        pass

    print "Getting subcategories..."
    subcat = GetSubcategories()
    subcat.getCategories()
    subcat.getSubcategories()
    print "Done"

    print "Preparing product list..."
    parser = DecaParser()
    parser.getProducts()
    print "Done"

    print "Processing data..."
    proc = ProcessData()
    proc.parseFile()
    print "Done"

    print "Preparing results list..."
    res = PrepareResults()
    res.getPrevProcDate()
    res.preparePromoList()
    res.prepareRegularList()
    print "Więcej informacji: https://github.com/thof/decapromolist#decapromolist"
    print "PayPal: _decapromolist@gmail.com_ (w razie gdyby ktoś chciał wspomóc projekt)"
    res.finish()()

    print "Commiting changes..."
    comm = GithubComm()
    comm.commitChanges()
