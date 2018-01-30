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

def FinderOpen(self,event):
    """
    Open a new window with a finder chart of the selected item in the target list.
        Args:
            event: handler to allow function to be tethered to a wx widget.
        Returns:
            Plot Finder Chart
    """

    sel_item=self.target.targetList.GetFocusedItem()
    input_ra=self.target.targetList.GetItem(sel_item,col=1).GetText()
    input_dec=self.target.targetList.GetItem(sel_item,col=2).GetText()
    input_epoch=self.target.targetList.GetItem(sel_item,col=3).GetText()

    self.inputcoordSorter(input_ra,input_dec,input_epoch)
    print self.plot_open
    if self.plot_open == True:
        plt.close()
        self.plot_open =False

    self.targetobject=FixedTarget(name=self.target.targetList.GetItem(sel_item,0).GetText(),coord=self.coordinates)

    self.finder_routine_complete = False
    f_thread=threading.Thread(target=self.GenerateFinder,args=(self.targetobject,),name="Finder Chart")
    f_thread.daemon = True
    f_thread.start()
    #f_thread.join(10)
    thread.start_new_thread(self.timeout,(f_thread,30.0))
    #mp.freeze_support()
    #p = mp.Process(target=self.GenerateFinder,args=(self.targetobject,))
    #self.process_list.append(p)
    #p.start()
    #p.join(5)

# ----------------------------------------------------------------------------------
def GenerateFinder(self, target, survey='DSS', fov_radius=18*u.arcmin,
                      log=False, ax=None, grid=False, reticle=False,
                      style_kwargs=None, reticle_style_kwargs=None):
    """
    Download command for finder chart of selected object. Look at Astroplan plot_finder_image
    for detailed documentation.
        Args:
            None
        Returns:
            None
    """
    #__all__ = ['plot_finder_image']
    print "Generating Finder"
    coord = target if not hasattr(target, 'coord') else target.coord
    position = coord.icrs
    coordinates = 'icrs'
    target_name = None if isinstance(target, SkyCoord) else target.name

    hdu = SkyView.get_images(position=position, coordinates=coordinates,
                                 survey=survey, radius=fov_radius, grid=grid)[0][0]
    print hdu
    #wcs = WCS(hdu.header)
    wx.CallAfter(self.plotFinder, ax, hdu, grid, log, fov_radius, reticle,
    style_kwargs, reticle_style_kwargs, target_name)
    #self.plotFinder(ax,hdu,grid,log,fov_radius,reticle,style_kwargs,reticle_style_kwargs,target_name)

# ----------------------------------------------------------------------------------

def plotFinder(self, ax, hdu, grid, log, fov_radius,reticle,
style_kwargs, reticle_style_kwargs, target_name):
    """
    Plot Command for finder chart downloaded in GenerateFinder(). Look at Astroplan plot_finder_image
    for detailed documentation.
        Args:
            None
        Returns:
            None
    """
    print "Plotting Finder"
    wcs = WCS(hdu.header)
    # Set up axes & plot styles if needed.
    if ax is None:
        ax = plt.gca(projection=wcs)
    if style_kwargs is None:
        style_kwargs = {}
    style_kwargs = dict(style_kwargs)
    style_kwargs.setdefault('cmap', 'Greys')
    style_kwargs.setdefault('origin', 'lower')
    print "Plotting"
    if log:
        image_data = np.log(hdu.data)
    else:
        image_data = hdu.data
    ax.imshow(image_data, picker=True, **style_kwargs)

    # Draw reticle
    if reticle:
        pixel_width = image_data.shape[0]
        inner, outer = 0.03, 0.08

        if reticle_style_kwargs is None:
            reticle_style_kwargs = {}
        reticle_style_kwargs.setdefault('linewidth', 2)
        reticle_style_kwargs.setdefault('color', 'm')

        ax.axvline(x=0.5*pixel_width, ymin=0.5+inner, ymax=0.5+outer,
               **reticle_style_kwargs)
        ax.axvline(x=0.5*pixel_width, ymin=0.5-inner, ymax=0.5-outer,
               **reticle_style_kwargs)
        ax.axhline(y=0.5*pixel_width, xmin=0.5+inner, xmax=0.5+outer,
               **reticle_style_kwargs)
        ax.axhline(y=0.5*pixel_width, xmin=0.5-inner, xmax=0.5-outer,
               **reticle_style_kwargs)

    # Labels, title, grid
    ax.set(xlabel='RA', ylabel='DEC')
    if target_name is not None:
        ax.set_title(target_name)
    ax.grid(grid)

    # Redraw the figure for interactive sessions.
    ax.figure.canvas.draw()
    self.plot_open = True
    self.finder_routine_complete = True
    print "plotted"
    self.target.finder_button.Enable()
    plt.show()
    return ax, hdu
# ----------------------------------------------------------------------------------
def timeout(self,t,value):
    """
    Timeout for Load Finder Chart if the process fails to download.
        Args:
            t (threading.Thread): Thread object to have a timeout associated with it
            value (float): Timeout duration in seconds
        Returns:
            None
    """
    #t.join(value)
    dot_count=0
    timeout=0
    while self.finder_routine_complete == False:
        wx.CallAfter(self.target.finder_button.Disable)
        wx.CallAfter(self.target.finder_button.SetLabel,("Downloading"+"."*dot_count))
        if dot_count == 3:
            dot_count=0
        dot_count+=1
        timeout+=1
        time.sleep(1.0)
        if timeout>=value:
            wx.CallAfter(self.log,("Failed to Load Finder Chart. Try again. Restart Bifrost Software if issue persists."))
            wx.CallAfter(self.target.finder_button.Enable)
            wx.CallAfter(self.target.finder_button.SetLabel,("Load Finder Chart"))
            self.finder_routine_complete=True
            break

    t.join()
    wx.CallAfter(self.target.finder_button.Enable)
    wx.CallAfter(self.target.finder_button.SetLabel,("Load Finder Chart"))
    return

# ----------------------------------------------------------------------------------
