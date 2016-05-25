#!/user/local/bin python
import time
import wx
import os
import subprocess
import re
import astropy
from astropy.time import Time
import thread
import ephem
import matplotlib
import datetime
import math
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt
import matplotlib.dates as dt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
from pytz import timezone
import scipy
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from scipy import linspace, polyval, polyfit, sqrt, stats, randn
from astroplan import Observer, FixedTarget
from astroplan.plots import plot_sky,plot_airmass
import astropy.units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, Galactic, FK4, FK5
from astroplan.plots.finder import plot_finder_image
from astroquery.skyview import SkyView
import wcsaxes

from twisted.internet import wxreactor
wxreactor.install()
from twisted.internet import reactor, protocol, defer
from twisted.protocols import basic

class Control(wx.Panel):
    def __init__(self,parent, debug, night):
        wx.Panel.__init__(self,parent)
        
        #self.parent = parent
        
        self.logBox = wx.TextCtrl(self,size=(600,200), style= wx.TE_READONLY | wx.TE_MULTILINE | wx.VSCROLL)

        #Input individual target, use astropy and a lot of error checking to solve format failures
        self.targetNameLabel = wx.StaticText(self, size=(75,-1))
        self.targetNameLabel.SetLabel('Name: ')
        self.targetNameText = wx.TextCtrl(self,size=(100,-1))

        self.targetRaLabel = wx.StaticText(self, size=(75,-1))
        self.targetRaLabel.SetLabel('RA: ')
        self.targetRaText = wx.TextCtrl(self,size=(100,-1))

        self.targetDecLabel = wx.StaticText(self, size=(75,-1))
        self.targetDecLabel.SetLabel('DEC: ')
        self.targetDecText = wx.TextCtrl(self,size=(100,-1))

        self.targetEpochLabel = wx.StaticText(self, size=(75,-1))
        self.targetEpochLabel.SetLabel('EPOCH: ')
        self.targetEpochText = wx.TextCtrl(self,size=(100,-1))

        self.targetMagLabel = wx.StaticText(self, size=(75,-1))
        self.targetMagLabel.SetLabel('V Mag: ')
        self.targetMagText = wx.TextCtrl(self,size=(100,-1))

        #Current Positions
        self.currentNameLabel = wx.StaticText(self, size=(75,-1))
        self.currentNameLabel.SetLabel('Name:')
        self.currentNamePos = wx.StaticText(self,size=(100,-1))
        self.currentNamePos.SetLabel('Unknown')
        self.currentNamePos.SetForegroundColour((255,0,0))

        self.currentRaLabel = wx.StaticText(self, size=(75,-1))
        self.currentRaLabel.SetLabel('RA: ')
        self.currentRaPos = wx.StaticText(self,size=(100,-1))
        self.currentRaPos.SetLabel('Unknown')
        self.currentRaPos.SetForegroundColour((255,0,0))

        self.currentDecLabel = wx.StaticText(self, size=(75,-1))
        self.currentDecLabel.SetLabel('DEC: ')
        self.currentDecPos = wx.StaticText(self,size=(100,-1))
        self.currentDecPos.SetLabel('Unknown')
        self.currentDecPos.SetForegroundColour((255,0,0))

        self.currentEpochLabel = wx.StaticText(self, size=(75,-1))
        self.currentEpochLabel.SetLabel('EPOCH: ')
        self.currentEpochPos = wx.StaticText(self,size=(75,-1))
        self.currentEpochPos.SetLabel('Unknown')
        self.currentEpochPos.SetForegroundColour((255,0,0))

        self.currentUTCLabel = wx.StaticText(self, size=(75,-1))
        self.currentUTCLabel.SetLabel('UTC: ')
        self.currentUTCPos = wx.StaticText(self,size=(75,-1))
        self.currentUTCPos.SetLabel('Unknown')
        self.currentUTCPos.SetForegroundColour((255,0,0))

        self.currentLSTLabel = wx.StaticText(self, size=(75,-1))
        self.currentLSTLabel.SetLabel('LST: ')
        self.currentLSTPos = wx.StaticText(self,size=(75,-1))
        self.currentLSTPos.SetLabel('Unknown')
        self.currentLSTPos.SetForegroundColour((255,0,0))

        self.currentLocalLabel = wx.StaticText(self, size=(75,-1))
        self.currentLocalLabel.SetLabel('Local: ')
        self.currentLocalPos = wx.StaticText(self,size=(75,-1))
        self.currentLocalPos.SetLabel('Unknown')
        self.currentLocalPos.SetForegroundColour((255,0,0))

        self.currentJDLabel = wx.StaticText(self, size=(75,-1))
        self.currentJDLabel.SetLabel('MJD: ')
        self.currentJDPos = wx.StaticText(self,size=(75,-1))
        self.currentJDPos.SetLabel('Unknown')
        self.currentJDPos.SetForegroundColour((255,0,0))


        self.currentFocusLabel = wx.StaticText(self, size=(75,-1))
        self.currentFocusLabel.SetLabel('Focus: ')
        self.currentFocusPos = wx.StaticText(self,size=(75,-1))
        self.currentFocusPos.SetLabel('Unknown')
        self.currentFocusPos.SetForegroundColour((255,0,0))

        self.currentRATRLabel = wx.StaticText(self, size=(125,-1))
        self.currentRATRLabel.SetLabel('RA Tracking Rate: ')
        self.currentRATRPos = wx.StaticText(self,size=(75,-1))
        self.currentRATRPos.SetLabel('Unknown')
        self.currentRATRPos.SetForegroundColour((255,0,0))
        
        self.currentDECTRLabel = wx.StaticText(self, size=(125,-1))
        self.currentDECTRLabel.SetLabel('DEC Tracking Rate: ')
        self.currentDECTRPos = wx.StaticText(self,size=(75,-1))
        self.currentDECTRPos.SetLabel('Unknown')
        self.currentDECTRPos.SetForegroundColour((255,0,0))


        #Focus Change
        self.focusIncPlusButton = wx.Button(self, -1, 'Increment Positive')
        self.focusIncNegButton = wx.Button(self, -1, 'Increment Negative')
        self.focusAbsText = wx.TextCtrl(self,size=(75,-1))
        self.focusAbsText.SetLabel('1500')
        self.focusAbsMove = wx.Button(self,-1,'Move Absolute')


        self.slewButton = wx.Button(self, -1, "Slew to Target")
        self.slewButton.Disable()
        self.trackButton = wx.Button(self, -1, "Start Tracking")
        self.trackButton.Disable()

        self.stopButton = wx.Button(self, -1, "HALT MOTION")
        # self.stopButton.Bind(wx.EVT_ENTER_WINDOW, self.onMouseOver)

        #need to reposition these, they're all on top of each other in the
        #top left
        self.jogNButton = wx.Button(self, -1, 'N', pos = (650, 175))
        self.jogSButton = wx.Button(self, -1, 'S', pos = (650, 225))
        self.jogWButton = wx.Button(self, -1, 'W', pos = (600, 200))
        self.jogEButton = wx.Button(self, -1, 'E', pos = (700, 200))
        #self.jogIncrement = wx.TextCtrl(self,size=(20,-1), pos = )


        #setup sizers
        self.vbox=wx.BoxSizer(wx.VERTICAL)
        self.vbox1=wx.BoxSizer(wx.VERTICAL)
        self.hbox1=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2=wx.BoxSizer(wx.HORIZONTAL)
        self.gbox=wx.GridSizer(rows=5, cols=2, hgap=5, vgap=5)
        self.gbox2=wx.GridSizer(rows=11, cols=2, hgap=5, vgap=5)
        self.gbox3=wx.GridSizer(rows=2, cols=2, hgap=5, vgap=5)

        self.gbox.Add(self.targetNameLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.targetNameText, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.targetRaLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.targetRaText, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.targetDecLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.targetDecText, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.targetEpochLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.targetEpochText, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.targetMagLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.targetMagText, 0, wx.ALIGN_RIGHT)

        self.vbox1.Add(self.gbox,0,wx.ALIGN_CENTER)



        self.gbox2.Add(self.currentNameLabel, 0, wx.ALIGN_RIGHT)
        self.gbox2.Add(self.currentNamePos, 0, wx.ALIGN_LEFT)
        self.gbox2.Add(self.currentRaLabel, 0, wx.ALIGN_RIGHT)
        self.gbox2.Add(self.currentRaPos, 0, wx.ALIGN_LEFT)
        self.gbox2.Add(self.currentDecLabel, 0, wx.ALIGN_RIGHT)
        self.gbox2.Add(self.currentDecPos, 0, wx.ALIGN_LEFT)
        self.gbox2.Add(self.currentEpochLabel, 0, wx.ALIGN_RIGHT)
        self.gbox2.Add(self.currentEpochPos, 0, wx.ALIGN_LEFT)
        self.gbox2.Add(self.currentJDLabel, 0, wx.ALIGN_RIGHT)
        self.gbox2.Add(self.currentJDPos, 0, wx.ALIGN_LEFT)
        self.gbox2.Add(self.currentUTCLabel, 0, wx.ALIGN_RIGHT)
        self.gbox2.Add(self.currentUTCPos, 0, wx.ALIGN_LEFT)
        self.gbox2.Add(self.currentLocalLabel, 0, wx.ALIGN_RIGHT)
        self.gbox2.Add(self.currentLocalPos, 0, wx.ALIGN_LEFT)
        self.gbox2.Add(self.currentLSTLabel, 0, wx.ALIGN_RIGHT)
        self.gbox2.Add(self.currentLSTPos, 0, wx.ALIGN_LEFT)
        self.gbox2.Add(self.currentFocusLabel, 0, wx.ALIGN_RIGHT)
        self.gbox2.Add(self.currentFocusPos, 0, wx.ALIGN_LEFT)
        self.gbox2.Add(self.currentRATRLabel, 0, wx.ALIGN_RIGHT)
        self.gbox2.Add(self.currentRATRPos, 0, wx.ALIGN_LEFT)
        self.gbox2.Add(self.currentDECTRLabel, 0, wx.ALIGN_RIGHT)
        self.gbox2.Add(self.currentDECTRPos, 0, wx.ALIGN_LEFT)

        self.gbox3.Add(self.focusIncPlusButton, 0, wx.ALIGN_LEFT)
        self.gbox3.Add(self.focusAbsText, 0, wx.ALIGN_LEFT)
        self.gbox3.Add(self.focusIncNegButton, 0, wx.ALIGN_LEFT)
        self.gbox3.Add(self.focusAbsMove, 0, wx.ALIGN_LEFT)

        self.hbox1.Add(self.gbox2, 0, wx.ALIGN_CENTER)
        self.hbox1.AddSpacer(25)
        self.hbox1.Add(self.vbox1, 0, wx.ALIGN_CENTER)
        self.hbox1.AddSpacer(25)
        self.hbox1.Add(self.gbox3, 0, wx.ALIGN_CENTER)

        self.hbox2.Add(self.slewButton, 0, wx.ALIGN_CENTER)
        self.hbox2.AddSpacer(25)
        self.hbox2.Add(self.trackButton, 0, wx.ALIGN_CENTER)

        self.vbox.Add(self.hbox1,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.hbox2,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.stopButton,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.logBox,0,wx.ALIGN_CENTER)

        self.SetSizer(self.vbox)

    #def onMouseOver(self, event):
            # mouseover changes colour of button
            #self.info.SetLabel("Stops all motion of the telescope (slewing and tracking).")
            #event.Skip()
    
class Target(wx.Panel):
    def __init__(self,parent, debug, night):
        wx.Panel.__init__(self,parent)

        #setup the test and retrieval button for getting target list
        self.fileLabel=wx.StaticText(self, size=(125,-1))
        self.fileLabel.SetLabel('Target List Path: ')
        self.fileText=wx.TextCtrl(self,size=(400,-1))

        self.listButton = wx.Button(self, -1, "Retrieve List")

        #show list of targets with selection button.  When the target is highlighted the selection button will input the data into the Control window.
        self.targetList=wx.ListCtrl(self,size=(525,200), style=wx.LC_REPORT | wx.VSCROLL)
        self.targetList.InsertColumn(0,'Target Name',width=125)
        self.targetList.InsertColumn(1,'RA',width=100)
        self.targetList.InsertColumn(2,'DEC',width=100)
        self.targetList.InsertColumn(3,'EPOCH',width=62.5)
        self.targetList.InsertColumn(5,'V Mag',width=62.5)
        self.targetList.InsertColumn(6,'Airmass',width=75)
        

        #Input individual target, use astropy and a lot of error checking to solve format failures
        self.nameLabel=wx.StaticText(self, size=(50,-1))
        self.nameLabel.SetLabel('Name: ')
        self.nameText=wx.TextCtrl(self,size=(100,-1))

        self.raLabel=wx.StaticText(self, size=(50,-1))
        self.raLabel.SetLabel('RA: ')
        self.raText=wx.TextCtrl(self,size=(100,-1))

        self.decLabel=wx.StaticText(self, size=(50,-1))
        self.decLabel.SetLabel('DEC: ')
        self.decText=wx.TextCtrl(self,size=(100,-1))

        self.epochLabel=wx.StaticText(self, size=(75,-1))
        self.epochLabel.SetLabel('EPOCH: ')
        self.epochText=wx.TextCtrl(self,size=(100,-1))

        self.magLabel=wx.StaticText(self, size=(75,-1))
        self.magLabel.SetLabel('V Mag: ')
        self.magText=wx.TextCtrl(self,size=(100,-1))
        
        #Buttons
        self.selectButton = wx.Button(self, -1, "Select as Current Target")
        self.enterButton = wx.Button(self, -1, "Add Item to List")
        self.plot_button=wx.Button(self,-1,'Plot Target')
        self.airmass_button=wx.Button(self,-1,"Airmass Curve")

        #setup sizers
        self.vbox=wx.BoxSizer(wx.VERTICAL)
        self.hbox1=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3=wx.BoxSizer(wx.HORIZONTAL)
        self.gbox=wx.GridSizer(rows=5, cols=2, hgap=5, vgap=5)

        self.hbox1.Add(self.fileLabel,0,wx.ALIGN_CENTER)
        self.hbox1.Add(self.fileText,0, wx.ALIGN_CENTER)
        self.hbox1.Add(self.listButton,0, wx.ALIGN_CENTER)


        self.gbox.Add(self.nameLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.nameText, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.raLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.raText, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.decLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.decText, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.epochLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.epochText, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.magLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.magText, 0, wx.ALIGN_RIGHT)

        self.hbox2.Add(self.targetList,0, wx.ALIGN_CENTER)
        self.hbox2.Add(self.gbox,0,wx.ALIGN_CENTER)

        self.hbox3.Add(self.selectButton,0, wx.ALIGN_CENTER)
        self.hbox3.AddSpacer(50)
        self.hbox3.Add(self.enterButton,0, wx.ALIGN_CENTER)
        self.hbox3.AddSpacer(50)
        self.hbox3.Add(self.plot_button,0,wx.ALIGN_CENTER)
        self.hbox3.AddSpacer(50)
        self.hbox3.Add(self.airmass_button,0,wx.ALIGN_CENTER)

        self.vbox.Add(self.hbox1,0, wx.ALIGN_CENTER,5)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.hbox2,0, wx.ALIGN_CENTER,5)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.hbox3,0, wx.ALIGN_CENTER,5)

        self.SetSizer(self.vbox)
        self.vbox.Fit(self)

        debug==True
        self.dir=os.getcwd()


'''
class Image(wx.Panel):
    def __init__(self,parent, debug, night):
        wx.Panel.__init__(self,parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.frame = parent
        
        self.fig = Figure((4,4))
        self.canvas = FigCanvas(self,-1, self.fig)
        self.ax1 = self.fig.add_subplot(111)
        self.ax1.set_axis_off()
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        
    def OnEraseBackground(self, evt):
        """
        Add a picture to the background
        """
        # yanked from ColourDB.py
        dc = evt.GetDC()
 
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        bmp = wx.Bitmap("testfinder.jpg")
        dc.DrawBitmap(bmp, 0, 0)
'''        
class ScienceFocus(wx.Panel):
    def __init__(self,parent, debug, night):
        wx.Panel.__init__(self,parent)
        None
'''
        self.currentFocusLabel = wx.StaticText(self, size=(75,-1))
        self.currentFocusLabel.SetLabel('Focus: ')
        self.currentFocusPos = wx.StaticText(self,size=(75,-1))
        self.currentFocusPos.SetLabel('Unknown')
        self.currentFocusPos.SetForegroundColour((255,0,0))

#Focus Change
        self.focusIncPlusButton = wx.Button(self, -1, 'Increment Positive')
        self.focusIncNegButton = wx.Button(self, -1, 'Increment Negative')
        self.focusAbsText = wx.TextCtrl(self,size=(75,-1))
        self.focusAbsText.SetLabel('1500')
        self.focusAbsMove = wx.Button(self,-1,'Move Absolute')


        self.slewButton = wx.Button(self, -1, "Slew to Target")
        #self.slewButton.Disable()
        self.trackButton = wx.Button(self, -1, "Start Tracking")
        #self.trackButton.Disable()
'''
class Guider(wx.Panel):
    def __init__(self,parent, debug, night):
        wx.Panel.__init__(self,parent)

        #self.guiderTZLabel=wx.StaticText(self, size=(75,-1))
        #self.guiderTZLabel.SetLabel('Time Zone: ')
        #time_options=['Pacific','UTC']
        #self.guiderTZCombo=wx.ComboBox(self,size=(50,-1), choices=time_options, style=wx.CB_READONLY)

        #self.header=wx.StaticText(self,-1,"Guider Performance")
        #Add current offset and timing information only.
        self.dpi = 100
        self.fig = Figure((7.0,4.5), dpi=self.dpi)
        self.canvas = FigCanvas(self,-1, self.fig)

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
        #self.hbox=wx.BoxSizer(wx.HORIZONTAL)
        #self.hbox.Add(self.guiderTZLabel,0)
        #self.hbox.Add(self.guiderTZCombo,0)
        #self.vbox.Add(self.hbox,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.canvas, 0, wx.ALIGN_CENTER)
        self.vbox.Add(self.toolbar,0, wx.ALIGN_CENTER)

        self.SetSizer(self.vbox)
        self.vbox.Fit(self)

class GuiderControl(wx.Panel):
    def __init__(self,parent, debug, night):
        wx.Panel.__init__(self,parent)

        # add visual representation of stepper and periscope position
        # show computation for decovultion of position
        # image display w/ vector offset arrows
        # need to define guider directory and filename structure

        self.Buffer = None
        self.center=[200,275]
        self.dc = None
        self.rotAng=0

        self.Bind(wx.EVT_PAINT, self.OnPaint)

        #thread.start_new_thread(self.rotPaint,())
        self.current_target=None

        img=wx.EmptyImage(320,320)
        self.imageCtrl = wx.StaticBitmap(self,wx.ID_ANY,wx.BitmapFromImage(img))
        '''
        self.fig = Figure((4,4))
        self.canvas = FigCanvas(self,-1, self.fig)
        self.ax1 = self.fig.add_subplot(111)
        self.ax1.set_axis_off()
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)
        '''
        self.finderButton=wx.Button(self,-1,"Load Finder Chart")
        #self.finderButton.Bind(wx.EVT_BUTTON,self.load_finder_chart)
        
        self.findStarsButton = wx.Button(self, -1, "Auto Find Guide Stars")
        self.startGuidingButton = wx.Button(self, -1, "Start Guiding")

        self.guiderTimeLabel=wx.StaticText(self, size=(75,-1))
        self.guiderTimeLabel.SetLabel('Exposure: ')
        self.guiderTimeText=wx.TextCtrl(self,size=(50,-1))
        self.guiderTimeText.SetValue('10')

        self.guiderBinningLabel=wx.StaticText(self, size=(75,-1))
        self.guiderBinningLabel.SetLabel('Binning: ')
        binning_options=['1','2','3']
        self.guiderBinningCombo=wx.ComboBox(self,size=(50,-1), choices=binning_options, style=wx.CB_READONLY)

        self.guiderExposureButton = wx.Button(self, -1, 'Guider Exposure')

        self.guiderRotLabel=wx.StaticText(self, size=(150,-1))
        self.guiderRotLabel.SetLabel('Guider Rotation Angle: ')
        self.guiderRotText=wx.TextCtrl(self,size=(50,-1))
        self.guiderRotText.SetValue('0.0')
        self.guiderRotButton = wx.Button(self, -1, 'Set Guider Rotation')
        self.Bind(wx.EVT_BUTTON, self.goToRot, self.guiderRotButton)

        self.vbox=wx.BoxSizer(wx.VERTICAL)
        self.hbox=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3=wx.BoxSizer(wx.HORIZONTAL)
        self.gbox=wx.GridSizer(rows=2, cols=2, hgap=5, vgap=5)

        self.gbox.Add(self.guiderTimeLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.guiderTimeText, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.guiderBinningLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.guiderBinningCombo, 0, wx.ALIGN_RIGHT)

        self.hbox.Add(self.finderButton,0,wx.ALIGN_RIGHT)
        self.hbox.Add(self.findStarsButton, 0, wx.ALIGN_RIGHT)
        self.hbox.Add(self.startGuidingButton, 0, wx.ALIGN_RIGHT)
        self.hbox.Add(self.guiderExposureButton, 0, wx.ALIGN_RIGHT)

        #self.hbox2.Add(self.panel2,0,wx.ALIGN_RIGHT)
        #self.hbox2.Add(self.canvas,0,wx.ALIGN_RIGHT)
        #self.hbox2.AddSpacer(133)
        self.hbox2.AddSpacer(350)
        self.hbox2.Add(self.imageCtrl,0,wx.ALIGN_RIGHT)

        self.hbox3.Add(self.guiderRotLabel,0,wx.ALIGN_CENTER)
        self.hbox2.AddSpacer(10)
        self.hbox3.Add(self.guiderRotText,0,wx.ALIGN_CENTER)
        self.hbox2.AddSpacer(10)
        self.hbox3.Add(self.guiderRotButton,0,wx.ALIGN_CENTER)

        self.vbox.AddSpacer(10)
        self.vbox.Add(self.gbox,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.hbox,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.hbox2,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.hbox3,0,wx.ALIGN_CENTER)


        self.SetSizer(self.vbox)

    '''Load the finder chart for the current target
    def load_finder_chart(self,event):
        
        self.finder_chart=plot_finder_image(self.current_target, fov_radius=2*u.degree,ax=self.ax1)
        self.ax1.set_axis_off()
        return
    '''

    def InitBuffer(self):
        size=self.GetClientSize()
        # if buffer exists and size hasn't changed do nothing
        if self.Buffer is not None and self.Buffer.GetWidth() == size.width and self.Buffer.GetHeight() == size.height:
            return False

        self.Buffer=wx.EmptyBitmap(size.width,size.height)
        self.dc=wx.MemoryDC()

        self.dc.SelectObject(self.Buffer)
        self.dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        self.dc.Clear()
        self.drawCircle(self.center, 175)
        self.dc.SelectObject(wx.NullBitmap)
        return True

    def drawCircle(self, center, diameter):
        size=self.GetClientSize()
        pen=wx.Pen('blue',1)
        self.dc.SetPen(pen)
        self.dc.DrawCircle(center[0],center[1],diameter)

    def drawPeriscope(self):
        size=self.GetClientSize()

        #draw a reference line
        pen=wx.Pen('black',1)
        self.dc.SetPen(pen)
        radius = 175
        ang = self.rotAng*(math.pi/180.0)
        centerLine=[self.center[0]-radius*math.sin(float(ang)), self.center[1]-radius*math.cos(float(ang))]
        print centerLine, ang
        self.dc.DrawLine(self.center[0],self.center[1],centerLine[0], centerLine[1])
        #draw for lines that are a box with perpendicular sides
        pen=wx.Pen('red',1)
        self.dc.SetPen(pen)
        #start with 0 deg up, left line
        startLeft=[self.center[0]-10,self.center[1]]
        endLeft = [startLeft[0], startLeft[1]-100]
        self.dc.DrawLine(startLeft[0],startLeft[1],endLeft[0], endLeft[1])
        #bottom line
        endBottom = [startLeft[0] + 20,startLeft[1]]
        self.dc.DrawLine(startLeft[0],startLeft[1],endBottom[0], endBottom[1])
        #right line
        endRight = [endBottom[0], endBottom[1]-100]
        self.dc.DrawLine(endBottom[0],endBottom[1],endRight[0], endRight[1])
        #top line
        self.dc.DrawLine(endRight[0],endRight[1],endLeft[0],endLeft[1])


    def OnPaint(self, event):
        
        self.InitBuffer()
        self.dc = wx.PaintDC(self)
        self.dc.DrawBitmap(self.Buffer, 0, 0)
        self.drawPeriscope()

    def goToRot(self,ang):
        thread.start_new_thread(self.toRot,())

    def toRot(self):
        #compute move, should be a count down to the desired angle
        move = float(self.guiderRotText.GetValue()) - self.rotAng
        print 'moving: '+ str(move)
        for m in range(int(math.fabs(move))):
            if float(self.guiderRotText.GetValue())>=0:
                self.rotAng = self.rotAng + 1
            else:
                self.rotAng = self.rotAng - 1
            print self.rotAng, m
            self.Refresh()
            time.sleep(0.05)

class GuiderFocus(wx.Panel):
    def __init__(self,parent, debug, night):
        wx.Panel.__init__(self,parent)
        None



class Initialization(wx.Panel):
    def __init__(self,parent, debug, night):
        wx.Panel.__init__(self,parent)

        # add line to separate the different sections

        self.atZenithButton = wx.Button(self, -1, "Load Zenith Coordinates")
        self.atZenithButton.Disable()
        


        #self.zenith = wx.PopupWindow("um r u sure")

        #Set current telescope position
        self.targetNameLabel=wx.StaticText(self, size=(75,-1))
        self.targetNameLabel.SetLabel('Name: ')
        self.targetNameText=wx.TextCtrl(self,size=(100,-1))

        self.targetRaLabel=wx.StaticText(self, size=(75,-1))
        self.targetRaLabel.SetLabel('RA: ')
        self.targetRaText=wx.TextCtrl(self,size=(100,-1))

        self.targetDecLabel=wx.StaticText(self, size=(75,-1))
        self.targetDecLabel.SetLabel('DEC: ')
        self.targetDecText=wx.TextCtrl(self,size=(100,-1))

        self.targetEpochLabel=wx.StaticText(self, size=(75,-1))
        self.targetEpochLabel.SetLabel('EPOCH: ')
        self.targetEpochText=wx.TextCtrl(self,size=(100,-1))
        self.targetEpochText.SetLabel('2000')

        #Precessed Coordinates
        self.precessNameText=wx.StaticText(self,size=(100,-1))
        self.precessNameText.SetLabel('None')
        self.precessRaText=wx.StaticText(self,size=(100,-1))
        self.precessRaText.SetLabel('None')
        self.precessDecText=wx.StaticText(self,size=(100,-1))
        self.precessDecText.SetLabel('None')
        self.precessEpochText=wx.StaticText(self,size=(100,-1))
        self.precessEpochText.SetLabel('None')

        # this should autofill from tcc.conf
        self.trackingRateRALabel=wx.StaticText(self, size=(100,-1))
        self.trackingRateRALabel.SetLabel('RA Tracking Rate: ')
        self.trackingRateRAText=wx.TextCtrl(self,size=(100,-1))
        self.rateRAButton = wx.Button(self, -1, "Set RA Tracking Rate")

        self.trackingRateDECLabel=wx.StaticText(self, size=(100,-1))
        self.trackingRateDECLabel.SetLabel('DEC Tracking Rate: ')
        self.trackingRateDECText=wx.TextCtrl(self,size=(100,-1))
        self.rateDECButton = wx.Button(self, -1, "Set DEC Tracking Rate")

        #allows for change in maximum guider offsets, should be set by tcc.conf as an initial value
        self.maxdRALabel=wx.StaticText(self, size=(75,-1))
        self.maxdRALabel.SetLabel('Max dRA: ')
        self.maxdRAText=wx.TextCtrl(self,size=(100,-1))
        self.dRAButton = wx.Button(self, -1, "Set Maximum dRA")

        self.maxdDECLabel=wx.StaticText(self, size=(75,-1))
        self.maxdDECLabel.SetLabel('Max dDEC: ')
        self.maxdDECText=wx.TextCtrl(self,size=(100,-1))
        self.dDECButton = wx.Button(self, -1, "Set Maximum dDEC")


        self.syncButton = wx.Button(self, -1, "Set Telescope Position")
        self.initButton = wx.Button(self, -1, "Initialize Telescope Systems")

        self.vbox=wx.BoxSizer(wx.VERTICAL)
        self.hbox1=wx.BoxSizer(wx.HORIZONTAL)
        self.gbox=wx.GridSizer(rows=4, cols=3, hgap=5, vgap=5)
        self.gbox2=wx.GridSizer(rows=5, cols=3, hgap=5, vgap=5)

        self.gbox.Add(self.targetNameLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.targetNameText, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.precessNameText, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.targetRaLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.targetRaText, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.precessRaText, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.targetDecLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.targetDecText, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.precessDecText, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.targetEpochLabel, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.targetEpochText, 0, wx.ALIGN_RIGHT)
        self.gbox.Add(self.precessEpochText, 0, wx.ALIGN_RIGHT)

        self.gbox2.Add(self.trackingRateRALabel, 0, wx.ALIGN_RIGHT)
        self.gbox2.Add(self.trackingRateRAText, 0, wx.ALIGN_LEFT)
        self.gbox2.Add(self.rateRAButton, 0, wx.ALIGN_LEFT)
        self.gbox2.Add(self.trackingRateDECLabel, 0, wx.ALIGN_RIGHT)
        self.gbox2.Add(self.trackingRateDECText, 0, wx.ALIGN_LEFT)
        self.gbox2.Add(self.rateDECButton,0,wx.ALIGN_LEFT)
        self.gbox2.Add(self.maxdRALabel, 0, wx.ALIGN_RIGHT)
        self.gbox2.Add(self.maxdRAText, 0, wx.ALIGN_LEFT)
        self.gbox2.Add(self.dRAButton, 0, wx.ALIGN_LEFT)
        self.gbox2.Add(self.maxdDECLabel, 0, wx.ALIGN_RIGHT)
        self.gbox2.Add(self.maxdDECText, 0, wx.ALIGN_LEFT)
        self.gbox2.Add(self.dDECButton, 0, wx.ALIGN_LEFT)


        self.hbox1.Add(self.atZenithButton,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(10)
        self.hbox1.Add(self.initButton,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(10)
        self.hbox1.Add(self.syncButton, 0, wx.ALIGN_RIGHT)

        self.vbox.AddSpacer(10)
        self.vbox.Add(self.hbox1,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.gbox,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.gbox2,0,wx.ALIGN_CENTER)

        self.SetSizer(self.vbox)


class NightLog(wx.ScrolledWindow):
    def __init__(self,parent, debug, night):
        self.parent = parent
        wx.ScrolledWindow.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)
        fontsz = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT).GetPixelSize()
        self.SetScrollRate(fontsz.x, fontsz.y)
        self.EnableScrolling(True,True)

        self.nltitle=wx.StaticText(self,-1, "Manastash Ridge Observatory Night Log")
        font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.nltitle.SetFont(font)
        self.labelastr=wx.StaticText(self, -1, "Astronomer(s)")
        self.labelobs=wx.StaticText(self, -1, "Observer(s)")
        self.labelinst=wx.StaticText(self, -1, "Instrument")
        self.labelstart=wx.StaticText(self, -1, "Start Time")
        self.labelend=wx.StaticText(self, -1, "End Time")
        self.usastr=wx.TextCtrl(self,size=(50,-1))
        self.usobs=wx.TextCtrl(self, size=(50,-1))
        self.usinst=wx.TextCtrl(self,size=(50,-1))
        self.usstart=wx.TextCtrl(self,size=(50,-1))
        self.usend=wx.TextCtrl(self,size=(50,-1))

        #First box components for observer and astronomer identification

        self.hbox1=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(self.labelastr,0,wx.ALIGN_RIGHT)
        self.hbox1.AddSpacer(5)
        self.hbox1.Add(self.usastr,1,wx.ALIGN_LEFT|wx.EXPAND)
        self.hbox1.AddSpacer(10)

        self.hbox2=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.labelobs,0,wx.ALIGN_RIGHT)
        self.hbox2.AddSpacer(21)
        self.hbox2.Add(self.usobs,1,wx.ALIGN_LEFT|wx.EXPAND)
        self.hbox2.AddSpacer(10)

        self.hbox3=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3.Add(self.labelinst,0,wx.ALIGN_RIGHT)
        self.hbox3.AddSpacer(23)
        self.hbox3.Add(self.usinst,1,wx.ALIGN_LEFT|wx.EXPAND)
        self.hbox3.AddSpacer(10)

        self.hbox4=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4.Add(self.labelstart,0,wx.ALIGN_RIGHT)
        self.hbox4.AddSpacer(27)
        self.hbox4.Add(self.usstart,1,wx.ALIGN_LEFT|wx.EXPAND)
        self.hbox4.AddSpacer(10)

        self.hbox5=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox5.Add(self.labelend,0,wx.ALIGN_RIGHT)
        self.hbox5.AddSpacer(31)
        self.hbox5.Add(self.usend,1,wx.ALIGN_LEFT|wx.EXPAND)
        self.hbox5.AddSpacer(10)


        #Activity Log
        self.actheader=wx.StaticText(self,label="ACTIVITY LOG")
        self.actlog=wx.TextCtrl(self, size=(600,100),style= wx.TE_MULTILINE)

        #Failure Log
        self.failheader=wx.StaticText(self,label="FAILURE LOG")
        #self.failinfo=wx.StaticText(self,label="Time                                                                          Description                                                                                    ")
        self.faillog=wx.TextCtrl(self, size=(600,50),style= wx.TE_MULTILINE)

        #Focus Log
        self.focheader=wx.StaticText(self,label="FOCUS LOG")
        #self.focinfo=wx.StaticText(self,label='Time               Instrument               Focus                 Az      El      Temp    Strc    Prim     Sec     Air     filt     FWHM')
        #self.foclog=wx.TextCtrl(self, size=(600,100),style= wx.TE_MULTILINE)
        self.foclog=wx.ListCtrl(self,size=(600,100), style=wx.LC_REPORT| wx.VSCROLL | wx.LC_VRULES)
        self.foclog.InsertColumn(0,'Time',width=50)
        self.foclog.InsertColumn(1,'Instrument',width=75)
        self.foclog.InsertColumn(2,'Focus',width=75)
        self.foclog.InsertColumn(3,'Az',width=50)
        self.foclog.InsertColumn(5,'El',width=50)
        self.foclog.InsertColumn(6,'Temp',width=50)
        self.foclog.InsertColumn(7,'Strc',width=50)
        self.foclog.InsertColumn(8,'Prim',width=50)
        self.foclog.InsertColumn(9,'Sec',width=50)
        self.foclog.InsertColumn(10,'Air',width=50)
        self.foclog.InsertColumn(11,'filt',width=50)
        self.foclog.InsertColumn(12,'FWHM',width=50)

        self.focusButton=wx.Button(self,label="Number of Focus Lines")
       # self.Bind(wx.EVT_BUTTON,self.getFocus,self.focusButton)
        self.focusNum=wx.TextCtrl(self,size=(30,-1))
        self.focusNum.AppendText('1')

        self.hbox6=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox6.Add(self.focusButton,0,wx.ALIGN_CENTER)
        self.hbox6.AddSpacer(5)
        self.hbox6.Add(self.focusNum,0,wx.ALIGN_CENTER)

        #Save as and Submit buttons
        self.saveButton=wx.Button(self,label="Save As")

        self.submitButton=wx.Button(self,label="Submit")

        self.hbox7=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox7.Add(self.saveButton,0,wx.ALIGN_CENTER)
        self.hbox7.AddSpacer(25)
        self.hbox7.Add(self.submitButton,0,wx.ALIGN_CENTER)


        #Vertical box organization
        self.vbox=wx.BoxSizer(wx.VERTICAL)

        self.vbox.Add(self.nltitle, 0, wx.ALIGN_CENTER)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.hbox1,0,wx.ALIGN_LEFT|wx.EXPAND)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.hbox2,0,wx.ALIGN_LEFT|wx.EXPAND)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.hbox3,0,wx.ALIGN_LEFT|wx.EXPAND)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.hbox4,0,wx.ALIGN_LEFT|wx.EXPAND)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.hbox5,0,wx.ALIGN_LEFT|wx.EXPAND)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.actheader,0,wx.ALIGN_CENTER)
        self.vbox.Add(self.actlog,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.failheader, 0, wx.ALIGN_CENTER)
        self.vbox.AddSpacer(5)
        #self.vbox.Add(self.failinfo,0,wx.ALIGN_CENTER)
        self.vbox.Add(self.faillog,0, wx.ALIGN_CENTER)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.focheader,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(5)
        #self.vbox.Add(self.focinfo,0,wx.ALIGN_CENTER)
        self.vbox.Add(self.foclog,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(5)
        self.vbox.Add(self.hbox6,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(25)
        self.vbox.Add(self.hbox7,0,wx.ALIGN_CENTER)


        self.SetSizer(self.vbox)
        self.Show()

class TCC(wx.Frame):
    title='Manastash Ridge Observatory Telescope Control Computer'
    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title,size=(900,600))
        
        #Tracking on boot is false
        self.tracking=False
        self.slewing=False
        self.night=True
        self.initState=False
        self.dict={'lat':None, 'lon':None,'elevation':None, 'lastRA':None, 'lastDEC':None,'lastGuiderRot':None,'lastFocusPos':None,'maxdRA':None,'maxdDEC':None, 'trackingRate':None }
        self.list_count=0
        #Stores current time zone for whole GUI
        self.current_timezone=Time.now()
        self.mro=ephem.Observer()
        
        self.MRO = Observer(longitude = -120.7278 *u.deg,
                latitude = 46.9528*u.deg,
                elevation = 1198*u.m,
                name = "Manastash Ridge Observatory"
                )
        debug=True
        

        self.dir=os.getcwd()
        
        #setup notebook
        p=wx.Panel(self)
        nb=wx.Notebook(p)
        controlPage=Control(nb, debug, self.night)
        targetPage=Target(nb, debug, self.night)
        #imagePage=Image(nb,debug,self.night)
        scienceFocusPage=ScienceFocus(nb, debug, self.night)
        guiderPage=Guider(nb, debug, self.night)
        guiderControlPage=GuiderControl(nb,debug,self.night)
        guiderFocusPage=GuiderFocus(nb,debug,self.night)
        initPage=Initialization(nb, debug, self.night)
        logPage=NightLog(nb, debug, self.night)

        nb.AddPage(controlPage,"Telescope Control")
        self.control=nb.GetPage(0)

        nb.AddPage(scienceFocusPage, "Science Focus")
        self.scienceFocus=nb.GetPage(1)

        nb.AddPage(targetPage,"Target List")
        self.target=nb.GetPage(2)
        
        #nb.AddPage(imagePage,"Image")
       # self.image=nb.GetPage(3)

        nb.AddPage(guiderControlPage,"Guider Control")
        self.guiderControl=nb.GetPage(3)

        nb.AddPage(guiderFocusPage, "Guider Focus")
        self.guiderFocus=nb.GetPage(4)

        nb.AddPage(guiderPage,"Guider Performance Monitor")
        self.guider=nb.GetPage(5)

        nb.AddPage(initPage,"Initialization Parameters")
        self.init=nb.GetPage(6)

        nb.AddPage(logPage,"Night Log")
        self.nl=nb.GetPage(7)

        self.Bind(wx.EVT_BUTTON, self.startSlew, self.control.slewButton)
        self.Bind(wx.EVT_BUTTON,self.toggletracksend,self.control.trackButton)
        self.Bind(wx.EVT_BUTTON,self.haltmotion,self.control.stopButton)
        self.Bind(wx.EVT_BUTTON,self.Noffset,self.control.jogNButton)
        self.Bind(wx.EVT_BUTTON,self.Soffset,self.control.jogSButton)
        self.Bind(wx.EVT_BUTTON,self.Eoffset,self.control.jogEButton)
        self.Bind(wx.EVT_BUTTON,self.Woffset,self.control.jogWButton)
        self.Bind(wx.EVT_BUTTON,self.focusIncPlus,self.control.focusIncPlusButton)
        self.Bind(wx.EVT_BUTTON,self.focusIncNeg,self.control.focusIncNegButton)
        self.Bind(wx.EVT_BUTTON,self.setfocus,self.control.focusAbsMove)
        
        self.Bind(wx.EVT_BUTTON, self.set_target, self.target.selectButton)
        self.Bind(wx.EVT_BUTTON, self.addToList, self.target.enterButton)
        self.Bind(wx.EVT_BUTTON, self.readToList, self.target.listButton)
        self.Bind(wx.EVT_BUTTON, self.target_plot, self.target.plot_button)
        self.Bind(wx.EVT_BUTTON, self.airmass_plot, self.target.airmass_button)
        

        self.Bind(wx.EVT_BUTTON,self.setTelescopeZenith ,self.init.atZenithButton)
        self.Bind(wx.EVT_BUTTON, self.setTelescopePosition, self.init.syncButton)
        self.Bind(wx.EVT_BUTTON, self.onInit, self.init.initButton)
        self.Bind(wx.EVT_BUTTON, self.setRATrackingRate,self.init.rateRAButton)
        self.Bind(wx.EVT_BUTTON, self.setDECTrackingRate,self.init.rateDECButton)
        
        self.createMenu()

        self.sb = self.CreateStatusBar(5)

        sizer=wx.BoxSizer()
        sizer.Add(nb,1, wx.EXPAND|wx.ALL)
        p.SetSizer(sizer)
        p.Layout()

        self.readConfig()
        """Target testing parameters """
        self.target.nameText.SetLabel('M31')
        self.target.raText.SetLabel('00h42m44.330s')
        self.target.decText.SetLabel('+41d16m07.50s')
        self.target.epochText.SetLabel('J2000')
        self.target.magText.SetLabel('3.43')

        #png image appears to cause an RGB conversion failure.  Either use jpg or convert with PIL
        img_default=os.path.join(self.dir,'gimg','gcam_56901_859.jpg')
        img = wx.Image(img_default, wx.BITMAP_TYPE_ANY)
        self.guiderControl.imageCtrl.SetBitmap(wx.BitmapFromImage(img))


    def createMenu(self):
        self.menubar = wx.MenuBar()

        menu_file = wx.Menu()
        m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)

        tool_file = wx.Menu()
        m_night = tool_file.Append(-1, 'Night\tCtrl-N','Night Mode')
        self.Bind(wx.EVT_MENU, self.on_night, m_night)

        self.tz_choice=wx.Menu()
        tz_UTC=self.tz_choice.Append(-1,'UTC')
        self.Bind(wx.EVT_MENU, self.on_UTC, tz_UTC)
        tz_P=self.tz_choice.Append(-1,'Pacific')
        self.Bind(wx.EVT_MENU, self.on_Pacific, tz_P)
        tool_file.AppendMenu(-1,'Time Zone',self.tz_choice)

        self.menubar.Append(menu_file, "&File")
        self.menubar.Append(tool_file, "&Tools")

        self.SetMenuBar(self.menubar)

    """Exit in a graceful way so that the telescope information can be saved and used at a later time"""
    def on_exit(self, event):
        dlg = wx.MessageDialog(self,
                               "Exit the TCC?",
                               "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            if(self.protocol is not None):
                d= self.protocol.sendCommand("shutdown")
                d.addCallback(self.quit)
    def quit(self):
        self.Destroy()
        reactor.stop()
            #add save coordinates
            #self.Destroy()

    def on_night(self,event):
        if self.night:
            self.SetBackgroundColour((176,23,23))
            self.night=False
        else:
            self.night=True
            color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BACKGROUND)
            self.SetBackgroundColour(color)
        return
    def on_UTC(self,event):
        self.current_timezone=Time.now()
        self.sb.SetStatusText('Timezone: UTC',4)
        return
    def on_Pacific(self,event):
        self.current_timezone=Time.now()-7*u.h
        self.sb.SetStatusText('Timezone: Pacific',4)
        return

    """Take input from the any system and log both on screen and to a file.
    Necessary to define command structure for easy expansion"""
    def log(self, input):
        today=time.strftime('%Y%m%d.log')
        current_time_log=time.strftime('%Y%m%dT%H%M%S')
        current_time=time.strftime('%Y%m%d  %H:%M:%S')
        f_out=open(self.dir+today,'a')
        f_out.write(current_time_log+','+str(input)+'\n')
        f_out.close()
        self.control.logBox.AppendText(str(current_time)+':  '+str(input)+'\n')
        return


    """Get the basic telescope information if it is available.  It would be nice if the dictionary was defined external to the program."""
    def readConfig(self):
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
        self.init.targetDecText.SetValue(str(self.dict['lat']))
        self.init.targetEpochText.SetValue(str( '%.3f') % t['epoch'])
        self.init.trackingRateRAText.SetValue(str(self.dict['trackingRate']))
        self.init.maxdRAText.SetValue(str(self.dict['maxdRA']))
        self.init.maxdDECText.SetValue(str(self.dict['maxdDEC']))
        return
        
    '''Jog Commands; apply a coordinate offset in the direction of preference'''
    def Noffset(self,event):
        self.protocol.sendCommand("offset 1 positive")
        return
    def Woffset(self,event):
        self.protocol.sendCommand("offset 0 negative")
        return
    def Eoffset(self,event):
        self.protocol.sendCommand("offset 0 positive")
        return
    def Soffset(self,event):
        self.protocol.sendCommand("offset 1 negative")
        return
        
    def focusIncPlus(self,event):
        val=self.control.focusAbsText.GetValue()
        val=float(val)+1500.0
        val=int(val)
        self.control.focusAbsText.SetValue(str(val))
        return
    def focusIncNeg(self,event):
        val=self.control.focusAbsText.GetValue()
        val=float(val)-1500.0
        val=int(val)
        self.control.focusAbsText.SetValue(str(val))
        return
        
    def setfocus(self,event):
        val=self.control.focusAbsText.GetValue()
        self.control.currentFocusPos.SetLabel(val)
        self.control.currentFocusPos.SetForegroundColour('black')
        self.protocol.sendCommand(str("focus")+' '+str(val))
        return
        
    '''Halt Telescope motion, emergency button, use stop slew during slewing if possible'''
    def haltmotion(self,event):
        self.protocol.sendCommand("halt")
        return
        
    '''Passes a command to the telescope to toggle tracking'''
    def toggletracksend(self,evt):
        #self.protocol.sendLine(str("toggletrack")+' '+str(self.tracking))
        self.protocol.sendCommand(str("toggletrack")+' '+str(self.tracking))
        if self.tracking==False:
            self.control.trackButton.SetLabel('Stop Tracking')
            self.sb.SetStatusText('Tracking: True',0)
        if self.tracking==True:
            self.control.trackButton.SetLabel('Start Tracking')
            self.sb.SetStatusText('Tracking: False',0)
        self.tracking= not self.tracking    
        return
    
    '''Take in any valid RA/DEC format and read it into a SkyCoord object'''    
    def inputcoordSorter(self,ra,dec,epoch_now,epoch):
        deg_input=True
        
        try:
            val=float(ra)
        except ValueError:
            deg_input=False
            
        self.validity=True
        
        if str(epoch)=='J2000':
    
            if deg_input==True:
                self.coordinates=SkyCoord(ra=float(ra)*u.degree,dec=float(dec)*u.degree,frame='icrs',equinox=str(epoch))
                self.coordinates=self.coordinates.transform_to(FK5(equinox='J'+epoch_now))
                return self.coordinates
            elif str(ra)[2]== 'h' and str(ra)[5]== 'm':
                self.coordinates=SkyCoord(ra,dec,frame='icrs',equinox=str(epoch))
                self.coordinates=self.coordinates.transform_to(FK5(equinox='J'+epoch_now))
                return self.coordinates
            elif str(ra)[2]== ' ' and str(ra)[5]== ' ':
                self.coordinates=SkyCoord(str(ra)+' '+str(dec), unit=(u.hourangle,u.deg),equinox=str(epoch))
                self.coordinates=self.coordinates.transform_to(FK5(equinox='J'+epoch_now))
                return self.coordinates
            elif str(ra)[2]== ':' and str(ra)[5]== ':':
                self.coordinates=SkyCoord(str(ra)+' '+str(dec), unit=(u.hourangle,u.deg),equinox=str(epoch))
                self.coordinates=self.coordinates.transform_to(FK5(equinox='J'+epoch_now))
                return self.coordinates
            else:
                self.validity=False
                dlg = wx.MessageDialog(self,
                               "Not a valid RA or DEC format. Please input an RA and DEC in any of the following forms: decimal degrees, 00h00m00s, 00:00:00, 00 00 00 ",
                               "Error", wx.OK|wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy() 
            return
        elif epoch=='J1950':
    
            if deg_input==True:
                self.coordinates=SkyCoord(ra=float(ra)*u.degree,dec=float(dec)*u.degree,frame='icrs',equinox=str(epoch))
                self.coordinates=self.coordinates.transform_to(FK4(equinox='J'+epoch_now))
                return self.coordinates
            elif str(ra)[2]== 'h' and str(ra)[5]== 'm':
                self.coordinates=SkyCoord(ra,dec,frame='icrs',equinox=str(epoch))
                self.coordinates=self.coordinates.transform_to(FK4(equinox='J'+epoch_now))
                return self.coordinates
            elif str(ra)[2]== ' ' and str(ra)[5]== ' ':
                self.coordinates=SkyCoord(str(ra)+' '+str(dec), unit=(u.hourangle,u.deg),equinox=str(epoch))
                self.coordinates=self.coordinates.transform_to(FK4(equinox='J'+epoch_now))
                return self.coordinates
            elif str(ra)[2]== ':' and str(ra)[5]== ':':
                self.coordinates=SkyCoord(str(ra)+' '+str(dec), unit=(u.hourangle,u.deg),equinox=str(epoch))
                self.coordinates=self.coordinates.transform_to(FK4(equinox='J'+epoch_now))
                return self.coordinates
            else:
                self.validity=False
                dlg = wx.MessageDialog(self,
                               "Not a valid RA or DEC format. Please input an RA and DEC in any of the following forms: decimal degrees, 00h00m00s, 00:00:00, 00 00 00 ",
                               "Error", wx.OK|wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy() 
            return
        else:
            self.validity=False
            dlg = wx.MessageDialog(self,
                               "Not a transformable input epoch. Coordinate types supported are J2000 and J1950. Leave epoch blank to assume J2000.",
                               "Error", wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy() 
            return
        
    
    '''Slew Command from coordinates in control tab, also acts as a toggle. If telescope is slewing, this will stop current slewing'''
    def startSlew(self,event):
        name=self.control.targetNameText.GetValue()
        input_ra=self.control.targetRaText.GetValue()
        input_dec=self.control.targetDecText.GetValue()
        input_epoch=self.control.targetEpochText.GetValue()
        current_epoch=self.control.currentEpochPos.GetLabel()
        
        
        
        if self.slewing==False:
            
            self.MRO_loc=EarthLocation(lat=46.9528*u.deg, lon=-120.7278*u.deg, height=1198*u.m)
            self.inputcoordSorter(input_ra,input_dec,current_epoch,input_epoch)
            self.obstarget=FixedTarget(name=name,coord=self.coordinates)
            self.target_altaz = self.coordinates.transform_to(AltAz(obstime=Time.now(),location=self.MRO_loc))

            self.alt=str("{0.alt:.2}".format(self.target_altaz))
            self.split_alt=self.alt.split(' ')
            self.slew_altitude=self.split_alt[0]
            
            ''' Debug code
            self.decimalcoords=self.coordinates.to_string('decimal')
            
            
            self.log([input_ra,input_dec,current_epoch])
            self.protocol.sendCommand("slew"+' '+str(self.decimalcoords))
            self.control.slewButton.SetLabel('Stop Slew')
            self.sb.SetStatusText('Slewing: True',1)
            self.control.currentNamePos.SetLabel(name)
            self.control.currentNamePos.SetForegroundColour((0,0,0))
            '''
            if float(self.slew_altitude) > float(self.horizonlimit):

                self.decimalcoords=self.coordinates.to_string('decimal')
            
            
                self.log([input_ra,input_dec,current_epoch])
                self.protocol.sendCommand("slew"+' '+str(self.decimalcoords))
                self.control.slewButton.SetLabel('Stop Slew')
                self.sb.SetStatusText('Slewing: True',1)
                self.control.currentNamePos.SetLabel(name)
                self.control.currentNamePos.SetForegroundColour((0,0,0))
            
                self.slewing= not self.slewing
            
            elif float(self.slew_altitude) < float(self.horizonlimit):
                dlg = wx.MessageDialog(self,
                               "Target is below current minimum altitude, cannot slew.",
                               "Error", wx.OK|wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.log("Error: Attempted slew altitude below 20 degrees.")
                return
                
        elif self.slewing==True:
            self.protocol.sendLine("stop")
            self.control.slewButton.SetLabel('Start Slew')
            self.sb.SetStatusText('Slewing: False',1)
            
            self.slewing= not self.slewing
            
        return

    """Take a selected item from the list and set it as the current target. Load it into the control tab and load it's coordinates into the guidercontrol tab for finder charts"""
    def set_target(self, event):
        name = self.target.targetList.GetItemText(self.target.targetList.GetFocusedItem(),0)
        ra = self.target.targetList.GetItemText(self.target.targetList.GetFocusedItem(),1)
        dec = self.target.targetList.GetItemText(self.target.targetList.GetFocusedItem(),2)
        epoch = self.target.targetList.GetItemText(self.target.targetList.GetFocusedItem(),3)
        mag = self.target.targetList.GetItemText(self.target.targetList.GetFocusedItem(),4)

        #self.coordinates=SkyCoord(ra,dec,frame='icrs')
        #self.guiderControl.current_target=FixedTarget(name=None,coord=self.coordinates)
        #self.image.current_target=FixedTarget(name=None,coord=self.coordinates)
        #self.load_finder_chart()

        #print name, ra, dec, epoch
        self.control.targetNameText.SetValue(name)
        self.control.targetRaText.SetValue(ra)
        self.control.targetDecText.SetValue(dec)
        self.control.targetEpochText.SetValue(epoch)
        self.control.targetMagText.SetValue(mag)
        
        self.log("Current target is '"+name+"'")
        
        return
        
    def load_finder_chart(self):
        
        self.finder_chart=plot_finder_image(self.image.current_target, fov_radius=2*u.degree,ax=self.image.ax1)
        self.image.ax1.set_axis_off()
        self.image.fig.savefig("testfinder.png")
        image_file = 'testfinder.png'

    """Add a manual text item from the target panel to the list control"""
    def addToList(self,event):
        t_name = self.target.nameText.GetValue()
        input_ra = self.target.raText.GetValue()
        input_dec = self.target.decText.GetValue()
        epoch = self.target.epochText.GetValue()
        mag  = self.target.magText.GetValue()
        epoch_now = self.control.currentEpochPos.GetLabel()
        
        self.inputcoordSorter(input_ra,input_dec,epoch_now,epoch)
        self.obstarget=FixedTarget(name=t_name,coord=self.coordinates)
        #airmass= self.MRO.altaz(Time.now(),self.obstarget).secz
       
        
        #add transformation, the epoch should be current
        if self.validity==True:
            
            self.target.targetList.InsertStringItem(self.list_count,str(t_name))
            self.target.targetList.SetStringItem(self.list_count,1,str(input_ra))
            self.target.targetList.SetStringItem(self.list_count,2,str(input_dec))
            self.target.targetList.SetStringItem(self.list_count,3,str(epoch))
            self.target.targetList.SetStringItem(self.list_count,4,str(mag))
            #self.target.targetList.SetStringItem(0,5,str(airmass))
            thread.start_new_thread(self.dyn_airmass,(t_name,input_ra,input_dec,self.obstarget,self.MRO,self.list_count,))
            self.list_count+=1
        return
        
    """Read in a target list file to the ctrl list.
    Format is: name;ra;dec;epoch"""
    def readToList(self,event):
        f_in=open(self.target.fileText.GetValue())
        for line in f_in:
            l = line.split(';')
            print l
            self.target.targetList.InsertStringItem(0,str(l[0]))
            self.target.targetList.SetStringItem(0,1,str(l[1]))
            self.target.targetList.SetStringItem(0,2,str(l[2]))
            self.target.targetList.SetStringItem(0,3,str(l[3]))

        f_in.close()
        return
        
    def dyn_airmass(self,n,r,d,tgt,obs,count):
        while True:
            a= obs.altaz(Time.now(),tgt).secz
            if a > 8 or a < 0:
                a="N/A"
            wx.CallAfter(self.target.targetList.SetStringItem,count,5,str(a))
            #self.target.targetList.SetStringItem(count,5,str(a))
            time.sleep(10)
            
    '''Plot the selected targets position over the next 8 hours'''
    def target_plot(self,event):
        input_ra=self.target.targetList.GetItemText(self.target.targetList.GetFocusedItem(),1)
        input_dec=self.target.targetList.GetItemText(self.target.targetList.GetFocusedItem(),2)
        input_epoch=self.target.targetList.GetItemText(self.target.targetList.GetFocusedItem(),3)
        current_epoch=self.control.currentEpochPos.GetLabel()
        
        self.inputcoordSorter(input_ra,input_dec,current_epoch,input_epoch)
            
        self.targetobject=FixedTarget(name=self.target.targetList.GetItemText(self.target.targetList.GetFocusedItem(),0),coord=self.coordinates)
        self.Obstime=Time.now()
        self.plot_times = self.Obstime + np.linspace(0, 8, 10)*u.hour
        self.target_style={'color':'Black'}
        self.initial_style={'color':'r'}
        
        plot_sky(self.targetobject, self.MRO, self.plot_times,style_kwargs=self.target_style)
        plt.legend(shadow=True, loc=2)
        plot_sky(self.targetobject, self.MRO, self.Obstime,style_kwargs=self.initial_style)
        plt.show()
        
    '''Plot the selected targets airmass curve'''
    def airmass_plot(self,event):
        input_ra=self.target.targetList.GetItemText(self.target.targetList.GetFocusedItem(),1)
        input_dec=self.target.targetList.GetItemText(self.target.targetList.GetFocusedItem(),2)
        input_epoch=self.target.targetList.GetItemText(self.target.targetList.GetFocusedItem(),3)
        current_epoch=self.control.currentEpochPos.GetLabel()
        
        self.inputcoordSorter(input_ra,input_dec,current_epoch,input_epoch)
            
        self.targetobject=FixedTarget(name=self.target.targetList.GetItemText(self.target.targetList.GetFocusedItem(),0),coord=self.coordinates)
        
        self.Obstime=Time.now()
        self.plot_times = self.Obstime + np.linspace(0, 10, 24)*u.hour
        self.target_style={'color':'Black'}
        self.airmass=plot_airmass(self.targetobject, self.MRO, self.plot_times,style_kwargs=self.target_style)
        plt.axhline(y=2,linestyle='--',color='orange')
        plt.axhline(y=2.5,linestyle='--',color='r')
        plt.legend(shadow=True, loc=1)
        plt.show()
        
    """This is the basic pointing protocol for the telescope.  A bubble level is used to set the telescope to a known position.  When the telescope is at Zenith the RA is the current LST, the DEC is the Latitude of the telescope, and the Epoch is the current date transformed to the current epoch"""
    def setTelescopeZenith(self, event):
        name='Zenith'
        ra=self.control.currentLSTPos.GetLabel() #set to current LST
        dec='+46:57:10.08' #set to LAT
        epoch=self.control.currentEpochPos.GetLabel()#define as current epoch
        
        self.init.targetNameText.SetValue(name)
        self.init.targetRaText.SetValue(ra)
        self.init.targetDecText.SetValue(dec)
        self.init.targetEpochText.SetValue(epoch)
        
        return
        
            
            
    def setTelescopePosition(self,event):
        target_name=self.init.targetNameText.GetValue()
        target_ra=self.init.targetRaText.GetValue()
        target_dec=self.init.targetDecText.GetValue()
        target_epoch=self.init.targetEpochText.GetValue()
        
        if target_name=='':
            self.control.currentNamePos.SetLabel('Unknown')
            self.control.currentNamePos.SetForegroundColour((255,0,0))
        else:
            self.control.currentNamePos.SetLabel(str(target_name))
            self.control.currentNamePos.SetForegroundColour('black')   
        
        self.control.currentRaPos.SetLabel(str(target_ra))
        self.control.currentRaPos.SetForegroundColour('black')
        self.control.currentDecPos.SetLabel(str(target_dec))
        self.control.currentDecPos.SetForegroundColour('black')
        
        self.log('Syncing TCC position to'+' '+str(target_ra)+' '+str(target_dec))
        
        return
    
    def setRATrackingRate(self,event):
        RArate=self.init.trackingRateRAText.GetValue()
        
        valid_input=True
        
        try:
            val=float(RArate)
        except ValueError:
            valid_input=False
        
        if valid_input==True:
            self.control.currentRATRPos.SetLabel(RArate)
            self.control.currentRATRPos.SetForegroundColour('black')
        else:
            dlg = wx.MessageDialog(self,
                               "Please input an integer or float number.",
                               "Error", wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy() 
        return
        
    def setDECTrackingRate(self,event):
        DECrate=self.init.trackingRateDECText.GetValue()
        
        valid_input=True
        
        try:
            val=float(DECrate)
        except ValueError:
            valid_input=False
        
        if valid_input==True:
            self.control.currentDECTRPos.SetLabel(DECrate)
            self.control.currentDECTRPos.SetForegroundColour('black')
        else:
            dlg = wx.MessageDialog(self,
                               "Please input an integer or float number.",
                               "Error", wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy() 
        return
        
    def onInit(self,event):
        self.mro.lon=self.dict['lon']
        self.mro.lat=self.dict['lat']
        self.horizonlimit=self.dict['horizonLimit']
        self.control.slewButton.Enable()
        self.control.trackButton.Enable()
        self.init.atZenithButton.Enable()
        thread.start_new_thread(self.timer,())
        self.initState=True
        if self.initState==True:
            self.control.currentJDPos.SetForegroundColour('black')
            self.control.currentLSTPos.SetForegroundColour('black')
            self.control.currentUTCPos.SetForegroundColour('black')
            self.control.currentLocalPos.SetForegroundColour('black')
            self.control.currentEpochPos.SetForegroundColour('black')
            self.sb.SetStatusText('ERROR: Telescope Not Responding',3)

    def timer(self):
        while True:
            t = self.timeCalc()
            wx.CallAfter(self.control.currentJDPos.SetLabel,( '%.2f' % t['mjd']))
            wx.CallAfter(self.control.currentLSTPos.SetLabel,(str(t['lst'])))
            wx.CallAfter(self.control.currentUTCPos.SetLabel,(str(t['utc'])))
            wx.CallAfter(self.control.currentLocalPos.SetLabel,(str(t['local'])))
            wx.CallAfter(self.control.currentEpochPos.SetLabel,('%.3f' % t['epoch']))
            time.sleep(1)

    def timeCalc(self):
        t = Time(Time.now())

        jdt=t.jd
        mjdt = t.mjd
        epoch = 1900.0 + ((float(jdt)-2415020.31352)/365.242198781)
        local = time.strftime('%Y/%m/%d %H:%M:%S')
        self.mro.date=datetime.datetime.utcnow()
        lst = self.mro.sidereal_time()
        return {'mjd':mjdt,'utc':self.mro.date,'local':local,'epoch':epoch, 'lst':lst}

    def test(self,event):
        print 'this is a test event'
        return

    def getFocus(self,event):
        num=self.focusNum.GetValue()
        files=os.popen('tail -%s /Users/%s/nfocus.txt' % (num, os.getenv('USER')), 'r')
        for l in files:
            self.focusLog.AppendText(l)
   

class DataForwardingProtocol(basic.LineReceiver):

    def __init__(self):
        self.output = None
        self._deferreds = {}

    def dataReceived(self, data):
        gui = self.factory.gui
        gui.protocol = self
        gui.control.protocol= self

        if gui:
            val = gui.control.logBox.GetValue()
            gui.control.logBox.SetValue(val + data)
            gui.control.logBox.SetInsertionPointEnd()
            sep_data= data.split(" ")
            if sep_data[0] in self._deferreds:
                self._deferreds.pop(sep_data[0]).callpack(sep_data[1])

    def sendCommand(self, data):
        self.sendLine(data)
        d=self._deferreds[data.split(" ")[0]]=defer.Deferred()
        return d
    
    def connectionMade(self):
        self.output = self.factory.gui.control.logBox

class TCCClient(protocol.ClientFactory):

    def __init__(self, gui):
        self.gui = gui
        self.protocol = DataForwardingProtocol

    def clientConnectionLost(self, transport, reason):
        reactor.stop()

    def clientConnectionFailed(self, transport, reason):
        reactor.stop()

if __name__=="__main__":

  app = wx.App()
  app.frame = TCC()
  app.frame.Show()
  reactor.registerWxApp(app)
  reactor.connectTCP('localhost',5501,TCCClient(app.frame))
  reactor.run()
  app.MainLoop()
