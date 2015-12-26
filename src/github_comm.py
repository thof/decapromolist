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

from subprocess import call
import os
from utils import Utils
from prepare_results import PrepareResults


class GithubComm:
    def __init__(self):
        pass

    def commitChanges(self):
        os.chdir(Utils.getConfig()['decapromolistDir'])
        print call("pwd", shell=True)
        print call("git add decapromolist/", shell=True)
        print call("git add category/", shell=True)
        call("git commit -m 'delta {}-{}'".format(PrepareResults.datePrevProcFormatted,
                                                  PrepareResults.dateFormatted), shell=True)
        call("git push -u origin master", shell=True)


if __name__ == "__main__":
    comm = GithubComm()
    comm.commitChanges()
