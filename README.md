# YTCM2
# YTCM - Youtube Channel Monitor
Youtube downloader loosely based on YTCC and My own implementation of YTCM but for this one there is also a GUI written in Tkinter
Command line tool and GUI written in python to monitor your favorite YT channels without siging up for an account.

This tool will write a watch file for JDownloader to download the video using your preferences in JDownloader for Youtube

Requires python 3.6 or later


For the base code credit goes to https://github.com/woefe/ytcc


:) Yes, I have some code cleanup to do but I'm putting this up here so I can keep from jacking this up too bad :)

# ytcm.py
Running this with -h or --help will give you a list of options
usage: ytcm.py [-h] [-a NAME DLDIR URL] [-c] [-r NAME [NAME ...]] [--rename OLDNAME NEWNAME] [-u] [-ua] [-uo CHANNEL_ID] [-l] [-d [ID [ID ...]]] [-m [ID [ID ...]]] [-f NAME [NAME ...]] [-n] [-s YYYY-MM-DD]
               [-t YYYY-MM-DD] [-p PATH] [-g] [-o COL [COL ...]] [--import-from PATH] [--export-to PATH] [--cleanup] [-v] [--bug-report-info]

Command Line tool to monitor your favorite YouTube channelsThe --list, --watch, --download, --mark-watched options can be combined with filter options --channel-filter, --include-watched, --since, --to

optional arguments:
  -h, --help            show this help message and exit
  -a NAME DLDIR URL, --add-channel NAME DLDIR URL
                        add a new channel. NAME is the name displayed by ytcc. DLDIR is the download directory under the folder defined in ytcc.conf URL is the url of the channel's front page or the URL of any
                        video published by the channel
  -c, --list-channels   print a list of all subscribed channels
  -r NAME [NAME ...], --delete-channel NAME [NAME ...]
                        unsubscribe from the channel identified by 'NAME'
  --rename OLDNAME NEWNAME
                        rename channel 'OLDNAME' to 'NEWNAME'
  -u, --update          update the video list
  -ua, --updatearchive  check archived chanels for updates and move them to monitored
  -uo CHANNEL_ID, --updateone CHANNEL_ID
                        Update one channel include channel youtube ID
  -l, --list            print a list of videos that match the criteria given by the filter options
  -d [ID [ID ...]], --download [ID [ID ...]]
                        download the videos identified by 'ID'. The videos are saved in $HOME/Downloads by default. Omitting the ID will download all videos that match the criteria given by the filter options
  -m [ID [ID ...]], --mark-downloaded [ID [ID ...]]
                        mark videos identified by ID as downloaded. Omitting the ID will mark all videos that match the criteria given by the filter options as downloaded
  -f NAME [NAME ...], --channel-filter NAME [NAME ...]
                        plays, lists, marks, downloads only videos from channels defined in the filter
  -n, --include-watched
                        include already watched videos to filter rules
  -s YYYY-MM-DD, --since YYYY-MM-DD
                        includes only videos published after the given date
  -t YYYY-MM-DD, --to YYYY-MM-DD
                        includes only videos published before the given date
  -p PATH, --path PATH  set the download path to PATH
  -g, --no-description  do not print the video description before playing the video
  -o COL [COL ...], --columns COL [COL ...]
                        specifies which columns will be printed when listing videos. COL can be any of ['ID', 'Date', 'Channel', 'Title', 'URL', 'Downloaded']. All columns can be enabled with 'all'
  --import-from PATH    import YouTube channels from YouTube's subscription export (available at https://www.youtube.com/subscription_manager)
  --export-to PATH      export YouTube channels in opml format
  --cleanup             removes old videos from the database and shrinks the size of the database file
  -v, --version         output version information and exit
  --bug-report-info     print info to include in a bug report

# ytcm-daemon.py
Running this will continuously monitor added channels
If you do run this and want to use the GUI to add channels be sure to set standalone to True on the ytcm.conf
--This can be configured to run on a local server and be managed by the GUI from a workstation utilizing some sort of network share.
--JDownloader can be installed on your server headless and be managed through the JD API


# ytcm_start.py
Running this will automatically start the monitor option and with a split terminal/console allow you to access other features of the program without opening a second terminal window

# ytcm-gui.py
Running this will start the tkinter gui application (more features to come)