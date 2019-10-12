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
from deca_parser2 import DecaParser2
from process_data import ProcessData
from prepare_results import PrepareResults
from github_comm import GithubComm


class Run:
    def __init__(self):
        pass

    print "Getting subcategories..."
    subcat = GetSubcategories()
    dataCat = subcat.getCategories2()
    subcat.saveSubcategories(dataCat)
    print "Done"

    print "Preparing products list..."
    parser = DecaParser2()
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
    res.finish()

    print "Commiting changes..."
    comm = GithubComm()
    comm.commitChanges()
