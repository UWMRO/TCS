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

def on_night(self,event):
    """
    Event handle for the night mode option in the menu. Aesthetic change to make the GUI background color redder.

        Args:
            self: points function towards WX application
            event: handler to allow function to be tethered to a wx widget
        Returns:
            None

    """
    if self.night:
        self.control.SetBackgroundColour((176,23,23))
        self.night=False
    else:
        self.night=True
        #color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BACKGROUND)
        self.control.SetBackgroundColour(self.d_color)
    return

# ----------------------------------------------------------------------------------
def pre_on(self,event):
    """
    Turns precession on for the entire GUI. Note that this is on by default when the GUI is initialized.
            Args:
                event: handler to allow function to be tethered to a wx widget.
            Returns:
                self.precession: Sets self.precession = True
    """
    self.telescope_status['precession']=True
    self.log("Precession enabled")
    return

# ----------------------------------------------------------------------------------
def pre_off(self,event):
    """
    Turns precession off for the entire GUI.
            Args:
                event: handler to allow function to be tethered to a wx widget.
            Returns:
                self.precession: Sets self.precession = True
    """
    self.telescope_status['precession']=False
    self.log("Precession disabled")
    return

# ----------------------------------------------------------------------------------
def onHelp(self, event):
    """
    Opens the TCC wiki
            Args:
                event: handler to allow function to be tethered to a wx widget.
            Returns:
                None
    """

    self.log("Opening Web Browser to load TCC wiki")
    webbrowser.open("https://github.com/UWMRO/TCC/wiki/User-Manual")
# ----------------------------------------------------------------------------------
