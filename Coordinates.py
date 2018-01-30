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


def inputcoordSorter(self,ra,dec,epoch):
    '''
    Take in any valid RA/DEC format and read it into an Astropy SkyCoord object. Format of RA must be consistent with format of DEC. Supports galactic coordinates as well, to
    input galactic coordinates, set the ra argument to be l=00h00m00s and the dec argument to be b=+00h00m00s. These will be put into a galactic skycoord frame which will then
    be transformed into an fk5 skycoord object.

        Args:
            ra (string): Right Ascension of object. Valid forms are decimal degrees, hh:mm:ss , hh mm ss ,XXhXXmXXs and l=XXhXXmXXs
            dec (string): Declination of object. Valid forms are decimal degrees, hh:mm:ss, hh mm ss, XXdXXmXXs and b=XXdXXmXXs
            epoch (string): The epoch that the RA/DEC are specific to (usually J2000).

        Returns:
            self.coordinates:
    '''

    self.validity=False
    self.galactic_coords=False

    #first check to see if galactic coordinates
    if str(ra)[0:2]== 'l=' or str(ra)[0:2] == 'L=':
        self.galactic_coords=True
        self.galcoordinates = SkyCoord("galactic", l=str(ra)[2:], b=str(dec)[2:])
        self.coordinates=self.galcoordinates.transform_to('fk5')
        self.validity=True
        return self.coordinates

    deg_input=True

    try:
        val=float(ra)
    except ValueError:
        deg_input=False

    if deg_input==True:
        self.coordinates=SkyCoord(ra=float(ra)*u.degree,dec=float(dec)*u.degree,frame='icrs',equinox=str(epoch))
        self.validity=True
        return self.coordinates
    elif str(ra)[2]== 'h' and str(ra)[5]== 'm':
        self.coordinates=SkyCoord(ra,dec,frame='icrs',equinox=str(epoch))
        self.validity=True
        return self.coordinates
    elif str(ra)[2]== ' ' and str(ra)[5]== ' ':
        self.coordinates=SkyCoord(str(ra)+' '+str(dec), unit=(u.hourangle,u.deg),equinox=str(epoch))
        self.validity=True
        return self.coordinates
    elif str(ra)[2]== ':' and str(ra)[5]== ':':
        self.coordinates=SkyCoord(str(ra)+' '+str(dec), unit=(u.hourangle,u.deg),equinox=str(epoch))
        self.validity=True
        return self.coordinates
    elif self.validity==False:
        dlg = wx.MessageDialog(self,
                       "Not a valid RA or DEC format. Please input an RA and DEC in any of the following forms: decimal degrees, 00h00m00s, 00:00:00, 00 00 00. If attempting to input galactic coordinates\n please enter in form l=00h00m00s and b=+00d00m00s in RA and DEC fields.",
                       "Error", wx.OK|wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return

# ----------------------------------------------------------------------------------
def coordprecess(self,coords,epoch_now,epoch):
    '''
    coordprecess() generates an astropy skycoord object with RA/DEC precessed to the current epoch.
    Precession is calculated using astronomical precession approximations centered on J2000. Note that
    while this function allows flexibility in coordinate epoch, it may fail at arbitrary coordinate epochs.
    It is recommended that when using an epoch that is not J2000, that the user transform to J2000 first.

        Args:
            coords(astropy.skycoord): astropy.skycoord object containing the unprecessed coordinates.
            epoch_now(string): The epoch of the date the user desires precession to. Usually the current epoch.
            epoch(string): The epoch of the coordinates. J2000 is recommended.
        Returns:
            self.coordinates(astropy.skycoord): astropy.skycoord object containing the new precessed coordinates.

    '''

    ra_in=coords.ra.deg
    dec_in=coords.dec.deg
    #ep_in=float(epoch[1:])
    ep_in=epoch
    ep_now_in=float(epoch_now)
    print ra_in, dec_in, ep_in, ep_now_in

    """   #By Calculation
    T=(ep_now_in - ep_in)/100.0
    M=1.2812323*T+0.0003879*(T**2)+0.0000101*(T**3)
    N=0.5567530*T-0.0001185*(T**2)-0.0000116*(T**3)
    #print T, M, N

    d_ra= M + N*np.sin(ra_in* np.pi / 180.)*np.tan(dec_in* np.pi / 180.)
    d_dec=N*np.cos(ra_in* np.pi / 180.)
    #print d_ra, d_dec
    """

    #By Astropy -- assumes input coords are J2000 currently
    coord_frame = SkyCoord(ra=ra_in*u.degree,dec=dec_in*u.degree,frame = 'icrs',equinox=str(ep_in))
    coord_fk5 = coord_frame.transform_to("fk5")
    precessed_coords = coord_fk5.transform_to(FK5(equinox='J'+str(ep_now_in)))

    self.ra_out=precessed_coords.ra.degree
    self.dec_out=precessed_coords.dec.degree

    #self.ra_out=ra_in+d_ra
    #self.dec_out=dec_in+d_dec
    print self.ra_out,self.dec_out
    #self.log('Precessed RA: '+str(self.ra_out))
    #self.log('Precessed DEC: '+str(self.dec_out))
    self.coordinates=SkyCoord(ra=float(self.ra_out)*u.degree,dec=float(self.dec_out)*u.degree,frame='icrs',equinox=str(epoch_now))
    return self.coordinates, self.ra_out, self.dec_out

# ----------------------------------------------------------------------------------Coord
