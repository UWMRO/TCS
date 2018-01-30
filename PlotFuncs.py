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

def LoadFinder(self, input_ra,input_dec,input_epoch):
    """
    Use Astroplan's plot_finder_image function to plot the finder image of the current target.
    Threaded so that normal TCC operation does not hang for finder chart download.

        Args:
            input_ra (string): Right Ascension of object. Valid forms are decimal degrees, hh:mm:ss , hh mm ss ,XXhXXmXXs and l=XXhXXmXXs
            input_dec (string): Declination of object. Valid forms are decimal degrees, hh:mm:ss, hh mm ss, XXdXXmXXs and b=XXdXXmXXs
            input_epoch (string): The epoch that the RA/DEC are specific to (usually J2000).

        Returns:
            None
    """

    self.coordinates = self.inputcoordSorter(input_ra,input_dec,input_epoch)
    self.finder_object=FixedTarget(name=None,coord=self.coordinates)
    #wx.CallAfter(plot_finder_image,self.finder_object,fov_radius=18*u.arcmin,ax=self.guiderControl.ax_l,reticle=False, log=False,)
    return

# ----------------------------------------------------------------------------------
def dyn_airmass(self,tgt,obs,count):
    """
    Continuously calculates the airmass using observer information and target information. Airmass is calculated using the secz function in astropy.
    Dynamically updates in the target list and allows a quick read of the airmass for any given target.

        Args:
            tgt (FixedTarget): Astroplan FixedTarget object for the target, details target name and RA/DEC coordinates.
            obs (astroplan.Observer): Astroplan Observer object for observer location, details longitude, latitude and elevation of observer.
            count (integer): list counter that tracks the position of the target in the wx listctrl object, used to append airmass to correct row.

        Returns:
            a (float): airmass at current time.

    """
    while self.calculate==True:
        a= obs.altaz(Time.now(),tgt).secz
        if a > 8 or a < 0:
            a="N/A"
        wx.CallAfter(self.target.targetList.SetStringItem,count,5,str(a))
        #self.target.targetList.SetStringItem(count,5,str(a))
        time.sleep(1)

# ----------------------------------------------------------------------------------
def target_plot(self,event):
    '''
    Plot the selected targets position over the next 8 hours utilizing astroplan's plot_sky() method. This method plot with respect to target selected in
    the target list tab and not the GUI-set current target. Individual points are plotted with 1 hour cadence. Red point indicates current position
    to specify direction of target trajectory. Note: Using this while a currentplot is being displayed will overwrite the current plot, this
    overplotting has complications between radial and cartesian plots and will produce strange results. Exit the working plot before sending a new plot command.

        Args:
            event: handler to allow function to be tethered to a wx widget. Tethered to the "Plot Target" button in the target list tab.

        Returns:
            Radial plot of target altitude and azimuth in new window.

    '''
    sel_item=self.target.targetList.GetFocusedItem()
    input_ra=self.target.targetList.GetItem(sel_item,col=1).GetText()
    input_dec=self.target.targetList.GetItem(sel_item,col=2).GetText()
    input_epoch=self.target.targetList.GetItem(sel_item,col=3).GetText()

    current_epoch=self.control.currentEpochPos.GetLabel()

    self.inputcoordSorter(input_ra,input_dec,input_epoch)

    if self.telescope_status.get('precession')==True:
        self.coordprecess(self.coordinates,current_epoch,input_epoch)

    self.targetobject=FixedTarget(name=self.target.targetList.GetItem(sel_item,0).GetText(),coord=self.coordinates)
    self.Obstime=Time.now()
    self.plot_times = self.Obstime + np.linspace(0, 8, 8)*u.hour
    self.target_style={'color':'Black'}
    self.initial_style={'color':'r'}
    print self.plot_open
    if self.plot_open == True:
        plt.close()
        self.plot_open = False

    plot_sky(self.targetobject, self.MRO, self.plot_times,style_kwargs=self.target_style)
    plt.legend(shadow=True, loc=2)
    plot_sky(self.targetobject, self.MRO, self.Obstime,style_kwargs=self.initial_style)
    self.plot_open = True
    plt.show()


# ----------------------------------------------------------------------------------
def airmass_plot(self,event):
    '''
    Plot the selected targets airmass curve over the next 10 hours utilizing astroplan's plot_airmass() method. This method plot with respect to target selected in
    the target list tab and not the GUI-set current target. Airmass warning limits at 2 and 2.5 are given as yellow and red lines respectively. Note: Using this while a current
    plot is being displayed will overwrite the current plot, this overplotting has complications between radial and cartesian plots and will produce strange results. Exit the working plot
    before sending a new plot command.

        Args:
            event: handler to allow function to be tethered to a wx widget. Tethered to the "Airmass Curve" button in the target list tab.

        Returns:
            Airmass curve of target in new window.

    '''
    sel_item=self.target.targetList.GetFocusedItem()
    input_ra=self.target.targetList.GetItem(sel_item,col=1).GetText()
    input_dec=self.target.targetList.GetItem(sel_item,col=2).GetText()
    input_epoch=self.target.targetList.GetItem(sel_item,col=3).GetText()
    current_epoch=self.control.currentEpochPos.GetLabel()

    self.inputcoordSorter(input_ra,input_dec,input_epoch)

    if self.telescope_status.get('precession')==True:
        self.coordprecess(self.coordinates,current_epoch,input_epoch)

    self.targetobject=FixedTarget(name=self.target.targetList.GetItem(sel_item,0).GetText(),coord=self.coordinates)

    self.Obstime=Time.now()
    self.plot_times = self.Obstime + np.linspace(0, 10, 24)*u.hour
    self.target_style={'color':'Black'}
    print self.plot_open
    if self.plot_open == True:
        plt.close()
        self.plot_open =False
    self.airmass=plot_airmass(self.targetobject, self.MRO, self.plot_times,style_kwargs=self.target_style)

    plt.axhline(y=2,linestyle='--',color='orange')
    plt.axhline(y=2.5,linestyle='--',color='r')
    plt.legend(shadow=True, loc=1)
    self.plot_open = True
    plt.show()


# ----------------------------------------------------------------------------------
