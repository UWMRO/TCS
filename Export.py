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

class TargetExportWindow(wx.Frame):
    """Window brought up to export current Target List"""
    # ----------------------------------------------------------------------------------
    def __init__(self,parent):
        """Create the Target Export Window"""
        wx.Frame.__init__(self, parent, -1, "Export to Target List File", size=(300,200))

        self.parent=parent
        self.defaultdirectory='/home/mro/Desktop/targetlists'

        self.panel=Export(self)

        self.panel.pathText.SetValue(self.defaultdirectory)

        self.Bind(wx.EVT_BUTTON, self.onExport, self.panel.ExButton)
        self.Bind(wx.EVT_BUTTON, self.onCancel, self.panel.CancelButton)

    # ----------------------------------------------------------------------------------
    def onExport(self,event):
        """
        Export the current Target List.
            Args:
                event: handler to tether function to wx.Button
            Returns:
                None
        """
        f = open(str(self.panel.pathText.GetValue()+'/'+self.panel.filenameText.GetValue()), 'w')
        for item in self.list:
            f.write(str(item)+'\n')
        f.close()
        self.Close()
    # ----------------------------------------------------------------------------------
    def onCancel(self, event):
        self.Close()

###########################################################################################
class Export(wx.Panel):
    """Window brought up to export current Target List"""
    # ----------------------------------------------------------------------------------
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)

        self.parent=parent

        self.pathLabel = wx.StaticText(self, size=(75,-1))
        self.pathLabel.SetLabel('Output Path: ')
        self.pathText = wx.TextCtrl(self,size=(-1,-1))

        self.filenameLabel = wx.StaticText(self, size=(75,-1))
        self.filenameLabel.SetLabel('File Name: ')
        self.filenameText = wx.TextCtrl(self,size=(-1,-1))

        self.ExButton=wx.Button(self,-1,"Export")
        self.CancelButton=wx.Button(self,-1,"Cancel")

        self.vbox=wx.BoxSizer(wx.VERTICAL)
        self.hbox1=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3=wx.BoxSizer(wx.HORIZONTAL)

        self.hbox1.AddSpacer(15)
        self.hbox1.Add(self.pathLabel,0,wx.ALIGN_LEFT)
        self.hbox1.Add(self.pathText,1,wx.ALIGN_LEFT)
        self.hbox1.AddSpacer(15)

        self.hbox2.AddSpacer(15)
        self.hbox2.Add(self.filenameLabel,0,wx.ALIGN_LEFT)
        self.hbox2.Add(self.filenameText,1,wx.ALIGN_LEFT)
        self.hbox2.AddSpacer(15)

        self.hbox3.Add(self.CancelButton,0,wx.ALIGN_CENTER)
        self.hbox3.AddSpacer(20)
        self.hbox3.Add(self.ExButton,1,wx.ALIGN_CENTER)

        self.vbox.AddSpacer(15)
        self.vbox.Add(self.hbox1,0,wx.ALIGN_LEFT|wx.EXPAND)
        self.vbox.AddSpacer(15)
        self.vbox.Add(self.hbox2,0,wx.ALIGN_LEFT|wx.EXPAND)
        self.vbox.AddSpacer(15)
        self.vbox.Add(self.hbox3,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(15)

        self.SetSizer(self.vbox)
