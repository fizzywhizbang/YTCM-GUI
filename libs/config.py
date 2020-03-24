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

import configparser
import io
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Iterable

from libs.database import Video, Channel
from libs.exceptions import BadConfigException

DEFAULTS: Dict[str, Dict[str, Any]] = {
    "YTCM": {
        "DBPath": "db/ytcm.db",
        "DownloadDir": "Downloads",
        "alphabet": "sdfervghnuiojkl",
        "orderBy": "channel, date",
        "watcherdir": "folderwatch/",
        "YTPrefix" : "https://www.youtube.com/channel/",
        "RSSPrefix" : "https://www.youtube.com/feeds/videos.xml?channel_id=",
        "watchPrefix" : "https://www.youtube.com/watch?v=",
        "updatetime" : 60,
        "serverdir" : "",
        "statuslog" : "logs/status_log.txt",
        "standalone" : True
    },
    "color": {
        "promptDownloadAudio": 2,
        "promptDownloadVideo": 4,
        "promptPlayAudio": 2,
        "promptPlayVideo": 4,
        "promptMarkWatched": 1,
        "tableAlternateBackground": 245,
    },
    "youtube-dl": {
        "format": "bestvideo+bestaudio/best",
        "outputTemplate": "%(title)s.%(ext)s",
        "loglevel": "normal",
        "ratelimit": 0,
        "retries": 0,
        "subtitles": "off",
        "thumbnail": "on",
        "skipLiveStream": "yes"
    },
    "TableFormat": {
        "ID": "on",
        "Date": "off",
        "Channel": "on",
        "Title": "on",
        "URL": "off",
        "Watched": "off"
    },
    "GUI" : {
        "bgcolor": "#dddddd",
        "good": "#b3ff99",
        "textBoxWidth": "40",
        "textBoxWidthLG": "60",
        "fontSize": "14",
        "fontHeader": "16",
        "mousebuttons": "2",
        "refreshimage": "images/arrow_refresh.png"
    }
}


def _get_config(override_cfg_file: Optional[str] = None) -> configparser.ConfigParser:
    """Read config file from several locations.

    Searches at following locations:
    1. ``override_cfg_file``
    2. ``$XDG_CONFIG_HOME/YTCM/YTCM.conf``
    3. ``~/.config/ytcm/ytcm.conf``
    4. ``~/.ytcm.conf``

    If no config file is found in these three locations, a default config file is created in
    ``~/.config/ytcm/ytcm.conf``

    :param override_cfg_file: Read the config from this file.
    :return: The dict-like config object
    """
    config_dir = os.getenv("XDG_CONFIG_HOME")
    if not config_dir:
        config_dir = "config"

    global_cfg_file = "/etc/ytcm/ytcm.conf"
    default_cfg_file = os.path.expanduser(config_dir + "/ytcm.conf")
    fallback_cfg_file = os.path.expanduser("~/.ytcm.conf")

    config = configparser.ConfigParser(interpolation=None)
    config.read_dict(DEFAULTS)

    cfg_file_locations = [global_cfg_file, default_cfg_file, fallback_cfg_file]
    if override_cfg_file:
        cfg_file_locations.append(override_cfg_file)

    if not config.read(cfg_file_locations):
        path = Path(default_cfg_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        with path.open("w") as conf_file:
            config.write(conf_file)

    return config


class Config:
    """Handles the ini-based configuration file."""

    def __init__(self, override_cfg_file: Optional[str] = None) -> None:
        super(Config, self).__init__()
        config = _get_config(override_cfg_file)
        self._config = config
        gui = config["GUI"]
        ytcm = config["YTCM"]

        self.download_dir = os.path.expanduser(ytcm["DownloadDir"])
        self.db_path = ytcm["serverdir"] + ytcm["dbpath"]
        self.quickselect_alphabet = set(ytcm["alphabet"])
        self.table_format = config["TableFormat"]
        self.youtube_dl = _YTDLConf(config["youtube-dl"])
        self.order_by = list(self.init_order())
        self.color = _ColorConf(config["color"])
        self.watcherdir = os.path.expanduser(ytcm["watcherdir"])
        self.updatetime = ytcm["updatetime"]
        self.RSSPrefix = ytcm["RSSPrefix"]
        self.YTPrefix = ytcm["YTPrefix"]
        self.watchPrefix = ytcm["watchPrefix"]
        self.statuslog = ytcm["statuslog"]
        self.standalone = ytcm["standalone"]
        self.serverdir = ytcm["serverdir"]

        self.bgcolor = gui["bgcolor"]
        self.good = gui["good"]
        self.textBoxWidth = gui["textBoxWidth"]        
        self.textBoxWidthLG = gui["textBoxWidthLG"]
        self.fontSize = gui["fontSize"]
        self.fontHeader = gui["fontHeader"]
        self.mousebuttons = gui["mousebuttons"]
        self.refreshimage = gui["refreshimage"]

    def init_order(self) -> Iterable[Any]:
        col_mapping = {
            "id": Video.id,
            "date": Video.publish_date,
            "channel": Channel.displayname,
            "title": Video.title,
            "url": Video.yt_videoid,
            "watched": Video.watched
        }
        for key in self._config["YTCM"]["orderBy"].split(","):
            sort_spec = list(map(lambda s: s.strip().lower(), key.split(":")))
            col = sort_spec[0]
            desc = ""

            if len(sort_spec) == 2:
                desc = sort_spec[1]

            column = col_mapping.get(col)
            if column is not None:
                column = column.collate("NOCASE")
                yield column.desc() if desc == "desc" else column
            else:
                raise BadConfigException(f"Cannot order by {key.strip()}")

    def __str__(self) -> str:
        strio = io.StringIO()
        self._config.write(strio)
        return strio.getvalue()


class _ColorConf:
    def __init__(self, subconf: Any) -> None:
        super(_ColorConf, self).__init__()
        self.prompt_download_audio = int(subconf["promptDownloadAudio"])
        self.prompt_download_video = int(subconf["promptDownloadVideo"])
        self.prompt_play_audio = int(subconf["promptPlayAudio"])
        self.prompt_play_video = int(subconf["promptPlayVideo"])
        self.prompt_mark_watched = int(subconf["promptMarkWatched"])
        self.table_alternate_background = int(subconf["tableAlternateBackground"])


class _YTDLConf:
    def __init__(self, subconf: Any) -> None:
        super(_YTDLConf, self).__init__()
        self.format = subconf["format"]
        self.output_template = subconf["outputTemplate"]
        self.loglevel = subconf["loglevel"]
        self.retries = float(subconf["retries"])  # float to set indefinetly many retires
        self.subtitles = subconf["subtitles"]
        self.thumbnail = subconf.getboolean("thumbnail")
        self.skip_live_stream = subconf.getboolean("skipLiveStream")

        limit = int(subconf["ratelimit"])
        self.ratelimit = limit if limit > 0 else None
