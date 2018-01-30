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

def setRATrackingRate(self,event):
    """
    Sets telescope RA tracking rate to the value specified in the RA tracking rate text box in the initialization tab.
        Args:
            event: handler to allow function to be tethered to a wx widget. Tethered to the "Set RA Tracking Rate" button in the initialization tab.
        Returns:
            None
    """
    RArate=self.init.trackingRateRAText.GetValue()

    valid_input=True

    try:
        val=float(RArate)
    except ValueError:
        valid_input=False

    if valid_input==True:
        self.control.currentRATRPos.SetLabel(RArate)
        self.control.currentRATRPos.SetForegroundColour('black')
        self.dict['RAtrackingRate'] = RArate
        #self.command_queue.put("RATR "+str(RArate))
        self.log("Right Ascension Tracking Rate set to " + RArate)
        self.log("If currently tracking, please turn tracking off and on to track at new rate.")
    else:
        dlg = wx.MessageDialog(self,
                           "Please input an integer or float number.",
                           "Error", wx.OK|wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
    return
# ----------------------------------------------------------------------------------
def resetRATrackingRate(self,event):
    """
    Sets telescope RA tracking rate to the recommended sidereal value of 15.04108
        Args:
            event: handler to allow function to be tethered to a wx widget. Tethered to the "Set RA Tracking Rate" button in the initialization tab.
        Returns:
            None
    """
    rate=15.04108
    self.control.currentRATRPos.SetLabel(str(rate))
    self.control.currentRATRPos.SetForegroundColour('black')
    self.dict['RAtrackingRate'] = rate
    #self.command_queue.put("RATR "+str(rate))
    self.log("Right Ascension Tracking Rate set to " + str(rate))
    self.log("If currently tracking, please turn tracking off and on to track at new rate.")

    return

# ----------------------------------------------------------------------------------
def setmaxdRA(self,event):
    """
    Sets the maximum RA adjustment the guider is allowed to perform.
        Args:
            event: handler to allow function to be tethered to a wx widget. Tethered to the "Set Maximum dRA" button in the initialization tab.
        Returns:
            None
            """
    dRA = self.init.maxdRAText.GetValue()

    valid_input = True

    try:
        val = float(dRA)
    except ValueError:
        valid_input = False

    if valid_input == True:
        self.dict['maxdRA'] = dRA
        self.log("Maximum Guider Right Ascension offset set to " + dRA)
    else:
        dlg = wx.MessageDialog(self,
                               "Please input an integer or float number.",
                               "Error", wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
    return

# ----------------------------------------------------------------------------------
def setmaxdDEC(self,event):
    """
    Sets the maximum DEC adjustment the guider is allowed to perform.
        Args:
            event: handler to allow function to be tethered to a wx widget. Tethered to the "Set Maximum dDEC" button in the initialization tab.
        Returns:
            None
    """
    dDEC = self.init.maxdDECText.GetValue()

    valid_input = True

    try:
        val = float(dDEC)
    except ValueError:
        valid_input = False

    if valid_input == True:
        self.dict['maxdDEC'] = dDEC
        self.log("Maximum Guider Declination offset set to " + dDEC)
    else:
        dlg = wx.MessageDialog(self,
                               "Please input an integer or float number.",
                               "Error", wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
    return

# ----------------------------------------------------------------------------------
