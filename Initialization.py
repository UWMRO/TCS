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

class Initialization(wx.Panel):
    """Initialization tab; initialize telescope, set coordinates and set neccesary parameters"""
    # ----------------------------------------------------------------------------------
    def __init__(self,parent, debug, night):
        """Create the Initialization panel"""
        wx.Panel.__init__(self,parent)

        #############################################################

        # Logbox for the Initialization tab, continuously updated by TCC.log()
        self.logBox = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.VSCROLL)

        #############################################################

        #Telescope Coordinates

        #Name of object at desired coordinates; if "Zenith" , Set Telescope Position uses Zenith command
        self.targetNameLabel=wx.StaticText(self, -1)
        self.targetNameLabel.SetLabel('Name: ')
        self.targetNameText=wx.TextCtrl(self,size=(100,-1))
        #Right Ascension Coordinate
        self.targetRaLabel=wx.StaticText(self, -1)
        self.targetRaLabel.SetLabel('RA: ')
        self.targetRaText=wx.TextCtrl(self,size=(100,-1))
        #Declination Coordinate
        self.targetDecLabel=wx.StaticText(self, -1)
        self.targetDecLabel.SetLabel('DEC: ')
        self.targetDecText=wx.TextCtrl(self,size=(100,-1))
        #Current Epoch; generated from init task
        self.targetEpochLabel=wx.StaticText(self, -1)
        self.targetEpochLabel.SetLabel('EPOCH: ')
        self.targetEpochText=wx.TextCtrl(self,size=(100,-1))
        self.targetEpochText.SetLabel('2000')
        #Buttons; At Zenith & Set Telescope Position
        self.atZenithButton = wx.Button(self, -1, "Load Zenith Coordinates") #Not a slew to Zenith
        self.syncButton = wx.Button(self, -1, "Update Telescope Coordinates") #Tell the telescope it is at a certain location
        #self.onTargetButton = wx.Button(self, -1, "On Target")

        #############################################################

        #Tracking Initialization

        #NOTE: RA and DEC tracking currently not working simultaneously, DEC tracking is needed much less than
        #RA tracking however, so for now only RA tracking works.

        # this should autofill from tcc.conf

        #Right Ascension Tracking Rate; Suggested value of 15.04108 deg/hr
        self.trackingRateRALabel=wx.StaticText(self)
        self.trackingRateRALabel.SetLabel('RA Tracking Rate: ')
        self.trackingRateRAText=wx.TextCtrl(self,size=(100,-1))
        self.rateRAButton = wx.Button(self, -1, "Set RA Tracking Rate")
        self.resetTRButton = wx.Button(self,-1,"  Reset Right Ascension Tracking Rate  ")

        #############################################################

        #Guiding Initialization

        #allows for change in maximum guider offsets, should be set by tcc.conf as an initial value

        #Maximum delta Right Ascension; Guider cannot issue a correction greater than this value
        self.maxdRALabel=wx.StaticText(self, size=(75,-1))
        self.maxdRALabel.SetLabel('Max dRA: ')
        self.maxdRAText=wx.TextCtrl(self,size=(100,-1))
        self.dRAButton = wx.Button(self, -1, "Set Maximum dRA")
        #Maximum delta Declination; Guider cannot issue a correction greater than this value
        self.maxdDECLabel=wx.StaticText(self, size=(75,-1))
        self.maxdDECLabel.SetLabel('Max dDEC: ')
        self.maxdDECText=wx.TextCtrl(self,size=(100,-1))
        self.dDECButton = wx.Button(self, -1, "Set Maximum dDEC")

        #############################################################

        #Telescope Slewing

        #Buttons
        self.initButton = wx.Button(self, -1, "Initialize Telescope Systems") #Initialization; Begin threads
        self.parkButton= wx.Button(self, -1, "Park Telescope") #Park Telescope, send telescope to park position
        self.parkButton.SetBackgroundColour('Light Slate Blue')
        self.parkButton.SetForegroundColour('White')
        self.coverposButton=wx.Button(self,-1,"Slew to Cover Position") # Slew to Cover Position
        self.coverposButton.SetBackgroundColour('Light Slate Blue')
        self.coverposButton.SetForegroundColour('White')

        #############################################################

        #Disable Buttons not usable before Initialization

        self.atZenithButton.Disable()
        self.syncButton.Disable()
        self.parkButton.Disable()
        self.coverposButton.Disable()
        #self.onTargetButton.Disable()

        #############################################################

        #Sizers: Create Box Sizers
        self.main_v=wx.BoxSizer(wx.VERTICAL)
        self.main_h=wx.BoxSizer(wx.HORIZONTAL)
        self.leftbox_v=wx.BoxSizer(wx.VERTICAL)

        self.tslabel = wx.StaticBox(self, label="Telescope Slewing")
        self.tsbox_v = wx.StaticBoxSizer(self.tslabel, wx.VERTICAL)

        self.tclabel = wx.StaticBox(self, label="Telescope Coordinates")
        self.tcbox_v = wx.StaticBoxSizer(self.tclabel, wx.VERTICAL)

        self.tlabel = wx.StaticBox(self, label="Tracking")
        self.tbox_v = wx.StaticBoxSizer(self.tlabel, wx.VERTICAL)

        self.glabel = wx.StaticBox(self, label="Guiding")
        self.gbox_v = wx.StaticBoxSizer(self.glabel, wx.VERTICAL)

        self.coordbox_g = wx.GridSizer(rows=4, cols=2, hgap=5, vgap=5)
        self.slewbox_h = wx.BoxSizer(wx.HORIZONTAL)
        self.trackbox1_h = wx.BoxSizer(wx.HORIZONTAL)
        self.trackbox2_h = wx.BoxSizer(wx.HORIZONTAL)
        self.guidebox1_h = wx.BoxSizer(wx.HORIZONTAL)
        self.guidebox2_h = wx.BoxSizer(wx.HORIZONTAL)
        self.logbox_h = wx.BoxSizer(wx.HORIZONTAL)

        #Sizers: Populate Box Sizers
        #self.coordbox_g.Add(self.atZenithButton,0,wx.ALIGN_CENTER)
        #self.coordbox_g.Add(self.syncButton,0, wx.ALIGN_CENTER)
        self.coordbox_g.Add(self.targetNameLabel, 0, wx.ALIGN_CENTER)
        self.coordbox_g.Add(self.targetNameText, 0, wx.ALIGN_CENTER)
        self.coordbox_g.Add(self.targetRaLabel, 0, wx.ALIGN_CENTER)
        self.coordbox_g.Add(self.targetRaText, 0, wx.ALIGN_CENTER)
        self.coordbox_g.Add(self.targetDecLabel, 0, wx.ALIGN_CENTER)
        self.coordbox_g.Add(self.targetDecText, 0, wx.ALIGN_CENTER)
        self.coordbox_g.Add(self.targetEpochLabel, 0, wx.ALIGN_CENTER)
        self.coordbox_g.Add(self.targetEpochText, 0, wx.ALIGN_CENTER)

        self.tcbox_v.Add(self.atZenithButton,0,wx.ALIGN_CENTER)
        self.tcbox_v.AddSpacer(5)
        self.tcbox_v.Add(self.coordbox_g, 0 ,wx.ALIGN_CENTER)
        self.tcbox_v.AddSpacer(5)
        self.tcbox_v.Add(self.syncButton,0,wx.ALIGN_CENTER)

        self.slewbox_h.Add(self.initButton,0,wx.ALIGN_LEFT)
        self.slewbox_h.AddSpacer(10)
        self.slewbox_h.Add(self.parkButton, 0, wx.ALIGN_LEFT)
        self.slewbox_h.AddSpacer(10)
        self.slewbox_h.Add(self.coverposButton, 0, wx.ALIGN_LEFT)


        self.tsbox_v.Add(self.slewbox_h,0,wx.ALIGN_LEFT)

        self.trackbox1_h.Add(self.trackingRateRALabel,0,wx.ALIGN_RIGHT)
        self.trackbox1_h.AddSpacer(5)
        self.trackbox1_h.Add(self.trackingRateRAText,0,wx.ALIGN_RIGHT)
        self.trackbox1_h.AddSpacer(5)
        self.trackbox1_h.Add(self.rateRAButton,0,wx.ALIGN_RIGHT)

        self.tbox_v.Add(self.trackbox1_h,0,wx.ALIGN_CENTER)
        self.tbox_v.AddSpacer(5)
        self.tbox_v.Add(self.resetTRButton,0,wx.ALIGN_CENTER)

        self.guidebox1_h.Add(self.maxdRALabel, 0, wx.ALIGN_RIGHT)
        self.guidebox1_h.AddSpacer(5)
        self.guidebox1_h.Add(self.maxdRAText,0, wx.ALIGN_RIGHT)
        self.guidebox1_h.AddSpacer(5)
        self.guidebox1_h.Add(self.dRAButton, 0, wx.ALIGN_RIGHT)

        self.guidebox2_h.Add(self.maxdDECLabel, 0, wx.ALIGN_RIGHT)
        self.guidebox2_h.AddSpacer(5)
        self.guidebox2_h.Add(self.maxdDECText, 0, wx.ALIGN_RIGHT)
        self.guidebox2_h.AddSpacer(5)
        self.guidebox2_h.Add(self.dDECButton, 0, wx.ALIGN_RIGHT)

        self.gbox_v.Add(self.guidebox1_h, 0, wx.ALIGN_CENTER)
        self.gbox_v.AddSpacer(5)
        self.gbox_v.Add(self.guidebox2_h, 0, wx.ALIGN_CENTER)


        self.leftbox_v.Add(self.tsbox_v,0,wx.ALIGN_LEFT)
        self.leftbox_v.AddSpacer(5)
        self.leftbox_v.Add(self.tbox_v,0,wx.ALIGN_LEFT)
        self.leftbox_v.AddSpacer(5)
        self.leftbox_v.Add(self.gbox_v, 0, wx.ALIGN_LEFT)


        self.main_h.AddSpacer(10)
        self.main_h.Add(self.leftbox_v, wx.ALIGN_LEFT)
        self.main_h.AddSpacer(100)
        self.main_h.Add(self.tcbox_v, wx.ALIGN_LEFT)

        self.logbox_h.AddSpacer(30)
        self.logbox_h.Add(self.logBox,wx.ALIGN_CENTER, wx.EXPAND)
        self.logbox_h.AddSpacer(30)

        self.main_v.Add(self.main_h,wx.ALIGN_CENTER)
        self.main_v.Add(self.logbox_h, wx.ALIGN_CENTER, wx.EXPAND)
        self.main_v.AddSpacer(15)

        self.SetSizer(self.main_v)
