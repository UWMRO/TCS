import time
import wx
import os
import signal
from astropy.time import Time
import thread
import threading
import ephem
import matplotlib
import datetime as dati
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.image import AxesImage
import matplotlib.image as mpimg
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
from astroplan import Observer, FixedTarget
from astroplan.plots import plot_sky,plot_airmass
import astropy.units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, FK5
from Finder_picker import plot_finder_image
from twisted.internet import wxreactor
from twisted.internet import reactor, protocol, defer
from twisted.protocols import basic
import subprocess
import Queue
from astroquery.skyview import SkyView
from astropy.wcs import WCS
import webbrowser
import glob

global pipe
pipe=None

def log(self, input):
    """
    Take input from the any system and log both on screen and to a file.
    Necessary to define command structure for easy expansion.

        Args:
            input (string): The desired message to be logged.

        Returns:
            None

    """
    today=time.strftime('%Y%m%d.log')
    current_time_log=time.strftime('%Y%m%dT%H%M%S')
    current_time=time.strftime('%Y%m%d  %H:%M:%S')
    #if self.at_MRO ==True:
    try:
        f_out=open(self.stordir+'/logs/'+today,'a')
    except IOError:
        f_out=open(self.dir+'/logs/'+today,'a')
    #else:
    #f_out=open(self.dir+'/logs/'+today,'a')
    f_out.write(current_time_log+','+str(input)+'\n')
    f_out.close()
    self.control.logBox.AppendText(str(current_time)+':  '+str(input)+'\n')
    self.target.logBox.AppendText(str(current_time) + ':  ' + str(input) + '\n')
    self.init.logBox.AppendText(str(current_time) + ':  ' + str(input) + '\n')
    return
# ----------------------------------------------------------------------------------

def getstatus(self):
    """
    Generate a log file for the current utc date. Prompt drivers for status of RA and DEC and add line to log file in form "UTC_DATE RA DEC EPOCH LST".

        Args:
            None
        Returns:
            None
    """
    time.sleep(2.0)
    while True:
        self.LST=str(self.control.currentLSTPos.GetLabel())
        self.epoch=str(self.control.currentEpochPos.GetLabel())
        self.UTC=str(self.control.currentUTCPos.GetLabel())
        self.UTC=self.UTC.split(" ")
        self.UTCdate=self.UTC[0].split("/")
        self.UTCdate=self.UTCdate[0]+self.UTCdate[1]+self.UTCdate[2]
        self.UTC=self.UTCdate+"T"+self.UTC[1]
        self.sfile=self.stordir+"/positionlogs/"+self.UTCdate+".txt"
        self.LST=self.LST.split(':')
        self.LST=float(self.LST[0])+float(self.LST[1])/60.+float(self.LST[2])/3600.
        #print "Get"
        try:
            #self.protocol.sendCommand("status "+str(self.UTC)+" "+str(self.epoch)+" "+str(self.LST)+" "+self.sfile)
            self.command_queue.put("status "+str(self.UTC)+" "+str(self.epoch)+" "+str(self.LST)+" "+self.sfile)

        except AttributeError:
            print "Not Connected to Telescope"
        time.sleep(1.0)

# ----------------------------------------------------------------------------------
def watchstatus(self):
    """
    Update TCC Status Dictionaries with information from the physical logs generated in TCC.getstatus().
        Args:
            None
        Returns:
            None
    """
    time.sleep(3.0)
    while True:
        time.sleep(1.0)
        self.UTC=str(self.control.currentUTCPos.GetLabel())
        self.UTC=self.UTC.split(" ")
        self.UTCdate=self.UTC[0].split("/")
        self.UTCdate=self.UTCdate[0]+self.UTCdate[1]+self.UTCdate[2]
        status_file = open(self.stordir+"/positionlogs/"+str(self.UTCdate)+".txt","r")

        current_pos = status_file.readlines()[-1].split()
        status_file.close()
        current_RA = current_pos[1]
        current_DEC = current_pos[2]
        current_SkyCoord = SkyCoord(ra=float(current_RA)*u.hourangle, dec=float		(current_DEC)*u.degree, frame='icrs')
        current_RADEC = current_SkyCoord.to_string('hmsdms')
        current_RA, current_DEC = current_RADEC.split(' ')
        self.telescope_status['RA']=current_RA
        self.telescope_status['Dec']=current_DEC
        #print "Watch"

# ----------------------------------------------------------------------------------

def logstatus(self):
    """
    Display parameters in telescope status dictionary to the user in each log box.
    Not sure how useful this is, every 10 minutes offers a sanity check that may be
    more useful to advanced users.
        Args:
            None
        Returns:
            None
    """
    while True:
        message=''
        for key in self.telescope_status:
            message+=key+': '+str(self.telescope_status.get(key))+' | '
        wx.CallAfter(self.log, (message))
        time.sleep(600) #Once Every 10 Minutes

# ----------------------------------------------------------------------------------
