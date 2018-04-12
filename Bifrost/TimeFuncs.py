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

def on_Pacific(self,event):
    """
    Event handle for the pacific time zone option. Changes time to the current pacific time representation.

        Args:
            event: handler to allow function to be tethered to a wx widget.

        Returns:
            None
    """
    self.current_timezone="PST"
    self.sb.SetStatusText('Timezone: PST',4)
    return

# ----------------------------------------------------------------------------------
def on_Mountain(self,event):
    """
    Event handle for the Mountain time zone option. Changes time to the current Mountain time representation.

     Args:
        event: handler to allow function to be tethered to a wx widget.

     Returns:
        None
    """
    self.current_timezone="MST"
    self.sb.SetStatusText('Timezone: MST',4)
    return

# ----------------------------------------------------------------------------------
def timer(self):
    """
    Dynamically updates Julian Date, LST, UTC, Local Time and current Epoch in the telescope control tab.
        Args:
            None
        Returns:
            None
    """
    while True:
        t = self.timeCalc()
        wx.CallAfter(self.control.currentJDPos.SetLabel,( '%.2f' % t['mjd']))
        wx.CallAfter(self.control.currentLSTPos.SetLabel,(str(t['lst'])))
        wx.CallAfter(self.control.currentUTCPos.SetLabel,(str(t['utc'])))
        wx.CallAfter(self.control.currentLocalPos.SetLabel,(str(t['local'])))
        wx.CallAfter(self.control.currentEpochPos.SetLabel,('%.3f' % t['epoch']))
        time.sleep(1)

# ----------------------------------------------------------------------------------
def timeCalc(self):
    """
   Calculates current time values for Julian Date, Epoch, Local Time and LST.
        Args:
            None
        Returns:
            None
    """
    t = Time(Time.now())

    jdt=t.jd
    mjdt = t.mjd
    epoch = 1900.0 + ((float(jdt)-2415020.31352)/365.242198781)

    if self.current_timezone=="PST":
        local = time.strftime('%Y/%m/%d %H:%M:%S')
    if self.current_timezone=="MST":
        MST = datetime.now() + timedelta(hours=1)
        local=MST.strftime("%Y/%m/%d %H:%M:%S")
        #MST_rounded=MST.split('.')[0]
        #local=MST_rounded.replace("-","/")
    self.mro.date=dati.datetime.utcnow()
    lst = self.mro.sidereal_time()
    return {'mjd':mjdt,'utc':self.mro.date,'local':local,'epoch':epoch, 'lst':lst}
