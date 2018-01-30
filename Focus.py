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

def focusIncPlus(self,event):
    """
    Focus Increment; apply a positive focus increment of 1500 to the move relative box.

        Args:
            event: handler to allow function to be tethered to a wx widget.Tethered to the "Increment Positive" button in the telescope control tab.

        Returns:
            None
    """
    val=self.control.focusAbsText.GetValue()
    val=float(val)+1500.0
    val=int(val)
    self.control.focusAbsText.SetValue(str(val))
    return

# ----------------------------------------------------------------------------------
def focusIncNeg(self,event):
    """
    Focus Increment; apply a negative focus increment of 1500 to the move relative box.

        Args:
            event: handler to allow function to be tethered to a wx widget. Tethered to the "Increment Negative" button in the telescope control tab.

        Returns:
            None
    """
    val=self.control.focusAbsText.GetValue()
    val=float(val)-1500.0
    val=int(val)
    self.control.focusAbsText.SetValue(str(val))
    return

# ----------------------------------------------------------------------------------
def setfocus(self,event):
    """
    Focus Command; set current TCC focus to the value entered in the WX textctrl box.
    Overwrites current TCC focus value and sends value to drivers.

        Args:
            event: handler to allow function to be tethered to a wx widget. Tethered to the "Move Absolute" button in the telescope control tab.

        Returns:
            None
    """
    inc=self.control.focusAbsText.GetValue()
    curFocus=self.control.currentFocusPos.GetLabel()
    if curFocus=='Unknown':
        curFocus=0.0
    newfocus=float(curFocus)+float(inc)
    self.control.currentFocusPos.SetLabel(str(newfocus))
    self.control.currentFocusPos.SetForegroundColour('black')
    #self.protocol.sendCommand(str("focus")+' '+str(inc))
    self.command_queue.put(str("focus")+' '+str(inc))
    return

# ----------------------------------------------------------------------------------
def getFocus(self,event):
    """
    In Development.
        Args:
            event: handler to allow function to be tethered to a wx widget.
        Returns:
            None
    """
    num=self.focusNum.GetValue()
    files=os.popen('tail -%s /Users/%s/nfocus.txt' % (num, os.getenv('USER')), 'r')
    for l in files:
        self.focusLog.AppendText(l)
