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

def startSlew(self,event):
    '''
    Slew Command from coordinates in control tab, also acts as a toggle. If telescope is slewing, this will stop current slewing. Stop slewing command acts as the ideal
    method for stopping the telescope. Halt Motion is the alternative intended for emergencies only. Before sending a slew command, startslew() checks the altitude of the
    target. If the altitude is below the altitude set in the configuration file, it will only return an error.

        Args:
            event: handler to allow function to be tethered to a wx widget. Tethered to the "Slew to Target" button in the telescope control tab.

        Returns:
            None

    '''
    name=self.control.targetNameText.GetValue()
    input_ra=self.control.targetRaText.GetValue()
    input_dec=self.control.targetDecText.GetValue()
    input_epoch=self.control.targetEpochText.GetValue()
    current_epoch=self.control.currentEpochPos.GetLabel()

    self.input_frame = SkyCoord(input_ra,input_dec,frame='icrs')

    if self.telescope_status.get('slewing')==False:

        self.MRO_loc=EarthLocation(lat=46.9528*u.deg, lon=-120.7278*u.deg, height=1198*u.m)
        self.inputcoordSorter(input_ra,input_dec,input_epoch)
        self.obstarget=FixedTarget(name=name,coord=self.coordinates)

        if self.telescope_status.get('precession')==True:
            self.coordinates, self.ra_out, self.dec_out = self.coordprecess(self.coordinates,current_epoch,input_epoch)

        self.target_altaz = self.coordinates.transform_to(AltAz(obstime=Time.now(),location=self.MRO_loc))

        self.alt=str("{0.alt:.2}".format(self.target_altaz))
        self.split_alt=self.alt.split(' ')
        self.slew_altitude=self.split_alt[0]

        if float(self.slew_altitude) > float(self.horizonlimit):

            self.decimalcoords=self.coordinates.to_string('decimal')

            self.LST=str(self.control.currentLSTPos.GetLabel())
            self.LST=self.LST.split(':')
            self.LST=float(self.LST[0])+float(self.LST[1])/60.+float(self.LST[2])/3600.
            self.log("First Slew LST: "+str(self.LST))
            #self.log([input_ra,input_dec,current_epoch])
            command="slew"+' '+str(self.decimalcoords)+' '+str(self.LST)
            if self.telescope_status.get("tracking") == True:
                #self.protocol.sendCommand("track off")
                self.command_queue.put("track off")
                self.log("Turning tracking off for slew duration")
                self.code_timer_Slew.Start(self.stop_time, oneShot = True)
                return
            elif self.telescope_status.get("tracking") == False:
                #self.protocol.sendCommand(command)
                self.command_queue.put(command)
                self.target_coords['Name']=name  #Store name of target for pointing routine
                if self.telescope_status.get('precession')==True:
                    self.target_coords['RA']= self.ra_out #Store target RA for pointing routine
                    self.target_coords['DEC']=self.dec_out #Store target DEC for pointing routine
                    self.log('Precessed RA: '+str(self.ra_out))
                    self.log('Precessed DEC: '+str(self.dec_out))
                else:
                    self.target_coords['RA']= self.input_frame.ra.degree #Store target RA for pointing routine
                    self.target_coords['DEC']=self.input_frame.dec.degree #Store target DEC for pointing routine
                self.telescope_status['slewing'] = not self.telescope_status.get('slewing')
                thread.start_new_thread( self.velwatch,(True, self.decimalcoords,) )
                return

        elif float(self.slew_altitude) < float(self.horizonlimit):
            dlg = wx.MessageDialog(self,
                           "Target is below current minimum altitude, cannot slew.",
                           "Error", wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.log("Error: Attempted slew altitude below 20 degrees.")
            return

    elif self.telescope_status.get('slewing')==True:
        #self.protocol.sendCommand("stop")
        self.command_queue.put("stop")
        self.log("Telescope Slew/Jog Command Stopped Early.")

        #self.control.slewButton.SetLabel('Start Slew')
        #self.control.slewButton.SetBackgroundColour("Light Slate Blue")
        #self.sb.SetStatusText('Slewing: False',1)

        self.telescope_status['slewing'] = False

    return
# ----------------------------------------------------------------------------------

def haltmotion(self,event):
    '''
    Halt Telescope motion, emergency button, use stop slew during slewing if possible.

        Args:
            event: handler to allow function to be tethered to a wx widget. Tethered to the "HALT MOTION" button in the telescope control tab.

        Returns:
            None

    '''
    #self.protocol.sendCommand("halt")
    self.command_queue.put("halt")

    self.log("WARNING: Emergency Stop Button pressed. A full restart of the TCC is required.")
    return

# ----------------------------------------------------------------------------------

def timeSlew(self,event):
    """
    After tracking is turned off, execute slew.

        Args:
            event: handler to allow function to be tethered to a wx widget.

        Returns:
            None
    """
    print "Timer Ended"
    name=self.control.targetNameText.GetValue()
    input_ra=self.control.targetRaText.GetValue()
    input_dec=self.control.targetDecText.GetValue()
    input_epoch=self.control.targetEpochText.GetValue()
    current_epoch=self.control.currentEpochPos.GetLabel()

    self.input_frame = SkyCoord(input_ra,input_dec,frame='icrs')

    self.MRO_loc=EarthLocation(lat=46.9528*u.deg, lon=-120.7278*u.deg, height=1198*u.m)
    self.inputcoordSorter(input_ra,input_dec,input_epoch)
    self.obstarget=FixedTarget(name=name,coord=self.coordinates)

    if self.telescope_status.get('precession')==True:
        self.coordinate, self.ra_out, self.dec_out = self.coordprecess(self.coordinates,current_epoch,input_epoch)

    self.decimalcoords=self.coordinates.to_string('decimal')

    self.LST=str(self.control.currentLSTPos.GetLabel())
    self.LST=self.LST.split(':')
    self.LST=float(self.LST[0])+float(self.LST[1])/60.+float(self.LST[2])/3600.
    self.log("First Slew LST: "+str(self.LST))
    #self.log([input_ra,input_dec,current_epoch])
    command="slew"+' '+str(self.decimalcoords)+' '+str(self.LST)

    #self.protocol.sendCommand(command)
    self.command_queue.put(command)
    self.target_coords['Name']=name  #Store name of target for pointing routine
    if self.telescope_status.get('precession')==True:
        self.target_coords['RA']= self.ra_out #Store target RA for pointing routine
        self.target_coords['DEC']=self.dec_out #Store target DEC for pointing routine
        self.log('Precessed RA: '+str(self.ra_out))
        self.log('Precessed DEC: '+str(self.dec_out))
    else:
        self.log("Warning: Precession is not on.")
        self.target_coords['RA']= self.input_frame.ra.degree #Store target RA for pointing routine
        self.target_coords['DEC']=self.input_frame.dec.degree #Store target DEC for pointing routine
        self.log('unprecessed RA: '+str(self.ra_out))
        self.log('unprecessed DEC: '+str(self.dec_out))
    self.telescope_status['slewing'] = True
    thread.start_new_thread(self.velwatch,(True,self.decimalcoords,))
    return
# ----------------------------------------------------------------------------------
def velwatch(self, secondary_slew = False, data=None):
    """
    During a slew, continually track telescope velocity through velmeasure.
        Args:
            None
        Returns:
            None
    """
    #d=self.protocol.sendCommand("velmeasure")
    #d.addCallback(self.velmeasure)
    time.sleep(1.0)
    while self.telescope_status.get('slewing')==True:
        #d=self.protocol.sendCommand("velmeasure")
        if secondary_slew:
            self.command_queue.put("velmeasureSS")
            print "Beginning First Slew"
            #d.addCallback(self.velmeasureSS)
            time.sleep(0.511)
        else:
            self.command_queue.put("velmeasure")
            #d.addCallback(self.velmeasure)
            time.sleep(0.511)
    if secondary_slew:
        wx.CallAfter(self.log,("Completed First Slew"))
        self.LST=str(self.control.currentLSTPos.GetLabel())
        self.LST=self.LST.split(':')
        self.LST=float(self.LST[0])+float(self.LST[1])/60.+float(self.LST[2])/3600.
        wx.CallAfter(self.log,("Secondary Slew LST: "+str(self.LST)))
        command="slew"+' '+str(data)+' '+str(self.LST)
        wx.CallAfter(self.log,("Beginning Secondary Slew"))
        #self.protocol.sendCommand(command)
        self.command_queue.put(command)
        self.telescope_status["slewing"]=True
        while self.telescope_status.get('slewing')==True:
            #d=self.protocol.sendCommand("velmeasure")
            time.sleep(0.511)
            self.command_queue.put("velmeasure")
            #d.addCallback(self.velmeasure)
            #time.sleep(0.511)
        #self.protocol.sendCommand("stop")
        wx.CallAfter(self.log,("Completed Secondary Slew"))
    return

# ----------------------------------------------------------------------------------
def velmeasure(self,msg):
    """
    Get telescope velocity. Server sends back a boolean value to indicate if the
    telescope has stopped moving. When the telescope has stopped moving, flips
    TCC slewing == False
        Args:
            None
        Returns:
            None
    """
    print repr(msg)
    msg=int(msg)
    if msg==1:
        self.telescope_status['slewing']=False
        print "Slewing == False"
        wx.CallAfter(self.slewbutton_toggle)
        if self.telescope_status.get('tracking')==True:
            #self.protocol.sendCommand("track on "+str(self.dict.get('RAtrackingRate')))
            self.command_queue.put("track on "+str(self.dict.get('RAtrackingRate')))
            #print "I made it"
        return

    if msg==0:
        self.telescope_status['slewing']=True
# ----------------------------------------------------------------------------------
def velmeasureSS(self,msg):
    """
    Get telescope velocity. Server sends back a boolean value to indicate if the
    telescope has stopped moving. Secondary Slew attempts a second slew to counteract
    movement of target over the slew period, then sends back to velmeasure.
        Args:
            None
        Returns:
            None
    """
    print repr(msg)
    msg=int(msg)
    if msg==1:
        self.telescope_status['slewing']=False

    if msg==0:
        self.telescope_status['slewing']=True


# ----------------------------------------------------------------------------------
def checkslew(self):
    """
    Continually check the value of the slewing key in self.telescope_status to keep the
    client in the correct state. When slewing is true, certain features are disabled.
        Args:
            None
        Returns:
            None
    """
    while True:
        if self.telescope_status.get('slewing')==False:
            wx.CallAfter(self.slewbuttons_on,True,self.telescope_status.get('tracking'))
        if self.telescope_status.get('slewing')==True:
            wx.CallAfter(self.slewbuttons_on,False,self.telescope_status.get('tracking'))
        time.sleep(0.25)

# ----------------------------------------------------------------------------------

def slewbuttons_on(self,bool,track):
    """
    Turn on/off slew buttons.
        Args:
            bool (Boolean): Sets whether to enable or disable buttons
            track (Boolean): Current tracking status
        Returns:
            None
    """
    self.control.trackButton.Enable(bool)
    self.init.parkButton.Enable(bool)
    self.init.coverposButton.Enable(bool)
    self.control.jogNButton.Enable(bool)
    self.control.jogWButton.Enable(bool)
    self.control.jogEButton.Enable(bool)
    self.control.jogSButton.Enable(bool)
    if not bool:
        self.control.slewButton.SetLabel('Stop Slew')
        self.control.slewButton.SetBackgroundColour('Firebrick')
        self.sb.SetStatusText('Slewing: True',1)
    elif bool:
        self.control.slewButton.SetLabel('Start Slew')
        self.control.slewButton.SetBackgroundColour('Light Slate Blue')
        self.sb.SetStatusText('Slewing: False',1)

# ----------------------------------------------------------------------------------
def slewbutton_toggle(self):
    """
    Toggle slew button label.
        Args:
            None
        Returns:
            None
    """
    self.control.slewButton.SetLabel('Start Slew')
    self.control.slewButton.SetBackgroundColour('Light Slate Blue')
    self.sb.SetStatusText('Slewing: False',1)

# ----------------------------------------------------------------------------------
