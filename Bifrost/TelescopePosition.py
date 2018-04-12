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

def setTelescopeZenith(self, event):
    """
    This is the basic pointing protocol for the telescope.  A bubble level is used to set the telescope to a known position. When the telescope is at Zenith the RA is the current LST, the
    DEC is the Latitude of the telescope, and the Epoch is the current date transformed to the current epoch. setTelescopeZenith() produces these parameters and writes them to the
    initialization text boxes. Pushing these to the telescope is then accomplished by Set Telescope Position.

        Args:
            event: handler to allow function to be tethered to a wx widget. Tethered to the "Load Zenith Coordinates" button in the initialization tab.

        Returns:
            None
    """
    name='Zenith'
    #ra=self.control.currentLSTPos.GetLabel() #set to current LST
    ra = "LST"
    dec='+46:57:10.08' #set to LAT
    epoch=self.control.currentEpochPos.GetLabel()#define as current epoch

    self.init.targetNameText.SetValue(name)
    self.init.targetRaText.SetValue(ra)
    self.init.targetDecText.SetValue(dec)
    self.init.targetEpochText.SetValue(epoch)

    return

# ----------------------------------------------------------------------------------
def setTelescopePosition(self,event):
    """
    Sends contents of the name, RA, DEC and EPOCH text boxes in the initialization tab to the control tab. Overwrites current control tab values in the status column with the sent values.
    Used to sync TCC values with physical position of telescope.

        Args:
            event: handler to allow function to be tethered to a wx widget. Tethered to the "Set Telescope Position" button in the initialization tab.

        Returns:
            None
    """
    target_name=self.init.targetNameText.GetValue()
    target_ra=self.init.targetRaText.GetValue()
    target_dec=self.init.targetDecText.GetValue()
    target_epoch=self.init.targetEpochText.GetValue()
    if target_ra == "LST":
        target_ra = self.control.currentLSTPos.GetLabel()

    self.log('Syncing TCC position to'+' '+str(target_ra)+' '+str(target_dec))
    if target_name=="Zenith":
        try:
            #self.protocol.sendCommand("zenith")
            self.command_queue.put("zenith")
        except AttributeError:
            print "Not Connected to Telescope"
    else:
        self.targetRA = str(target_ra)
        self.targetRA = self.targetRA.split(':')
        self.targetRA = float(self.targetRA[0]) + float(self.targetRA[1]) / 60. + float(self.targetRA[2]) / 3600.
        self.targetRA = self.targetRA * 15.0  # Degrees
        self.targetDEC = str(target_dec)
        self.targetDEC = self.targetDEC.split(':')
        self.targetDEC = float(self.targetDEC[0]) + float(self.targetDEC[1]) / 60. + float(self.targetDEC[2]) / 3600.
        self.LST = str(self.control.currentLSTPos.GetLabel())
        self.LST = self.LST.split(':')
        self.LST = float(self.LST[0]) + float(self.LST[1]) / 60. + float(self.LST[2]) / 3600.
        try:
            #self.protocol.sendCommand("point " + str(self.targetRA) + " " + str(self.targetDEC) + " " + str(self.LST))
            self.command_queue.put("point " + str(self.targetRA) + " " + str(self.targetDEC) + " " + str(self.LST))
        except AttributeError:
            print "Not Connected to Telescope"
    return
# ----------------------------------------------------------------------------------
def parkscope(self,event):
    """
    Send Command to the telescope to park (move to zenith).

        Args:
            event: handler to allow function to be tethered to a wx widget. Tethered to the "Park Telescope" button in the initialization tab.

        Returns:
            None
    """
    if self.telescope_status.get('slewing')==False:
        try:
            #self.protocol.sendCommand("park")
            self.command_queue.put("park")
            if self.telescope_status.get('pointState')==True:
                self.target_coords['Name'] = "Zenith"
            if self.telescope_status.get('tracking')==True:
                self.telescope_status['tracking']=False
                self.control.trackButton.SetLabel('Start Tracking')
                self.control.trackButton.SetBackgroundColour('Light Slate Blue')
                self.log("Tracking was on, turned off to Park Telescope")

        except AttributeError:
            print "Not Connected to Telescope"
# ----------------------------------------------------------------------------------
def coverpos(self,event):
    """
    Send Command to the telescope to Cover Position.

        Args:
            event: handler to allow function to be tethered to a wx widget. Tethered to the "Slew to Cover Position" button in the initialization tab.

        Returns:
            None
    """
    if self.telescope_status.get('slewing')==False:
        try:
            #self.protocol.sendCommand("coverpos")
            self.command_queue.put("coverpos")
            if self.telescope_status.get('pointState')==True:
                self.target_coords['Name'] = "Cover Position"
            if self.telescope_status.get('tracking')==True:
                self.telescope_status['tracking']=False
                self.control.trackButton.SetLabel('Start Tracking')
                self.control.trackButton.SetBackgroundColour('Light Slate Blue')
                self.log("Tracking was on, turned off for slew to Cover Position")

        except AttributeError:
            print "Not Connected to Telescope"

# ----------------------------------------------------------------------------------
def pointing(self,event):
    """
    Pointing aligns the telescopes position coordinates with a target has been slewed to. Pointing is called
    when the observer jogs the target directly into the center of the frame after a slew. This alignment corrects
    future inaccuracies in slewing and should be executed as an initialization task.

        Args:
            event: handler allows function to be tethered to a WX widget. Tethered to the On Target button
        Returns:
            None
    """
    self.targetRA=str(self.target_coords.get('RA'))
    #self.targetRA_h, self.targetRA=self.targetRA.split('h')
    #self.targetRA_m, self.targetRA=self.targetRA.split('m')
    #self.targetRA_s = self.targetRA[:-1]
    #self.targetRA=float(self.targetRA_h)+float(self.targetRA_m)/60.+float(self.targetRA_s)/3600.
    #self.targetRA=self.targetRA*15.0 #Degrees
    self.targetDEC=str(self.target_coords.get('DEC'))
    #self.targetDEC_d, self.targetDEC=self.targetDEC.split('d')
    #self.targetDEC_m, self.targetDEC=self.targetDEC.split('m')
    #self.targetDEC_s = self.targetDEC[:-1]
    #self.targetDEC=float(self.targetDEC_d)+float(self.targetDEC_m)/60.+float(self.targetDEC_s)/3600.

    self.LST=str(self.control.currentLSTPos.GetLabel())
    self.LST=self.LST.split(':')
    self.LST=float(self.LST[0])+float(self.LST[1])/60.+float(self.LST[2])/3600.
    print "point "+str(self.targetRA)+ " "+str(self.targetDEC)+" "+str(self.LST)

    try:
        #self.protocol.sendCommand("point "+str(self.targetRA)+ " "+str(self.targetDEC)+" "+str(self.LST))
        self.command_queue.put("point "+str(self.targetRA)+ " "+str(self.targetDEC)+" "+str(self.LST))
        self.log("Pointing Successful: Telescope coordinates updated to coordinates of " +self.target_coords.get('Name'))
        self.log("Updated RA: "+str(self.targetRA))
        self.log("Updated DEC: "+str(self.targetDEC))
    except AttributeError:
        print "Not Connected to Telescope"
    self.telescope_status['pointState']=True
    if self.telescope_status.get("tracking") == True:
        self.command_queue.put('track on '+str(self.dict.get('RAtrackingRate')))


# ----------------------------------------------------------------------------------
