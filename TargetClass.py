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


class Target(wx.Panel):
    """Panel for adding, plotting, tracking and selecting astronomical targets."""
    # ----------------------------------------------------------------------------------
    def __init__(self,parent, debug, night):
        """Create the Target panel"""
        wx.Panel.__init__(self,parent)
        self.parent = parent
        self.listpath='/home/mro/Desktop/targetlists/*'
        #self.listpath=('/home/doug/TCC/targetlists/*')

        self.listglob=glob.glob(self.listpath)
        self.targetlists=[]
        for list in self.listglob:
            filename=list.split("/")[-1]
            self.targetlists.append(filename)


        #############################################################

        # #Target List Retrieval
        self.fileLabel=wx.StaticText(self, size=(-1,-1))
        self.fileLabel.SetLabel('Current Target List:   ')
        self.fileText=wx.TextCtrl(self,size=(400,-1))
        #
        #self.fileText = wx.ComboBox(self, -1, size = (400,-1), style = wx.CB_DROPDOWN,
        #                                 choices = self.targetlists)

        #############################################################

        #Logbox for the Target tab, continuously updated by TCC.log()
        self.logBox = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.VSCROLL)

        #############################################################

        #Initialize Target List Table
        self.targetList=wx.ListCtrl(self,size=(525,200), style=wx.LC_REPORT | wx.VSCROLL)
        self.targetList.InsertColumn(0,'Object Name',width=125)
        self.targetList.InsertColumn(1,'RA',width=100)
        self.targetList.InsertColumn(2,'DEC',width=100)
        self.targetList.InsertColumn(3,'EPOCH',width=62.5)
        self.targetList.InsertColumn(5,'V Mag',width=62.5)
        self.targetList.InsertColumn(6,'Airmass',width=75)

        #############################################################

        #Manual Target Input

        #Target Name
        self.nameLabel=wx.StaticText(self, size=(50,-1))
        self.nameLabel.SetLabel('Name: ')
        self.nameText=wx.TextCtrl(self,size=(125,-1))

        #Target RA
        self.raLabel=wx.StaticText(self, size=(50,-1))
        self.raLabel.SetLabel('RA: ')
        self.raText=wx.TextCtrl(self,size=(125,-1))

        #Target DEC
        self.decLabel=wx.StaticText(self, size=(50,-1))
        self.decLabel.SetLabel('DEC: ')
        self.decText=wx.TextCtrl(self,size=(125,-1))

        #Target Coordinate Epoch
        self.epochLabel=wx.StaticText(self, size=(75,-1))
        self.epochLabel.SetLabel('EPOCH: ')
        self.epochText=wx.TextCtrl(self,size=(125,-1))

        #Target V Magnitude
        self.magLabel=wx.StaticText(self, size=(75,-1))
        self.magLabel.SetLabel('V Mag: ')
        self.magText=wx.TextCtrl(self,size=(125,-1))

        #############################################################

        #Buttons
        self.listButton = wx.Button(self, -1, "Retrieve List")
        self.selectButton = wx.Button(self, -1, "Select Target")
        self.enterButton = wx.Button(self, -1, "Add to List")
        self.popButton = wx.Button(self, -1, "Populate Current Info")
        self.removeButton=wx.Button(self,-1,"Remove Selected from List")
        self.exportButton=wx.Button(self,-1,"Export List")
        self.plot_button=wx.Button(self,-1,'Plot Target')
        self.plot_button.SetBackgroundColour("Lime Green")
        self.plot_button.SetForegroundColour("White")
        self.airmass_button=wx.Button(self,-1,"Airmass Curve")
        self.airmass_button.SetBackgroundColour("Lime Green")
        self.airmass_button.SetForegroundColour("White")
        self.finder_button=wx.Button(self,-1,"Load Finder Chart")
        self.finder_button.SetBackgroundColour("Lime Green")
        self.finder_button.SetForegroundColour("White")
        #self.refresh_button=wx.Button(self,-1,"Refresh Choices")

        #Turn Buttons off initially, enable on initialization
        self.listButton.Disable()
        self.selectButton.Disable()
        self.enterButton.Disable()
        self.removeButton.Disable()
        self.exportButton.Disable()
        self.plot_button.Disable()
        self.airmass_button.Disable()
        self.finder_button.Disable()

        #Sizers: Create Box Sizers
        self.vbox=wx.BoxSizer(wx.VERTICAL)
        self.hbox1=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3=wx.BoxSizer(wx.HORIZONTAL)
        self.logbox_h= wx.BoxSizer(wx.HORIZONTAL)
        self.gbox=wx.GridSizer(rows=5, cols=2, hgap=5, vgap=5)

        #Sizers: Populate Box Sizers
        self.hbox1.Add(self.fileLabel,0,wx.ALIGN_CENTER)
        self.hbox1.Add(self.fileText,0, wx.ALIGN_CENTER)
        self.hbox1.Add(self.listButton,0, wx.ALIGN_CENTER)
        self.hbox1.AddSpacer(5)

        self.hbox1.Add(self.popButton,0, wx.ALIGN_CENTER)
        self.hbox1.AddSpacer(10)
        #self.hbox1.Add(self.refresh_button,0,wx.ALIGN_CENTER)

        #Populate Manual Target Input Box
        self.gbox.Add(self.nameLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.nameText, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.raLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.raText, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.decLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.decText, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.epochLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.epochText, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.magLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.magText, 0, wx.ALIGN_RIGHT)

        self.hbox2.Add(self.targetList,0, wx.ALIGN_CENTER)
        self.hbox2.Add(self.gbox,0,wx.ALIGN_CENTER)

        self.hbox3.Add(self.selectButton,0, wx.ALIGN_CENTER)
        self.hbox3.AddSpacer(10)
        self.hbox3.Add(self.enterButton,0, wx.ALIGN_CENTER)
        self.hbox3.AddSpacer(10)
        self.hbox3.Add(self.removeButton,0, wx.ALIGN_CENTER)
        self.hbox3.AddSpacer(10)
        self.hbox3.Add(self.exportButton,0, wx.ALIGN_CENTER)
        self.hbox3.AddSpacer(10)
        self.hbox3.Add(self.plot_button,0,wx.ALIGN_CENTER)
        self.hbox3.AddSpacer(10)
        self.hbox3.Add(self.airmass_button,0,wx.ALIGN_CENTER)
        self.hbox3.AddSpacer(10)
        self.hbox3.Add(self.finder_button,0,wx.ALIGN_CENTER)

        self.logbox_h.AddSpacer(30)
        self.logbox_h.Add(self.logBox, wx.ALIGN_CENTER, wx.EXPAND)
        self.logbox_h.AddSpacer(30)

        self.vbox.Add(self.hbox1,0, wx.ALIGN_CENTER,5)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.hbox2,0, wx.ALIGN_CENTER,5)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.hbox3,0, wx.ALIGN_CENTER,5)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.logbox_h, wx.ALIGN_CENTER, wx.EXPAND)
        self.vbox.AddSpacer(15)

        self.SetSizer(self.vbox)
        self.vbox.Fit(self)

        debug==True
        self.dir=os.getcwd()
