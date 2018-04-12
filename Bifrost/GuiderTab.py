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

class GuiderPerformance(wx.Panel):
    """Secondary tab for guider operation, view guider performance from this panel.
    Not currently enabled."""
    # ----------------------------------------------------------------------------------
    def __init__(self,parent, debug, night):
        """Create the Guider Performance panel"""
        wx.Panel.__init__(self,parent)

        #Initialize Figure Canvas Structure
        self.dpi = 100
        self.fig = Figure((7.0,4.5), dpi=self.dpi)
        self.canvas = FigCanvas(self,-1, self.fig)

        #Guider Perfomance Initialization
        self.ax1 = self.fig.add_subplot(211)
        self.ax1.set_title('Guider Performance', size='small')
        self.ax1.set_ylabel('Offset (arcmin)', size='x-small')

        self.ax1.plot([1,2,3], label="Seeing")
        self.ax1.plot([3,2,1], label="Line 2")
        self.ax1.legend(bbox_to_anchor=(0,1.02,1.,.102),loc=3,ncol=2,mode="expand",borderaxespad=0.)

        for xlabel_i in self.ax1.get_xticklabels():
            xlabel_i.set_fontsize(8)
        for ylabel_i in self.ax1.get_yticklabels():
            ylabel_i.set_fontsize(8)

        self.ax2= self.fig.add_subplot(212)
        self.ax2.set_xlabel('Time (PT)', size='x-small')
        self.ax2.set_ylabel('fwhm (arcsec)', size='x-small')
        for xlabel_i in self.ax2.get_xticklabels():
            xlabel_i.set_fontsize(8)
        for ylabel_i in self.ax2.get_yticklabels():
            ylabel_i.set_fontsize(8)

        self.toolbar = NavigationToolbar(self.canvas)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.canvas, 0, wx.ALIGN_CENTER)
        self.vbox.Add(self.toolbar,0, wx.ALIGN_CENTER)

        self.SetSizer(self.vbox)
        self.vbox.Fit(self)

###########################################################################################
class GuiderControl(wx.Panel):
    """Primary tab for guider operation, utilize guider functions from this panel. Not
    currently enabled."""
    # ----------------------------------------------------------------------------------
    def __init__(self,parent, debug, night):
        """Create Guider Control panel"""
        wx.Panel.__init__(self,parent)

        # add visual representation of stepper and periscope position
        # show computation for decovultion of position
        # image display w/ vector offset arrows
        # need to define guider directory and filename structure

        self.Buffer = None
        self.center=[200,275] #Center Coordinate for finder image and guider image plots
        self.dc = None
        self.rotAng=0 #Guider Rotation Angle

        #############################################################

        #Righthand Figure; guider image
        self.fig_r = Figure((4,4))
        self.canvas_r = FigCanvas(self,-1, self.fig_r)
        self.ax_r = self.fig_r.add_subplot(111)
        self.ax_r.set_axis_off()
        self.fig_r.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)

        #############################################################

        #Lefthand Figure; finder image with periscope overlay
        self.fig_l = Figure((4,4))
        self.canvas_l = FigCanvas(self,-1, self.fig_l)
        self.ax_l = self.fig_l.add_subplot(111)
        self.ax_l.set_axis_off()
        self.cir = matplotlib.patches.Circle( (150,150), radius=125, fill=False, color='steelblue',linewidth=2.5)
        self.cir1 = matplotlib.patches.Circle( (150,150), radius=126, fill=False, color='k',linewidth=1.0)
        self.line= matplotlib.patches.Rectangle( (150,150), height=125, width=2, fill=True, color='k')
        self.ax_l.add_patch(self.cir) #Periscope Overlay
        self.ax_l.add_patch(self.cir1) #Periscope Overlay
        self.ax_l.add_patch(self.line) #Periscope Overlay
        self.fig_l.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)

        #############################################################

        #Guider Controls Box

        #Row 1: Guider Exposure
        self.guiderTimeLabel = wx.StaticText(self, size=(100, -1))
        self.guiderTimeLabel.SetLabel('Exposure: ')
        self.guiderTimeText = wx.TextCtrl(self, size=(100, -1))
        self.guiderTimeText.SetValue('10.0')
        self.guiderExposureButton = wx.Button(self, -1, 'Guider Exposure', size=(125, -1))
        #Row 2: Guider Rotation
        self.guiderRotLabel = wx.StaticText(self, size=(100, -1))
        self.guiderRotLabel.SetLabel('Rot. Angle: ')
        self.guiderRotText = wx.TextCtrl(self, size=(100, -1))
        self.guiderRotText.SetValue('0.0')
        self.guiderRotButton = wx.Button(self, -1, 'Set Rotation', size=(125, -1))
        #Row 3: Guiding Controls
        self.findStarsButton = wx.Button(self, -1, "Auto Find Guide Stars",size=(150,-1))
        self.startGuidingButton = wx.Button(self, -1, "Start Guiding",size=(150,-1))

        #############################################################

        #Guider Jog Controls
        self.jogNButton = wx.Button(self, -1, 'N',size=(75,-1))
        self.jogSButton = wx.Button(self, -1, 'S',size=(75,-1))
        self.jogWButton = wx.Button(self, -1, 'W',size=(75,-1))
        self.jogEButton = wx.Button(self, -1, 'E',size=(75,-1))

        #############################################################

        #Guider Focus Controls
        self.focusIncPlusButton = wx.Button(self, -1, 'Increment Positive')
        self.focusIncNegButton = wx.Button(self, -1, 'Increment Negative')
        self.focusAbsText = wx.TextCtrl(self,size=(75,-1))
        self.focusAbsText.SetValue('1500')
        self.focusAbsMove = wx.Button(self,-1,'Move Relative')

        #############################################################

        #Sizers: Create Box Sizers
        self.vbox=wx.BoxSizer(wx.VERTICAL)
        self.hbox=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3=wx.BoxSizer(wx.HORIZONTAL)
        self.gbox=wx.GridSizer(rows=2, cols=3, hgap=0, vgap=5)
        self.gbox3=wx.GridSizer(rows=2, cols=2, hgap=5, vgap=5)
        self.ghbox=wx.BoxSizer(wx.HORIZONTAL)

        #Guider Controls Box Sizer
        self.clabel=wx.StaticBox(self,label="Guider Controls")
        self.vboxc= wx.StaticBoxSizer(self.clabel, wx.VERTICAL)
        #Guider Focus Controls Box Sizer
        self.flabel=wx.StaticBox(self,label="Focus Guider")
        self.vboxf= wx.StaticBoxSizer(self.flabel, wx.VERTICAL)
        #Jog Guider Field Box Sizer
        self.jlabel=wx.StaticBox(self,label="Jog Telescope")
        self.vboxj= wx.StaticBoxSizer(self.jlabel, wx.VERTICAL)

        #Sizers: Populate Box Sizers
        self.gbox3.Add(self.focusIncPlusButton, 0, wx.ALIGN_LEFT)
        self.gbox3.Add(self.focusAbsText, 0, wx.ALIGN_LEFT)
        self.gbox3.Add(self.focusIncNegButton, 0, wx.ALIGN_LEFT)
        self.gbox3.Add(self.focusAbsMove, 0, wx.ALIGN_LEFT)

        self.vboxf.Add(self.gbox3,0,wx.ALIGN_CENTER)

        self.hbox3.Add(self.jogWButton,0,wx.ALIGN_LEFT)
        self.hbox3.AddSpacer(5)
        self.hbox3.Add(self.jogEButton,0,wx.ALIGN_LEFT)

        self.vboxj.Add(self.jogNButton,0,wx.ALIGN_CENTER)
        self.vboxj.AddSpacer(5)
        self.vboxj.Add(self.hbox3,0,wx.ALIGN_CENTER)
        self.vboxj.AddSpacer(5)
        self.vboxj.Add(self.jogSButton,0,wx.ALIGN_CENTER)

        self.gbox.Add(self.guiderTimeLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.guiderTimeText, 0, wx.ALIGN_LEFT)
        self.gbox.Add(self.guiderExposureButton,0,wx.ALIGN_LEFT)
        self.gbox.Add(self.guiderRotLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.guiderRotText, 0, wx.ALIGN_LEFT)
        self.gbox.Add(self.guiderRotButton,0,wx.ALIGN_LEFT)
        #self.gbox.Add(self.finderLabel, 0, wx.ALIGN_RIGHT)
        #self.gbox.Add(self.finderText, 0, wx.ALIGN_LEFT)
        #self.gbox.Add(self.finderButton,0,wx.ALIGN_LEFT)

        self.hbox.Add(self.findStarsButton, 0, wx.ALIGN_LEFT)
        self.hbox.AddSpacer(15)
        self.hbox.Add(self.startGuidingButton, 0, wx.ALIGN_RIGHT)

        self.vboxc.Add(self.gbox,0,wx.ALIGN_CENTER)
        self.vboxc.AddSpacer(10)
        self.vboxc.Add(self.hbox,0,wx.ALIGN_CENTER)

        self.ghbox.AddSpacer(20)
        self.ghbox.Add(self.vboxc,0,wx.ALIGN_LEFT)
        self.ghbox.AddSpacer(20)
        self.ghbox.Add(self.vboxj,0,wx.ALIGN_LEFT)
        self.ghbox.AddSpacer(20)
        self.ghbox.Add(self.vboxf,0,wx.ALIGN_LEFT)

        self.hbox2.Add(self.canvas_l,0,wx.ALIGN_CENTER)
        self.hbox2.AddSpacer(50)
        self.hbox2.Add(self.canvas_r,0,wx.ALIGN_CENTER)

        self.vbox.AddSpacer(10)
        self.vbox.Add(self.hbox2,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.ghbox,0,wx.ALIGN_LEFT)


        self.SetSizer(self.vbox)

###########################################################################################
