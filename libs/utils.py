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
from typing import TypeVar, Optional, Callable
import subprocess, time, json, feedparser
from datetime import *
from libs.config import Config
from libs.database import Database
import os.path
from os import path

# pylint: disable=invalid-name
T = TypeVar("T")

config = Config()

def _get_youtube_rss_url(yt_channel_id: str) -> str:
    return f"https://www.youtube.com/feeds/videos.xml?channel_id={yt_channel_id}"


def unpack_optional(elem: Optional[T], default: Callable[[], T]) -> T:
    if elem is None:
        return default()
    return elem

def get_unix_time():
    d = datetime.now()
    ut = d.timestamp()
    return ut

def get_unix_utc(dt,opt="null") -> str:
    d = datetime.strptime( dt, "%Y-%m-%dT%H:%M:%S+00:00" )
    ut = d.timestamp()
    if opt == 'ut':
        return str(int(ut))
    else:
        return d

def get_datatime_from_unix(dt) -> str:
    return str(datetime.fromtimestamp(dt))

def time_diff(past, current) -> int:
    convert_past = datetime.fromtimestamp(round(past))
    convert_current = datetime.fromtimestamp(round(current))
    return round((convert_current - convert_past).total_seconds() / 60)

def check_db_lock() -> bool:
    return (path.exists(config.db_path.replace(".db",".db-journal")))


