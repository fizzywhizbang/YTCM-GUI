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

import argparse
import os
from datetime import datetime

import libs.cli
from libs import _


def is_directory(string: str) -> str:
    if not os.path.isdir(string):
        msg = _("{!r} is not a directory").format(string)
        raise argparse.ArgumentTypeError(msg)

    return string


def is_date(string: str) -> datetime:
    try:
        return datetime.strptime(string, "%Y-%m-%d")
    except ValueError:
        msg = _("{!r} is not a valid date").format(string)
        raise argparse.ArgumentTypeError(msg)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=_("Command Line tool to monitor your favorite YouTube channels"
                      "The --list, --watch, --download, --mark-watched options can be "
                      "combined with filter options --channel-filter, --include-watched, --since,"
                      " --to"))

    parser.add_argument("-a", "--add-channel",
                        help=_("add a new channel. NAME is the name displayed by ytcc. DLDIR is the download directory under the folder defined in ytcc.conf URL is the "
                               "url of the channel's front page or the URL of any video published "
                               "by the channel"),
                        nargs=3,
                        metavar=("NAME", "DLDIR", "URL"))

    parser.add_argument("-c", "--list-channels",
                        help=_("print a list of all subscribed channels"),
                        action="store_true")

    parser.add_argument("-r", "--delete-channel",
                        help=_("unsubscribe from the channel identified by 'NAME'"),
                        metavar="NAME",
                        nargs='+',
                        type=str)

    parser.add_argument("--rename",
                        help=_("rename channel 'OLDNAME' to 'NEWNAME'"),
                        metavar=("OLDNAME", "NEWNAME"),
                        nargs=2,
                        type=str)

    parser.add_argument("-u", "--update",
                        help=_("update the video list"),
                        action="store_true")

    parser.add_argument("-ua", "--updatearchive",
                        help=_("check archived chanels for updates and move them to monitored"),
                        action="store_true")

    parser.add_argument("-uo", "--updateone",
                        help=_("Update one channel include channel youtube ID"),
                        nargs=1,
                        metavar="CHANNEL_ID")

    parser.add_argument("-l", "--list",
                        help=_("print a list of videos that match the criteria given by the "
                               "filter options"),
                        action="store_true")

    parser.add_argument("-d", "--download",
                        help=_("download the videos identified by 'ID'. The videos are saved "
                               "in $HOME/Downloads by default. Omitting the ID will download "
                               "all videos that match the criteria given by the filter options"),
                        nargs="*",
                        type=int,
                        metavar="ID")

    parser.add_argument("-m", "--mark-downloaded",
                        help=_("mark videos identified by ID as downloaded. Omitting the ID will mark"
                               " all videos that match the criteria given by the filter options as "
                               "downloaded"),
                        nargs='*',
                        type=int,
                        metavar="ID")

    parser.add_argument("-f", "--channel-filter",
                        help=_("plays, lists, marks, downloads only videos from channels defined "
                               "in the filter"),
                        nargs='+',
                        type=str,
                        metavar="NAME")

    parser.add_argument("-n", "--include-watched",
                        help=_("include already watched videos to filter rules"),
                        action="store_true")

    parser.add_argument("-s", "--since",
                        help=_("includes only videos published after the given date"),
                        metavar="YYYY-MM-DD",
                        type=is_date)

    parser.add_argument("-t", "--to",
                        help=_("includes only videos published before the given date"),
                        metavar="YYYY-MM-DD",
                        type=is_date)

    parser.add_argument("-p", "--path",
                        help=_("set the download path to PATH"),
                        metavar="PATH",
                        type=is_directory)

    parser.add_argument("-g", "--no-description",
                        help=_("do not print the video description before playing the video"),
                        action="store_true")

    parser.add_argument("-o", "--columns",
                        help=_("specifies which columns will be printed when listing videos. COL "
                               "can be any of {columns}. All columns can be enabled with "
                               "'all'").format(columns=libs.cli.TABLE_HEADER),
                        nargs='+',
                        metavar="COL",
                        choices=["all", *libs.cli.TABLE_HEADER])

    parser.add_argument("--import-from",
                        help=_("import YouTube channels from YouTube's subscription export "
                               "(available at https://www.youtube.com/subscription_manager)"),
                        metavar="PATH",
                        type=argparse.FileType("r"))

    parser.add_argument("--export-to",
                        help=_("export YouTube channels in opml format"),
                        metavar="PATH",
                        type=argparse.FileType("wb"))

    parser.add_argument("--cleanup",
                        help=_("removes old videos from the database and shrinks the size of the "
                               "database file"),
                        action="store_true")

    parser.add_argument("-v", "--version",
                        help=_("output version information and exit"),
                        action="store_true")

    parser.add_argument("--bug-report-info",
                        help=_("print info to include in a bug report"),
                        action="store_true")

    return parser.parse_args()
