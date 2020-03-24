# ytcc - The YouTube channel checker
# Copyright (C) 2019  Wolfgang Popp
#
# This file is part of ytcc.
#
# ytcc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ytcc is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ytcc.  If not, see <http://www.gnu.org/licenses/>.

"""Youtube Channel Monitor.

Command Line tool to monitor your favorite YouTube channels without
signing up for a Google account.
"""

__license__ = "GPLv3"
__version__ = "1.8.1"
__author__ = __maintainer__ = "Marc Levine"
__email__ = "marc@3sys.com"

from pathlib import Path
import gettext
import sys


def _get_translations_path() -> str:
    path = Path(__file__)
    path = path.parent.joinpath("resources", "locale")
    if path.is_dir():
        return str(path)

    return sys.prefix + "/share/locale"


gettext.bindtextdomain("ytcm", _get_translations_path())
gettext.textdomain("ytcm")
_ = gettext.gettext
