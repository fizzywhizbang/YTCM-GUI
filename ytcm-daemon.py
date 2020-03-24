#!/usr/bin/env python3
# YTCM - Youtube Channel Monitor
# Copyright (C) 2019  Marc Levine
#
# This file is part of YTCM.
#
# YTCM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# YTCM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with YTCM.  If not, see <http://www.gnu.org/licenses/>.
from threading import Thread
import threading
import subprocess
import os
import time
from time import sleep
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from libs.config import Config
from libs.utils import time_diff
config = Config()
debug = False
logfile_name = config.statuslog


def get_chan_list() -> str:
    proc = subprocess.Popen(["./ytcm.py", "-c"], stdout=subprocess.PIPE)
    out = proc.stdout.read()
    return out
    # os.system('./ytcm.py -c')

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def read_runpid() -> int:
    ts = str(time.time())
    runpidfile = "logs/run.pid"

    try:
        runpid = open(runpidfile, "r")
        lastcheck = runpid.read()
        print(float(lastcheck))
        diff = time_diff(float(lastcheck), float(ts))
        print("{} minutes since last check".format(diff))
        nextcheck = int(config.updatetime) - diff
        print("{} minutes until next check".format(nextcheck))
        runpid.close()
        
    except:
        print("no last run time")
        nextcheck = 0
    
    return int(nextcheck)

def channels_update():
    prettytime=datetime.datetime.now()
    opts = ["./ytcm.py", "-u", "-d"]
    #check for running pid and read time
    #if time < config.update time else delete pid due to orphan and run update
    ts = str(time.time())
    runpidfile = "logs/run.pid"
    #check last run time to keep from getting banned when restarting the program
    nextcheck = read_runpid()
    if nextcheck <= 1:
        #rewrite pid
        runpid = open(runpidfile, "w")
        runpid.write(ts)
        runpid.close()
        print("running {}".format(ts))
        proc = subprocess.Popen(opts, stdout=subprocess.PIPE)

        #write to log file
        logfile = open(logfile_name, 'w')
        logfile.write("{}\n".format(prettytime))
        logfile.close()

        while True:
            nextline = proc.stdout.readline()
            if len(nextline) >=1:
                try:
                    print(nextline)
                except:
                    print(nextline)
            else:
                break
                

def run():
    channels_update() #start initial scan
    scheduler = BlockingScheduler()
    #schedule scan to run at x minutes defined in the config
    scheduler.add_job(channels_update, 'interval', minutes=int(config.updatetime)) #add monitor to blocking scheduler
    scheduler.start()
   

if __name__=='__main__':
    run()
    