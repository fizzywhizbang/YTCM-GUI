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
# from tkinter import Tk, RIGHT, BOTH, RAISED, Label, LEFT
from tkinter.ttk import Frame, Button, Style, Combobox, Treeview, Progressbar, Frame, Entry

from tkinter import *
import tkinter as tk
from tkinter import messagebox
from libs.config import Config
from libs.database import Channel, Database, Video
from libs.core import YTCM
import libs.utils 
from libs.utils import *
import webbrowser
import os, datetime
from time import sleep
from threading import Thread
import threading
import subprocess
import feedparser
import time
from typing import Iterable, List, TextIO, Optional, Any, Dict, BinaryIO
from urllib.error import URLError
from urllib.parse import urlparse, urlunparse, parse_qs
from urllib.request import urlopen
from lxml import etree
from shutil import copyfile
from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import asc, desc

from helper import Commands

runscheduler=True

#defaults
config = Config()
helper = Commands()

database = Database(config.db_path)
ytcm = YTCM()
left="W"
right="E"
top="N"
bottom="S"
ttop="top"
rightclick = "<Button-" + config.mousebuttons + ">"
testURL = ""

monitor_thread = ""
logfile_name = config.serverdir + config.statuslog
t = Thread()

active_view=""

class MainWindow(tk.Frame):

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        
        
        self.utils = libs.utils

        # create all of the main containers
        self.top_frame = Frame(root, bg='#EEEEEE', height=50, pady=3)
        self.center = Frame(root, bg=config.bgcolor, width=50,
                       height=40, padx=3, pady=3)
        self.bottom_frame = Frame(root, bg='#EEEEEE', width=600, height=35, pady=3)

        # layout all of the main containers

        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)

        self.top_frame.grid(row=0, sticky="ew", columnspan=3)
        self.center.grid(row=1, sticky="nsew")
        self.bottom_frame.grid(row=2, sticky="ew")

        # create the widgets for the top frame
        self.headerimage = PhotoImage(file="images/ytimg.png")
        self.headerimage = self.headerimage.subsample(6,6)
        self.HeaderTitle = Label(self.top_frame, bg="#EEEEEE", text="YTCM GUI", image=self.headerimage, compound=LEFT , font=(
            "Arial Bold", config.fontHeader), fg="RoyalBlue")

        # layout the widgets in the top frame
        self.HeaderTitle.grid(row=0, column=0)

        #layout bottom frame menu
        self.actionlbl = Button(self.bottom_frame, text="Monitor", bg="#EEEEEE",fg="Green",command=lambda : self.menudo("home"))
        self.actionlbl.grid(column=0, row=0, padx=2, pady=3)

        self.add = Button(self.bottom_frame, text="Add",fg="Blue",bg=config.bgcolor, font=("Arial", config.fontSize), command=lambda : self.menudo("add",self.center))
        self.add.grid(column=1, row=0,pady=3)
        self.lbl1 = Label(self.bottom_frame, text="Show:",fg="Blue", font =('Arial', 12, 'bold', 'underline'))
        self.lbl1.grid(column=2, row=0, pady=3)
        self.active = Button(self.bottom_frame, text="Active",fg="Blue",bg=config.bgcolor, font=("Arial", config.fontSize), command=lambda : self.menudo("List Channels",0,0))
        self.active.grid(column=3, row=0,pady=3)
        self.arch = Button(self.bottom_frame, text="Archived",fg="Blue",bg=config.bgcolor, font=("Arial", config.fontSize), command=lambda : self.menudo("Archive Channels"))
        self.arch.grid(column=4, row=0,pady=3)
        self.arch = Button(self.bottom_frame, text="All",fg="Blue",bg=config.bgcolor, font=("Arial", config.fontSize), command=lambda : self.menudo("List All Channels",0,2))
        self.arch.grid(column=5, row=0,pady=3)
        self.backup = Button(self.bottom_frame, text="Backup db",fg="Green",bg=config.bgcolor, font=("Arial", config.fontSize), command=lambda : self.menudo("backup"))
        self.backup.grid(column=6, row=0,pady=3)

        self.quitbtn = Button(self.bottom_frame, text="Quit", fg="red", bg=config.bgcolor, font=("Arial", config.fontSize), command=lambda: exit(0))
        self.quitbtn.grid(column=8, row=0, pady=3)

        self.show_last_log()


    def clear_center(self):
        self.center = Frame(root, bg=config.bgcolor, width=50, height=40, padx=3, pady=3)
        
        # layout all of the main containers
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)  
        self.center.grid(row=1, sticky="nsew")

    def dosomething(self, combo):
        action = combo.get()
        self.HeaderTitle.configure(text="YTCM GUI (" + action +")")
        if action == "Select Action":
            #clear the center view
            self.HeaderTitle.configure(text="YTCM GUI")
            self.center.destroy()
            self.clear_center()

        if action == "test":
            self.center.destroy()
            self.testformat()

        if action == "Update Channels":
            
            self.center.destroy()
            self.update_chans()       
        
        if action == "Delete Channel":
            print("delete chan")

        if action == "List Channels":
            
            self.center.destroy()
            self.listchans()
        if action == "Add Channel":
           
            self.center.destroy()
            self.addChan()
        if action == "List Archive Channels":
           
            self.center.destroy()
            self.listchans(None, "", 1)

        if action == "List All Channels":
            self.center.destroy()
            self.listchans(None, "", 2)

        if action == "Update Archived Channels":
            
            self.center.destroy()
            self.update_chans(1)

        if action == "Edit Config":
            
            self.center.destroy()
            self.edit_config()
        
    def menudo(self, action, return_index=None,opt=None):
        active_view = ""
        self.HeaderTitle.configure(text="YTCM GUI (" + action +")")
        if action == "Delete Channel":
            self.delete_channel(return_index)
        if action == "Archive Channel":
            self.set_archive_channel(return_index,opt)
        if action == "Archive Channels":
            self.center.destroy()
            self.listchans(None, "", 1)
        if action == "List Channels":
            # print(return_index)
            
            self.center.destroy()
            self.listchans(return_index,"",opt)
        
        if action == "backup":
            ts = time.time()
            msg = Label(self.center, text="Backing up db at {}".format(ts))
            msg.grid(columnspan=3,row=0)
            self.center.destroy()
            self.backupdb()

        if action == "add":
            self.center.destroy()
            self.addChan()

        if action == "List All Channels":
            # print(return_index)
            
            self.center.destroy()
            self.listchans(return_index,"",opt)

        if action == "home":
            self.center.destroy()
            self.HeaderTitle.configure(text="YTCM GUI")
            # self.actioncombo.current(0)
            self.clear_center()
            #show last log
            self.show_last_log()

        if "List Videos" in action:
            channame = action.split("chan=")
            self.listVideos(channame[1], return_index)
        
        if "Channel Settings" in action:
            self.showChanSettings(return_index,opt)

    def show_last_log(self,update=False):

        self.active_view = "show_last_log"
        log = open(logfile_name, "r")
        
        label = Label(self.center, text="Last Scan Status", font=("Arial Bold", config.fontSize), fg="RoyalBlue", bg=config.bgcolor)
        label.grid(column=1, row=0)
        
        self.refresh = PhotoImage(file="images/arrow_refresh.png")
        refbutton = Button(self.center, text="Refresh ", image=self.refresh, compound=RIGHT, command=self.show_last_log)
        refbutton.grid(row=0,column=2, sticky="W")
        
       
        msgbox = Text(self.center, width=112, height=25,spacing1=2)
        i=0
        updatetime="0"
        msgbox.tag_configure("headfont", font=("Arial", "16","bold"), foreground="green")
        msgbox.tag_configure("headfont2", font=("Arial", "14","bold","underline"), foreground="red")
        msgbox.tag_configure("bodyfont", font=("Arial", "14","underline"),foreground="NavyBlue")
        msgbox.tag_configure("datefont", font=("Arial", "14","italic","underline"),foreground="green")
        msgbox.tag_configure("datefont2", font=("Arial", "14","italic","underline"),foreground="red")
        logfound = False
        for lines in log:
            if i == 0:
                updatetime = lines.rstrip()
                msgbox.insert(INSERT, "#############################################################\n", "headfont")
                head = "The following channels checked\n"
                head += "Your default update schedule is {} minutes\n".format(config.updatetime)
                head += "last update was at {}\n".format(updatetime)
                msgbox.insert(INSERT,head,"headfont")
                msgbox.insert(INSERT, "#############################################################\n\n","headfont")
            else:
                try:
                    logfound = True
                    #changed to comma delimited
                    arr = lines.split(",")
                    chaninfo = database.get_channel_info(arr[0], 1)
                    msgbox.insert(INSERT,"Publisher: " + chaninfo[1] + "\n", "headfont2")
                    msgbox.insert(INSERT,"added: " + arr[1] + " -- published: " + arr[2],"bodyfont")
                except:
                    print("No Log")
                    
            i=i+1 
        if logfound == False:
            msgbox.insert(INSERT,"No Log Found\nRefresh in a few seconds", "datefont2")

        
        msgbox.grid(columnspan=4, row=1)     
        log.close()

    def backupdb(self):
        self.center = Frame(root, bg=config.bgcolor, width=50, height=40, padx=3, pady=3)
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)  
        self.center.grid(row=1, sticky="nsew")

        src = config.db_path
        ts = time.time()
        msg = Label(self.center, text="Backing up db at {}".format(ts))
        msg.grid(columnspan=3,row=0)
        newext = "_backup_" + str(ts) + ".db"
        dst= config.db_path.replace(".db",newext)
        copyfile(src, dst)


    def edit_config(self):
        self.center = Frame(root, bg=config.bgcolor, width=50, height=40, padx=3, pady=3)
        
        # layout all of the main containers
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)  
        self.center.grid(row=1, sticky="nsew")
        
        dbpathLBL = Label(self.center, text="Database Path")
        dbpathLBL.grid(column=0, row=0)
        dbpath = Entry(self.center, width=config.textBoxWidthLG)
        dbpath.insert(END, config.db_path)
        dbpath.grid(column=1, row=0)

        dwnloadLBL = Label(self.center, text="Download DIR")
        dwnloadLBL.grid(column=0, row=1)
        downloaddir = Entry(self.center, width=config.textBoxWidthLG)
        downloaddir.insert(END, config.download_dir)
        downloaddir.grid(column=1, row=1)

        watcherdirLBL = Label(self.center, text="Watcher DIR")
        watcherdirLBL.grid(column=0, row=2)
        watcherdir = Entry(self.center, width=config.textBoxWidthLG)
        watcherdir.insert(END, config.watcherdir)
        watcherdir.grid(column=1, row=2)
    
    def search_chans(self,chanstr,byid=0):
        
        if byid == 0:
            try:
                channeldata = database.get_channel_info(chanstr,1)
                return channeldata[1]
            except:
                return "YTCM-Clear"
        else:
            try:
                channeldata = database.get_channel_info(chanstr,0)
                return channeldata[1]
            except:
                return "YTCM-Clear"
        
    def add_chan(self,chanstr, chaname,chadir,pgrsbar,markall,updatechan):
        chanurl = chanstr.get()
        channelFull = chanstr.get()
        channel_name = chaname.get()
        channel_dir = chadir.get()
        #set error state
        ytcm_error = True
        complete = False

        known_yt_domains = ["youtu.be", "youtube.com", "youtubeeducation.com", "youtubekids.com","youtube-nocookie.com", "yt.be", "ytimg.com"]
        #first check if this domain is valid
        url_parts = urlparse(chanurl, scheme="https")
        if not url_parts.netloc:
            url_parts = urlparse("https://" + chanurl)
        else:
            pgrsbar.step(5)
            self.center.update()

        domain = url_parts.netloc.split(":")[0]
        domain = ".".join(domain.split(".")[-2:])

        if domain not in known_yt_domains:
            messagebox.showerror(title="Entry Error",message="There is something wrong with that URL")
        else:
            chanstr.config({"background":"#b3ff99"})
            pgrsbar.step(10)
            self.center.update()


        #strip yrl from channel id
        if "http" in chanurl:
            channelarray = chanurl.split("/")
            chanurl = channelarray[4]
        
        search_result = self.search_chans(chanurl)
        if "YTCM-Clear" not in search_result:
            messagebox.showerror(title="Channel alredy in database",message="This channel is already in your database under the name of {}".format(search_result))
        else:
            
            pgrsbar.step(20)
            self.center.update()

        #validate channel name
        chan_name_validate = self.search_chans(channel_name)
        if "YTCM-Clear" not in chan_name_validate:
            messagebox.showerror(title="Channel name already exists",message="That channel name is already in the database")
        else:
            chaname.config({"background":config.good})
            pgrsbar.step(25)
            self.center.update()
    
        #verify channel inserted
        try:
            database.add_channel(Channel(displayname=channel_name,dldir=channel_dir,yt_channelid=chanurl))           
            ytcm_error = False
            self.chanid = chanurl
            complete = True
        except:
                messagebox.showerror(title="EEEEROR",message="Something failed while inserting the channel")


        if updatechan.get() == 1 or markall.get() == 1:
            helper.do_update_one(chanurl)

        if markall.get() == 1:
            helper.do_mark()
        
        if ytcm_error == False and complete == True:
            pgrsbar.step(39)
            self.menudo("Channel Settings", channel_name,1)
            sleep(1)
            self.center.update()

    def delete_channel(self,item):
        # print(item)
        chan = []
        #add channel to iterable string
        chan.append(item)
        #delete channel
        database.delete_channels(chan)
        # return to channel list
        self.menudo("List Channels")

    def set_archive_channel(self,item,opt):
        
        database.set_archive(item,opt)
        if opt == 1:
            self.menudo("List Channels")
        else:
            self.menudo("Archive Channels")


    def listchans(self,index=None,tagsearch="",archived=0,ob=Channel.displayname,so=asc):
        self.center = Frame(root, bg=config.bgcolor, width=50, height=40, padx=3, pady=3)
        
     

        # layout all of the main containers
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)  
        self.center.grid(row=1, sticky="nsew")
    
        channels = database.get_channels(archived,ob,so)   
        if so == desc:
            so = asc
        else:
            so = desc

        tree=Treeview(self.center)
        
        sstring = Entry(self.center, width=config.textBoxWidth)
        sstring.bind("<KeyRelease-Return>",lambda e : self.listchans(None,sstring.get(),archived,ob,so))
        sstring.grid(column=0,row=0)
        if len(tagsearch) >=1:
            sstring.focus()
            sstring.insert(0,tagsearch)
        searchbutton = Button(self.center, text="Search", command=lambda : self.listchans(None,sstring.get(),archived,ob,so))
        searchbutton.grid(column=1,row=0)

        clearbutton = Button(self.center,text="Clear Search")
        clearbutton.configure(command=lambda : self.listchans(archived))
        clearbutton.grid(column=3,row=0)
    

        tree["columns"]=("one","two")
        
        tree.column("#0", width=210, minwidth=10, stretch=YES)
        tree.column("one", width=350, minwidth=250, stretch=YES)
        tree.column("two",width=210,minwidth=10,stretch=YES)
        
        tree.heading("#0",text="Last Check",anchor=W, command=lambda : self.listchans(None,sstring.get(),archived,Channel.lastcheck,so))
        
        tree.heading("one", text="Channel Name",anchor=E, command=lambda : self.listchans(None,sstring.get(),archived,Channel.displayname,so))
        tree.heading("two", text="Last Published",command=lambda : self.listchans(None,sstring.get(),archived,Channel.lastpub,so))
        i = 0
        tree.tag_configure('oddrow', background='#88DD88')
        tree.tag_configure('evenrow', background='#FFFFFF')
        tree.tag_configure('archivedodd', background="#88DD88",foreground="#aaaaaa")
        tree.tag_configure('archivedeven', background='#FFFFFF',foreground="#cccccc")
     
        for item in channels:
            foldername = "folder" + str(i)
            
        
            if i % 2 == 0:
                color="evenrow"
            else:
                color="oddrow"
        
            if item.archive == True:
                if i % 2 == 0:
                    color="archivedeven"
                else:
                    color="archivedodd"
            
            if tagsearch.lower() in str(item.displayname).lower() or tagsearch.lower() in str(item.dldir).lower() or tagsearch.lower() in str(item.yt_channelid).lower():
                if item.lastpub == None:
                    lastpub = "N/A"
                else:
                    lastpub = time.ctime(item.lastpub)

                foldername = tree.insert("","end",text=time.ctime(item.lastcheck), values=(item.displayname,lastpub), tags = (color,item.displayname,item.dldir,item.yt_channelid))
                
                tree.insert(foldername,"end",text="Directory",values=(item.dldir,), tags=(color))
                
                tree.insert(foldername,"end", text="Last Published", values=(lastpub,), tags=(color))
                        
                i = i + 1

        vertscroll = Scrollbar(self.center)
        vertscroll.config(command=tree.yview)
        tree.config(yscrollcommand=vertscroll.set, height=20)
        vertscroll.grid(column=4, row=1, sticky='NSE')
        tree.bind("<Double-1>", self.item_selected)
        
        tree.grid(row=1,columnspan=4,sticky="NSEW")
        tree.focus(index)
        tree.selection_set(index)
        tree.see(index)

    def item_selected(self,event):
        item_id = event.widget.focus()
        item = event.widget.item(item_id)
        values = item['values']

        value = values[0]
        # #reset selected item
        
        self.center.destroy()
        
        self.showChanSettings(value, item_id)

    def get_feed(self,value):
        url = config.RSSPrefix + value
        feed = feedparser.parse(url)
        for entry in feed.entries:

            return [
                Video(
                    yt_videoid=str(entry.yt_videoid),
                    title=str(entry.title),
                    description=str(entry.description),
                    publisher=value,
                    publish_date=self.utils.get_unix_utc(entry.published,'ut'),
                    watched=False
                )
                for entry in feed.entries
            ]

    def show_feed(self,body, value):
        center = body
        tree=Treeview(center)
        tree["columns"]=("one","two")
        
        tree.column("#0", width=20, minwidth=10, stretch=YES)
        tree.column("one", width=390, minwidth=250, stretch=YES)
        tree.column("two", width=200, minwidth=40)
    
        tree.heading("#0",text="ID",anchor=W)
        tree.heading("one", text="Title",anchor=W)
        tree.heading("two", text="Date",anchor=W)
        i = 0
        tree.tag_configure('oddrow', background='#88DD88')
        tree.tag_configure('evenrow', background='#FFFFFF')
        vids = self.get_feed(value)
        for videodata in vids:
            foldername = "folder" + str(i)
            if i % 2 == 0:
                color="evenrow"
            else:
                color="oddrow"
            ts = int(videodata.publish_date)
            
            foldername=tree.insert("","end",text=i, values=(videodata.title, time.ctime(ts)), tags = (color))
            
            tree.insert(foldername,"end",text="desc",values=(videodata.description,""), tags=(color))
            i = i + 1

        vertscroll = Scrollbar(center)
        vertscroll.config(command=tree.yview)
        tree.config(yscrollcommand=vertscroll.set)
        tree.grid(row=5,columnspan=3,sticky="NSEW")
        
        vertscroll.grid(column=3, row=5, sticky='NSE')

    def showChanSettings(self,value, return_index):

        self.center = Frame(root, bg=config.bgcolor, width=50, height=40, padx=3, pady=3)
        
        # layout all of the main containers
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)  
        self.center.grid(row=1, sticky="nsew")
        # set header label
        self.HeaderTitle.configure(text=value + " Channel Settings")
        
        #set center frame
        channelData = database.get_channel_info(value,0)
        # feedArray = get_feed(channelData[3])

        ##########
        ## top menu

        linklabel = Label(self.center, text=value + " URL-->", fg="blue",bg=config.bgcolor, cursor="hand2", font=("Arial Bold", 12))
        linklabel.grid(column=0,row=0)
        linklabel.bind("<Button-1>", lambda e: self.callback(config.YTPrefix + channelData[3] + "/videos"))
        #get_feed(channelData[3])
        rssbtn = Button(self.center, text=value + " RSS-->",bg=config.bgcolor, fg="blue", cursor="hand2", font=("Arial Bold", 12), command=lambda : self.show_feed(self.center, channelData[3]))
        rssbtn.grid(column=1, row=0)
        
        updateChanBtn = Button(self.center, text="Update Channel",fg="green", font=("Arial Bold", 12), command=lambda : self.open_new_window(channelData[3]))
        updateChanBtn.grid(column=2,row=0, columnspan=3)

        ##########
        ## channel info
        chanlbl = Label(self.center, text="Enter Channel URL",bg=config.bgcolor, font=("Arial", config.fontSize))
        chanlbl.grid(column=0, row=1, sticky=left)

        channelString = Entry(self.center, width=config.textBoxWidth)
        channelString.insert(END, channelData[3])
        channelString.grid(column=1,columnspan=3,row=1)

        chanNameLbl = Label(self.center, text="Channel Name",bg=config.bgcolor, font=("Arial", config.fontSize))
        chanNameLbl.grid(column=0, row=2, sticky=left)
        channelName = Entry(self.center, width=config.textBoxWidth)
        channelName.insert(END, channelData[1])
        channelName.grid(column=1,columnspan=3, row=2)


        channelDirLbl = Label(self.center, text="Channel Directory",bg=config.bgcolor, font=("Arial", config.fontSize))
        channelDirLbl.grid(column=0, row=3, sticky=left)
        channelDirTxt = Entry(self.center, width=config.textBoxWidth)
        channelDirTxt.insert(END, channelData[2])
        channelDirTxt.grid(column=1,columnspan=3, row=3) 

        ct = database.get_video_count(channelData[3])
        
        ##########
        ## bottom buttons
        showVidsBtn = Button(self.center, text="Show Downloaded " + "("+ct+")",fg="Blue",bg=config.bgcolor, font=("Arial", config.fontSize), command=lambda : self.menudo("List Videos chan=" + value, self.center))
        showVidsBtn.grid(column=0, row=4,pady=3, sticky=left)
        archive = channelData[6]
        if archive == 0:
            arcbutton = Button(self.center, text="Archive Channel",fg="Blue",bg=config.bgcolor, font=("Arial", config.fontSize), command=lambda : self.menudo("Archive Channel", channelData[3],1))
            arcbutton.grid(column=1, row=4,pady=3)
        else :
            arcbutton = Button(self.center, text="UnArchive Channel",fg="Blue",bg=config.bgcolor, font=("Arial", config.fontSize), command=lambda : self.menudo("Archive Channel", channelData[3],0))
            arcbutton.grid(column=1, row=4,pady=3)

        delbutton = Button(self.center, text="Delete Channel",fg="Blue",bg=config.bgcolor, font=("Arial", config.fontSize), command=lambda : self.menudo("Delete Channel", channelData[1],channelData[6]))
        delbutton.grid(column=2, row=4,pady=3)    

        btn = Button(self.center, text="Return",fg="Blue",bg=config.bgcolor, font=("Arial", config.fontSize), command=lambda : self.menudo("List Channels", return_index,channelData[6]))
        btn.grid(column=3, row=4,pady=3)  

        savebtn = Button(self.center, text="Save", fg="Blue", bg=config.bgcolor,font=("Arial", config.fontSize), command=lambda : self.update_channel_settings(channelData[0],channelString,channelName,channelDirTxt,channelData[1]))
        savebtn.grid(column=4, row=4,pady=3)

    def update_channel_settings(self,dbid,channelString,channelName,channelDirTxt,oldname):
        name = channelName.get()
        dldir = channelDirTxt.get()
        chanurl = channelString.get()
        if name == oldname:
            #channel name is not being updated
            updatecomplete = database.update_channel_data(dbid,chanurl, name, dldir,False)
        else:
            updatecomplete = database.update_channel_data(dbid,chanurl, name, dldir,True)
        
        print(updatecomplete)
 

    def listVideos(self,chan, target):
        self.center = target
        #get chan id
        chanid = database.get_channel_id(chan)
        vids = database.get_channel_videos(chanid)
    
    
        tree=Treeview(self.center)
        tree["columns"]=("one","two")
        
        tree.column("#0", width=20, minwidth=10, stretch=YES)
        tree.column("one", width=390, minwidth=250, stretch=YES)
        tree.column("two", width=200, minwidth=40)
    
        tree.heading("#0",text="ID",anchor=W)
        tree.heading("one", text="Title",anchor=W)
        tree.heading("two", text="Date",anchor=W)
        i = 0
        tree.tag_configure('oddrow', background='#88DD88')
        tree.tag_configure('evenrow', background='#FFFFFF')

        for videodata in vids:
            foldername = "folder" + str(i)
            if i % 2 == 0:
                color="evenrow"
            else:
                color="oddrow"
            # tree.insert("", 1, "", text="Folder 1", values=("23-Jun-17 11:05","File folder",""))
            ts = int(videodata.publish_date)
            foldername=tree.insert("","end",text=videodata.yt_videoid, values=(videodata.title, time.ctime(ts)), tags = (color))
            #tree.insert(folder1, "end", "", text="photo1.png", values=("23-Jun-17 11:28","PNG file","2.6 KB"))
            tree.insert(foldername,"end",text="desc",values=(videodata.description,videodata.watched), tags=(color))
            i = i + 1
       
        vertscroll = Scrollbar(self.center)
        vertscroll.config(command=tree.yview)
        tree.config(yscrollcommand=vertscroll.set)
        tree.bind("<Button-"+config.mousebuttons+">", self.video_action_window)
        tree.grid(row=5,columnspan=3,sticky="NSEW")
        
    def callback(self,url):
        webbrowser.open_new(url)

    def update_chans(self,archive=0):
        self.center = Frame(root, bg=config.bgcolor, width=50, height=40, padx=3, pady=3)
        
        # layout all of the main containers
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)  
        self.center.grid(row=1, sticky="nsew")

        #run through channel check's
        channels = database.get_channels(archive)
        number_of_channels = len(channels) + .1
        pgbar = Progressbar(self.center, orient=HORIZONTAL,length=700, mode="determinate")
        pgbar["maximum"] = number_of_channels
        
        tbox = Text(self.center,height=25,width=100)
        tbox.grid(column=0, row=0)
        pgbar.grid(column=0,row=1)
        for item in channels:
            pgbar.step()
            tbox.insert(END, "checking " + item.displayname + "\n")
            self.center.update()
            
    def addChan(self):
        self.center = Frame(root, bg=config.bgcolor, width=50, height=40, padx=3, pady=3)
        
        # layout all of the main containers
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)  
        self.center.grid(row=1, sticky="nsew")
        #set center frame
        
        chanlbl = Label(self.center,bg=config.bgcolor, text="Enter Channel URL", font=("Arial", config.fontSize))
        chanlbl.grid(column=0, row=1, sticky=left)

        channelString = Entry(self.center, width=config.textBoxWidthLG)
        #for testing
        channelString.insert(0,testURL)
        channelString.grid(column=1,columnspan=4,row=1)

        chanNameLbl = Label(self.center,bg=config.bgcolor, text="Channel Name", font=("Arial", config.fontSize))
        chanNameLbl.grid(column=0, row=2, sticky=left)
        channelName = Entry(self.center, width=config.textBoxWidthLG)
        
        channelName.grid(column=1,columnspan=4, row=2)


        channelDirLbl = Label(self.center,bg=config.bgcolor, text="Channel Directory", font=("Arial", config.fontSize))
        channelDirLbl.grid(column=0, row=3, sticky=left)
        channelDirTxt = Entry(self.center, width=config.textBoxWidthLG)
        
        channelDirTxt.grid(column=1,columnspan=4, row=3) 

        channelName.bind("<KeyRelease>", lambda e: self.writeTo(channelName, channelDirTxt))

        pgrsbar = Progressbar(self.center,orient=HORIZONTAL,length=400,mode="determinate",takefocus=True,maximum=100)
        pgrsbar.place(anchor="e")
        checkCmd = IntVar()
        checkCmd.set(0)
        updatechan = Checkbutton(self.center, text="Download all videos", variable=checkCmd,onvalue=1, offvalue=0)
        updatechan.grid(column=1, row=4)
        markallCmd = IntVar()
        markallCmd.set(0)
        markall = Checkbutton(self.center, text="Mark all downloaded", variable=markallCmd, onvalue=1, offvalue=0)
        markall.grid(column=2, row=4)
        btnadd = Button(self.center, text="Add", font=("Arial", config.fontSize), command=lambda : self.add_chan(channelString, channelName, channelDirTxt,pgrsbar,markallCmd,checkCmd))
        btnadd.grid(column=3, row=4, sticky=right)
        btn = Button(self.center, text="Cancel", font=("Arial", config.fontSize), command=lambda : self.menudo("home"))
        btn.grid(column=4, row=4, sticky=right)
        
        
        
        pgrsbar.grid(columnspan=4,row=6)
    
    def writeTo(self,inp,out):
        out.delete(0,'end')
        out.insert(0,inp.get())

    def search(self,tree,val,channels):
        tree.selection_set(tree.tag_has(val))

    def download_video(self,video,chanid):
        folderwatch = config.watcherdir
        dldir = database.get_channel_dir(chanid) 
        ts = int(time.time())
        database.update_channel_ts(chanid, ts)    
        url = config.watchPrefix + video.yt_videoid
        
        # #write to jdownloader watcher directory
        cmd = ""
        cmd += "#download %s\n" % video.title
        cmd += "text=\"%s\"\n" % url
        #removed package name to use JDownloader preferences
        #cmd += "packageName=%s\n" % videotitle
        cmd += "enabled=true\n"
        cmd += "autoStart=TRUE\n"
        cmd += "forcedStart=Default\n"
        cmd += "autoConfirm=TRUE\n"
        cmd += "downloadFolder=%s/<jd:packagename>\n" % dldir
        cmd += "priority=DEFAULT\n"
        cmd += "downloadPassword=null\n"
        filename = folderwatch + video.yt_videoid + ".crawljob"
        f = open(filename, "w+")
        f.write(cmd)
        f.close()
        #mark video watched/downloaded
        video.watched = True

        return True

    def open_new_window(self,chanid):
        newWindow = Tk()
        newWindow.title('Channel Update')
        newWindow.geometry('{}x{}'.format(800, 500))
        vids = self.get_feed(chanid)
        '''
                    yt_videoid=str(entry.yt_videoid),
                    title=str(entry.title),
                    description=str(entry.description),
                    publisher=value,
                    publish_date=get_unix_utc(entry.published,'ut'),
                    watched=False
        '''
        tbox = Text(newWindow,height=25,width=100)
        tbox.grid(column=0, row=0)
        pgbar = Progressbar(newWindow, orient=HORIZONTAL,length=500, mode="determinate")
        pgbar["maximum"] = len(vids) + .1
        pgbar.grid(column=0,row=1)
        for videodata in vids:
            pgbar.step()
            newWindow.update()
            
            #if video not downloaded inititate download
            result = database.add_video(videodata.yt_videoid,videodata)
            if result == 1:
                if self.download_video(videodata,chanid) == True:
                    tbox.insert(END,"Downloading " + videodata.title + " \n")
            else:
                tbox.insert(END,videodata.title + " already downloaded \n")
        database.close()
        tbox.insert(END, "Operation complete")
        sleep(2)
        newWindow.destroy()
        # newWindow.mainloop()

    
    def video_action_window(self,event):
        item_id = event.widget.focus()
        item = event.widget.item(item_id)
        values = item['text']
        
        # popupmenu.place(x=cursorx, y=cursory)
        print(values)
        # Popup.text_popup(self, values)

        newWindow = Tk()
        newWindow.title('Video Opts')
        
        newWindow.geometry('{}x{}'.format(200, 200))
        lbl = Label(newWindow, text="Actions", pady=10)
        lbl.pack()
        btn = Button(newWindow, text="Re-Download", font=("Arial", 12), command=lambda : self.reset_video(values, newWindow))
        btn.pack()
        newWindow.mainloop()

    def reset_video(self,vidid,newWindow):
        database.reset_video_watched_flag(vidid)
        helper.do_download()
        messagebox.showinfo(title="Download Status", message="Video {} added to download queue".format(vidid))
        newWindow.destroy()


def read_runpid() -> int:
    ts = str(time.time())
    runpidfile = "logs/run.pid"
    try:
        runpid = open(runpidfile, "r")
        lastcheck = runpid.read()
        diff = time_diff(float(lastcheck), float(ts))
        print("{} minutes since last check".format(diff))
        nextcheck = int(config.updatetime) - diff
        print("{} minutes until next check".format(nextcheck))
        runpid.close()
    except:
        print("no last run time")
        nextcheck = 0
    
    return int(nextcheck)

def monitor():
    prettytime=datetime.datetime.now()
    opts = ["./ytcm.py", "-u", "-d"]
    #check for running pid and read time
    #if time < config.update time else delete pid due to orphan and run update
    ts = str(time.time())
    runpidfile = config.serverdir + "logs/run.pid"
    nextcheck = read_runpid()

    print(nextcheck)
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
        monitor() #start the monitor routine
        scheduler = BlockingScheduler()
        
        scheduler.add_job(monitor, 'interval', minutes=int(config.updatetime)) #add monitor to blocking scheduler
        
        scheduler.start()



if __name__ == "__main__":
    root = tk.Tk()
    root.title('YTCM GUI')
    root.geometry('{}x{}'.format(800, 500))
    root.configure(bg=config.bgcolor)
    
    main = MainWindow(root)
    fname = config.serverdir + config.statuslog
 
    if config.standalone == True:
        t._target = run
        t.daemon=True
        t.start()

    root.mainloop()
