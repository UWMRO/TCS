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

class Control(wx.Panel):
    """Primary tab for telescope operation, display status of telescope parameters."""
    # ----------------------------------------------------------------------------------
    def __init__(self,parent, debug, night):
        """Create the Control Panel"""
        wx.Panel.__init__(self,parent)

        self.parent = parent


        #Logbox for the control tab, continuous updates supplied by TCC.log
        self.logBox = wx.TextCtrl(self, style= wx.TE_READONLY | wx.TE_MULTILINE | wx.VSCROLL)

        ############################################################

        #Manual Target Input

        #Target Name
        self.targetNameLabel = wx.StaticText(self, size=(75,-1))
        self.targetNameLabel.SetLabel('Name: ')
        self.targetNameText = wx.TextCtrl(self,size=(125,-1))

        #Target Right Ascension
        self.targetRaLabel = wx.StaticText(self, size=(75,-1))
        self.targetRaLabel.SetLabel('RA: ')
        self.targetRaText = wx.TextCtrl(self,size=(125,-1))

        #Target Declination
        self.targetDecLabel = wx.StaticText(self, size=(75,-1))
        self.targetDecLabel.SetLabel('DEC: ')
        self.targetDecText = wx.TextCtrl(self,size=(125,-1))

        #Target Epoch
        self.targetEpochLabel = wx.StaticText(self, size=(75,-1))
        self.targetEpochLabel.SetLabel('EPOCH: ')
        self.targetEpochText = wx.TextCtrl(self,size=(125,-1))

        #Target V Magnitude
        self.targetMagLabel = wx.StaticText(self, size=(75,-1))
        self.targetMagLabel.SetLabel('V Mag: ')
        self.targetMagText = wx.TextCtrl(self,size=(125,-1))

        #############################################################

        #TCC Status Items

        #Current Target Name
        self.currentNameLabel = wx.StaticText(self, size=(75,-1))
        self.currentNameLabel.SetLabel('Name:')
        self.currentNamePos = wx.StaticText(self,size=(100,-1))
        self.currentNamePos.SetLabel('Unknown')
        self.currentNamePos.SetForegroundColour((255,0,0))

        #Current RA Position of the Telescope
        self.currentRaLabel = wx.StaticText(self, size=(75,-1))
        self.currentRaLabel.SetLabel('RA: ')
        self.currentRaPos = wx.StaticText(self,size=(100,-1))
        self.currentRaPos.SetLabel('Unknown')
        self.currentRaPos.SetForegroundColour((255,0,0))

        #Current DEC Position of the Telescope
        self.currentDecLabel = wx.StaticText(self, size=(75,-1))
        self.currentDecLabel.SetLabel('DEC: ')
        self.currentDecPos = wx.StaticText(self,size=(100,-1))
        self.currentDecPos.SetLabel('Unknown')
        self.currentDecPos.SetForegroundColour((255,0,0))

        #Current Epoch (updated by timer thread)
        self.currentEpochLabel = wx.StaticText(self, size=(75,-1))
        self.currentEpochLabel.SetLabel('EPOCH: ')
        self.currentEpochPos = wx.StaticText(self,size=(75,-1))
        self.currentEpochPos.SetLabel('Unknown')
        self.currentEpochPos.SetForegroundColour((255,0,0))

        #CUrrent Date and Time in Universal Time (updated by timer thread)
        self.currentUTCLabel = wx.StaticText(self, size=(75,-1))
        self.currentUTCLabel.SetLabel('UTC: ')
        self.currentUTCPos = wx.StaticText(self,size=(150,-1))
        self.currentUTCPos.SetLabel('Unknown')
        self.currentUTCPos.SetForegroundColour((255,0,0))

        #Current Local Sidereal Time (updated by timer thread)
        self.currentLSTLabel = wx.StaticText(self, size=(75,-1))
        self.currentLSTLabel.SetLabel('LST: ')
        self.currentLSTPos = wx.StaticText(self,size=(100,-1))
        self.currentLSTPos.SetLabel('Unknown')
        self.currentLSTPos.SetForegroundColour((255,0,0))

        #Current Local Date and Time (updated by timer thread)
        self.currentLocalLabel = wx.StaticText(self, size=(75,-1))
        self.currentLocalLabel.SetLabel('Local: ')
        self.currentLocalPos = wx.StaticText(self,size=(150,-1))
        self.currentLocalPos.SetLabel('Unknown')
        self.currentLocalPos.SetForegroundColour((255,0,0))

        #Current Julian Date (updated by timer thread)
        self.currentJDLabel = wx.StaticText(self, size=(75,-1))
        self.currentJDLabel.SetLabel('MJD: ')
        self.currentJDPos = wx.StaticText(self,size=(75,-1))
        self.currentJDPos.SetLabel('Unknown')
        self.currentJDPos.SetForegroundColour((255,0,0))

        #Current Relative Position of the focus axis
        self.currentFocusLabel = wx.StaticText(self, size=(75,-1))
        self.currentFocusLabel.SetLabel('Focus: ')
        self.currentFocusPos = wx.StaticText(self,size=(75,-1))
        self.currentFocusPos.SetLabel('Unknown')
        self.currentFocusPos.SetForegroundColour((255,0,0))

        #Current RA Tracking Rate
        self.currentRATRLabel = wx.StaticText(self, size=(75,-1))
        self.currentRATRLabel.SetLabel('RA TR: ')
        self.currentRATRPos = wx.StaticText(self,size=(75,-1))
        self.currentRATRPos.SetLabel('Unknown')
        self.currentRATRPos.SetForegroundColour((255,0,0))

        #Current DEC Tracking Rate
        #self.currentDECTRLabel = wx.StaticText(self, size=(75,-1))
        #self.currentDECTRLabel.SetLabel('DEC TR: ')
        #self.currentDECTRPos = wx.StaticText(self,size=(75,-1))
        #self.currentDECTRPos.SetLabel('Unknown')
        #self.currentDECTRPos.SetForegroundColour((255,0,0))

        #############################################################

        #Focus Controls
        self.focusIncPlusButton = wx.Button(self, -1, 'Increment Positive')
        self.focusIncNegButton = wx.Button(self, -1, 'Increment Negative')
        self.focusAbsText = wx.TextCtrl(self,size=(75,-1))
        self.focusAbsText.SetValue('1500')
        self.focusAbsMove = wx.Button(self,-1,'Move Relative')
        self.focusAbsMove.SetBackgroundColour('Light Slate Blue')
        self.focusAbsMove.SetForegroundColour('White')

        #############################################################

        #Telescope Control Buttons
        self.slewButton = wx.Button(self, -1, "Slew to Target")
        self.slewButton.SetBackgroundColour('Light Slate Blue')
        self.slewButton.SetForegroundColour('White')
        self.slewButton.Disable()
        self.trackButton = wx.Button(self, -1, "Start Tracking")
        self.trackButton.SetBackgroundColour('Light Slate Blue')
        self.trackButton.SetForegroundColour('White')
        self.trackButton.Disable()
        self.pointButton = wx.Button(self, -1, "Update Pointing to Target")
        self.pointButton.Disable()
        self.stopButton = wx.Button(self, -1, "  EMERGENCY STOP  ")
        self.stopButton.SetBackgroundColour('Red')
        self.stopButton.SetForegroundColour('White')

        #############################################################

        #Telescope Jog Controls
        self.jogNButton = wx.Button(self, -1, 'N')
        self.jogNButton.SetBackgroundColour('Light Slate Blue')
        self.jogNButton.SetForegroundColour('White')
        self.jogSButton = wx.Button(self, -1, 'S')
        self.jogSButton.SetBackgroundColour('Light Slate Blue')
        self.jogSButton.SetForegroundColour('White')
        self.jogWButton = wx.Button(self, -1, 'W')
        self.jogWButton.SetBackgroundColour('Light Slate Blue')
        self.jogWButton.SetForegroundColour('White')
        self.jogEButton = wx.Button(self, -1, 'E')
        self.jogEButton.SetBackgroundColour('Light Slate Blue')
        self.jogEButton.SetForegroundColour('White')
        self.jogIncrement = wx.TextCtrl(self,size=(50,-1))
        self.jogIncrement.SetValue('1.0')
        self.jogUnits = wx.ComboBox(self, -1, "arcsec", size =(100,-1), style = wx.CB_DROPDOWN,
                                    choices=["arcsec", "arcmin", "deg"])

        #############################################################

        #Sizers; Build Sizers
        self.vbox=wx.BoxSizer(wx.VERTICAL)
        self.vbox1=wx.BoxSizer(wx.VERTICAL)
        self.vbox2=wx.BoxSizer(wx.VERTICAL)
        self.vbox7=wx.BoxSizer(wx.VERTICAL)
        self.hbox1=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3=wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.gbox=wx.GridSizer(rows=6, cols=2, hgap=5, vgap=5)
        self.gbox2=wx.GridSizer(rows=10, cols=2, hgap=0, vgap=5)
        self.gbox3=wx.GridSizer(rows=2, cols=2, hgap=5, vgap=5)

        #Current Target Sizer
        self.ctlabel = wx.StaticBox(self,label="Current Target")
        self.vbox3 = wx.StaticBoxSizer(self.ctlabel, wx.VERTICAL)

        #TCC Status Sizer
        self.TCCstatus=wx.StaticBox(self,label="TCC Status")
        self.vbox4= wx.StaticBoxSizer(self.TCCstatus, wx.VERTICAL)

        #Focus Sizer
        self.flabel=wx.StaticBox(self,label="Focus")
        self.vbox5= wx.StaticBoxSizer(self.flabel, wx.VERTICAL)

        #Jog Telescope Sizer
        self.jlabel=wx.StaticBox(self,label="Jog Telescope")
        self.vbox6= wx.StaticBoxSizer(self.jlabel, wx.VERTICAL)

        #Sizers: Populate Sizers

        #Populate Current Target Box
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
        self.gbox.Add(self.slewButton,0, wx.ALIGN_CENTER)
        self.gbox.Add(self.trackButton,0, wx.ALIGN_CENTER)

        self.vbox3.Add(self.gbox,0,wx.ALIGN_CENTER)
        self.vbox3.AddSpacer(10)
        self.vbox3.Add(self.pointButton,0,wx.ALIGN_CENTER)
        self.vbox1.Add(self.vbox3,0,wx.ALIGN_CENTER)

        #Populate TCC Status Box
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
        #self.gbox2.Add(self.currentDECTRLabel, 0, wx.ALIGN_RIGHT)
        #self.gbox2.Add(self.currentDECTRPos, 0, wx.ALIGN_LEFT)

        self.vbox4.Add(self.gbox2,0,wx.ALIGN_CENTER)

        self.vbox7.Add(self.vbox4,0,wx.ALIGN_CENTER)
        self.vbox7.AddSpacer(5)
        self.vbox7.Add(self.stopButton,0,wx.ALIGN_CENTER)

        self.gbox3.Add(self.focusIncPlusButton, 0, wx.ALIGN_LEFT)
        self.gbox3.Add(self.focusAbsText, 0, wx.ALIGN_LEFT)
        self.gbox3.Add(self.focusIncNegButton, 0, wx.ALIGN_LEFT)
        self.gbox3.Add(self.focusAbsMove, 0, wx.ALIGN_LEFT)

        self.vbox5.Add(self.gbox3,0,wx.ALIGN_CENTER)

        self.hbox3.Add(self.jogEButton,0,wx.ALIGN_LEFT)
        self.hbox3.AddSpacer(5)
        self.hbox3.Add(self.jogWButton,0,wx.ALIGN_LEFT)

        self.hbox4.Add(self.jogIncrement,0,wx.ALIGN_LEFT)
        self.hbox4.AddSpacer(5)
        self.hbox4.Add(self.jogUnits, 0, wx.ALIGN_LEFT)

        self.vbox6.Add(self.jogNButton,0,wx.ALIGN_CENTER)
        self.vbox6.AddSpacer(5)
        self.vbox6.Add(self.hbox3,0,wx.ALIGN_CENTER)
        self.vbox6.AddSpacer(5)
        self.vbox6.Add(self.jogSButton,0,wx.ALIGN_CENTER)
        self.vbox6.AddSpacer(5)
        self.vbox6.Add(self.hbox4 ,0, wx.ALIGN_CENTER)

        self.vbox2.Add(self.vbox5,0,wx.ALIGN_CENTER)
        self.vbox2.AddSpacer(15)
        self.vbox2.Add(self.vbox6,0,wx.ALIGN_CENTER)


        self.hbox1.Add(self.vbox7, 0, wx.ALIGN_CENTER)
        self.hbox1.AddSpacer(15)
        self.hbox1.Add(self.vbox1, 0, wx.ALIGN_CENTER)
        self.hbox1.AddSpacer(15)
        self.hbox1.Add(self.vbox2, 0, wx.ALIGN_CENTER)

        self.hbox5.AddSpacer(30)
        self.hbox5.Add(self.logBox, -1, wx.EXPAND)
        self.hbox5.AddSpacer(30)

        self.vbox.Add(self.hbox1,0,wx.ALIGN_CENTER)
        self.vbox.AddSpacer(15)
        self.vbox.Add(self.hbox5,-1,wx.EXPAND)
        self.vbox.AddSpacer(15)

        self.SetSizer(self.vbox)

###########################################################################################
