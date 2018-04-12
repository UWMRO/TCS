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

def on_exit(self, event):
    """
    Exit in a graceful way so that the telescope information can be saved and used at a later time.

        Args:
            event: handler to allow function to be tethered to a wx widget
        Returns:
            None
    """
    dlg = wx.MessageDialog(self,
                           "Exit the TCC?",
                           "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
    result = dlg.ShowModal()
    dlg.Destroy()
    if result == wx.ID_OK:
        if(self.protocol is not None):
            try:
                #d= self.protocol.sendCommand("shutdown")
                self.command_queue.put("shutdown")
                #d.addCallback(self.quit)
            except AttributeError:
                print "Not Connected to Telescope"
            self.quit()
        else:
            self.quit()

# ----------------------------------------------------------------------------------
def quit(self):
    """
    Exit the GUI and shut down the reactor.

        Args:
            None
        Returns:
            None
    """

    self.Destroy()
    os.killpg(os.getpgid(pipe.pid),signal.SIGTERM)
    reactor.callFromThread(reactor.stop)
        #add save coordinates
        #self.Destroy()
