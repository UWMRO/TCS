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


def readConfig(self):
    """
    Get the basic telescope information if it is available.  It would be nice if the dictionary was defined external to the program.

        Args:
            None
        Returns:
            None
    """
    self.log('==== Initializing Parameters ====')
    self.log('Reading in config file ....')
    f_in=open('tcc.conf','r')
    for line in f_in:
        l=line.split()
        self.dict[l[0]]=l[1]
    f_in.close()
    for d in self.dict:
        self.log([d,self.dict[d]])
    t = self.timeCalc()
    self.log('Configuration parameters read')
    self.sb.SetStatusText('Tracking: False',0)
    self.sb.SetStatusText('Slewing: False',1)
    self.sb.SetStatusText('Guiding: False',2)
    self.sb.SetStatusText('Init Telescope to Enable Slew / Track',3)
    self.sb.SetStatusText('Timezone: UTC',4)
    #self.init.targetDecText.SetValue(str(self.dict['lat']))
    #self.init.targetEpochText.SetValue(str( '%.3f') % t['epoch'])
    self.init.trackingRateRAText.SetValue(str(self.dict['RAtrackingRate']))
    self.init.maxdRAText.SetValue(str(self.dict['maxdRA']))
    self.init.maxdDECText.SetValue(str(self.dict['maxdDEC']))
    return

# ----------------------------------------------------------------------------------
    def displaystatus(self):
        """
        Update TCC Status grid with information from the TCC.telescope_status dictionary.
            Args:
                None

            Returns:
                None
        """
        #time.sleep(1.0)
        while True:
            time.sleep(1.0)
            wx.CallAfter(self.control.currentRaPos.SetLabel,(self.telescope_status['RA']))
            if self.telescope_status['RA']=='Unknown':
                wx.CallAfter(self.control.currentRaPos.SetForegroundColour,('Red'))
            else:
                wx.CallAfter(self.control.currentRaPos.SetForegroundColour,((0,0,0)))

            wx.CallAfter(self.control.currentDecPos.SetLabel,(self.telescope_status['Dec']))
            if self.telescope_status['Dec'] == 'Unknown':
                wx.CallAfter(self.control.currentDecPos.SetForegroundColour,('Red'))
            else:
                wx.CallAfter(self.control.currentDecPos.SetForegroundColour,((0,0,0)))

            if self.telescope_status['pointState'] == False:
                wx.CallAfter(self.control.currentNamePos.SetLabel,('Not Pointed'))
                wx.CallAfter(self.control.currentNamePos.SetForegroundColour, ('Red'))
            else:
                wx.CallAfter(self.control.currentNamePos.SetLabel,(self.target_coords['Name']))
                wx.CallAfter(self.control.currentNamePos.SetForegroundColour, ((0,0,0)))

    # ----------------------------------------------------------------------------------
def onInit(self,event):
    """
    Initialize telescope systems according to values set in the TCC config file. Enables buttons throughout the GUI that depend on initialized systems to function.

    Args:
        event: handler to allow function to be tethered to a wx widget. Tethered to the "Initialize Telescope Systems" button in the initialization tab.

    Returns:
        None
    """
    if self.telescope_status.get('initState')==False:
        self.mro.lon=self.dict['lon']
        self.mro.lat=self.dict['lat']
        self.horizonlimit=self.dict['horizonLimit']
        self.RA_trackrate=self.dict['RAtrackingRate']

        self.command_queue = Queue.Queue() #Set up the command queue which pushes commands to the server in a single thread.


        self.control.slewButton.Enable()
        self.control.trackButton.Enable()
        self.control.currentRATRPos.SetLabel(str(self.RA_trackrate))
        self.init.atZenithButton.Enable()
        self.init.syncButton.Enable()

        self.target.listButton.Enable()
        self.target.selectButton.Enable()
        self.target.enterButton.Enable()
        self.target.removeButton.Enable()
        self.target.exportButton.Enable()
        self.target.plot_button.Enable()
        self.target.airmass_button.Enable()
        self.target.finder_button.Enable()
        self.init.parkButton.Enable()
        self.init.coverposButton.Enable()

        #Watch Dog Threads
        thread.start_new_thread(self.timer,())
        thread.start_new_thread(self.checkslew,())
        thread.start_new_thread(self.getstatus,())
        thread.start_new_thread(self.watchstatus,())
        thread.start_new_thread(self.displaystatus,())
        thread.start_new_thread(self.checkhandPaddle,())
        thread.start_new_thread(self.watchcommand,())

        self.telescope_status['initState']=True
    if self.telescope_status.get('initState')==True:
        self.control.currentJDPos.SetForegroundColour('black')
        self.control.currentLSTPos.SetForegroundColour('black')
        self.control.currentUTCPos.SetForegroundColour('black')
        self.control.currentLocalPos.SetForegroundColour('black')
        self.control.currentEpochPos.SetForegroundColour('black')
        self.control.currentRATRPos.SetForegroundColour('black')
        self.control.currentFocusPos.SetLabel('0.0')
        self.control.currentFocusPos.SetForegroundColour('black')
        thread.start_new_thread(self.logstatus,())
        if self.protocol != None:
            self.telescope_status['connectState'] = True
        else:
            self.telescope_status['connectState'] = False
        """
        try:
            self.telescope_status['connectState']=self.server.connectState
        except NameError:
            self.telescope_status['connectState']= False
        """
        if self.telescope_status.get('connectState'):
            self.log("Successfully connected to the telescope.")
            self.sb.SetStatusText('Connected to Telescope', 3)
            #self.at_MRO = True #Dev Variable
        else:
            self.sb.SetStatusText('ERROR: Telescope Not Responding',3)
            self.log("Failed to connect to telescope. Restart the application.")
# ----------------------------------------------------------------------------------
