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

# ytcm-daemon.py
Running this will continuously monitor added channels
If you do run this and want to use the GUI to add channels be sure to set standalone to True on the ytcm.conf
--This can be configured to run on a local server and be managed by the GUI from a workstation utilizing some sort of network share.
--JDownloader can be installed on your server headless and be managed through the JD API


# ytcm_start.py
Running this will automatically start the monitor option and with a split terminal/console allow you to access other features of the program without opening a second terminal window

# ytcm-gui.py
Running this will start the tkinter gui application (more features to come)