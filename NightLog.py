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

class NightLog(wx.ScrolledWindow):
    """Night Log panel, write and save user logs for an observing night. Not currently
    displayed."""
    # ----------------------------------------------------------------------------------
    def __init__(self,parent, debug, night):
        """Create the Night Log panel"""
        self.parent = parent
        wx.ScrolledWindow.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)
        fontsz = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT).GetPixelSize()
        self.SetScrollRate(fontsz.x, fontsz.y)
        self.EnableScrolling(True,True)

        self.nltitle=wx.StaticText(self,-1, "Manastash Ridge Observatory Night Log")
        font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.nltitle.SetFont(font)
        self.labelastr=wx.StaticText(self, -1, "Astronomer(s)")
        self.labelobs=wx.StaticText(self, -1, "Observer(s)")
        self.labelinst=wx.StaticText(self, -1, "Instrument")
        self.labelstart=wx.StaticText(self, -1, "Start Time")
        self.labelend=wx.StaticText(self, -1, "End Time")
        self.usastr=wx.TextCtrl(self,size=(50,-1))
        self.usobs=wx.TextCtrl(self, size=(50,-1))
        self.usinst=wx.TextCtrl(self,size=(50,-1))
        self.usstart=wx.TextCtrl(self,size=(50,-1))
        self.usend=wx.TextCtrl(self,size=(50,-1))

        #First box components for observer and astronomer identification

        self.hbox1=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(self.labelastr,0,wx.ALIGN_RIGHT)
        self.hbox1.AddSpacer(5)
        self.hbox1.Add(self.usastr,1,wx.ALIGN_LEFT|wx.EXPAND)
        self.hbox1.AddSpacer(10)

        self.hbox2=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.labelobs,0,wx.ALIGN_RIGHT)
        self.hbox2.AddSpacer(21)
        self.hbox2.Add(self.usobs,1,wx.ALIGN_LEFT|wx.EXPAND)
        self.hbox2.AddSpacer(10)

        self.hbox3=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3.Add(self.labelinst,0,wx.ALIGN_RIGHT)
        self.hbox3.AddSpacer(23)
        self.hbox3.Add(self.usinst,1,wx.ALIGN_LEFT|wx.EXPAND)
        self.hbox3.AddSpacer(10)

        self.hbox4=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4.Add(self.labelstart,0,wx.ALIGN_RIGHT)
        self.hbox4.AddSpacer(27)
        self.hbox4.Add(self.usstart,1,wx.ALIGN_LEFT|wx.EXPAND)
        self.hbox4.AddSpacer(10)

        self.hbox5=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox5.Add(self.labelend,0,wx.ALIGN_RIGHT)
        self.hbox5.AddSpacer(31)
        self.hbox5.Add(self.usend,1,wx.ALIGN_LEFT|wx.EXPAND)
        self.hbox5.AddSpacer(10)


        #Activity Log
        self.actheader=wx.StaticText(self,label="ACTIVITY LOG")
        self.actlog=wx.TextCtrl(self, size=(600,100),style= wx.TE_MULTILINE)

        #Failure Log
        self.failheader=wx.StaticText(self,label="FAILURE LOG")
        self.faillog=wx.TextCtrl(self, size=(600,50),style= wx.TE_MULTILINE)

        #Focus Log
        self.focheader=wx.StaticText(self,label="FOCUS LOG")
        self.foclog=wx.ListCtrl(self,size=(600,100), style=wx.LC_REPORT| wx.VSCROLL | wx.LC_VRULES)
        self.foclog.InsertColumn(0,'Time',width=50)
        self.foclog.InsertColumn(1,'Instrument',width=75)
        self.foclog.InsertColumn(2,'Focus',width=75)
        self.foclog.InsertColumn(3,'Az',width=50)
        self.foclog.InsertColumn(5,'El',width=50)
        self.foclog.InsertColumn(6,'Temp',width=50)
        self.foclog.InsertColumn(7,'Strc',width=50)
        self.foclog.InsertColumn(8,'Prim',width=50)
        self.foclog.InsertColumn(9,'Sec',width=50)
        self.foclog.InsertColumn(10,'Air',width=50)
        self.foclog.InsertColumn(11,'filt',width=50)
        self.foclog.InsertColumn(12,'FWHM',width=50)

        self.focusButton=wx.Button(self,label="Number of Focus Lines")
        self.focusNum=wx.TextCtrl(self,size=(30,-1))
        self.focusNum.AppendText('1')

        self.hbox6=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox6.Add(self.focusButton,0,wx.ALIGN_CENTER)
        self.hbox6.AddSpacer(5)
        self.hbox6.Add(self.focusNum,0,wx.ALIGN_CENTER)

        #Save as and Submit buttons
        self.saveButton=wx.Button(self,label="Save As")

        self.submitButton=wx.Button(self,label="Submit")

        self.hbox7=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox7.Add(self.saveButton,0,wx.ALIGN_CENTER)
        self.hbox7.AddSpacer(25)
        self.hbox7.Add(self.submitButton,0,wx.ALIGN_CENTER)


        #Vertical box organization
        self.vbox=wx.BoxSizer(wx.VERTICAL)

        self.vbox.Add(self.nltitle, 0, wx.ALIGN_CENTER)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.hbox1,0,wx.ALIGN_LEFT|wx.EXPAND)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.hbox2,0,wx.ALIGN_LEFT|wx.EXPAND)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.hbox3,0,wx.ALIGN_LEFT|wx.EXPAND)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.hbox4,0,wx.ALIGN_LEFT|wx.EXPAND)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.hbox5,0,wx.ALIGN_LEFT|wx.EXPAND)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.actheader,0,wx.ALIGN_CENTER)
        self.vbox.Add(self.actlog,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.failheader, 0, wx.ALIGN_CENTER)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.faillog,0, wx.ALIGN_CENTER)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.focheader,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.foclog,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.hbox6,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(25)
        self.vbox.Add(self.hbox7,0,wx.ALIGN_CENTER)


        self.SetSizer(self.vbox)
        self.Show()
###########################################################################################
