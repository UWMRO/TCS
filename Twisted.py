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


'''
Twisted Python
'''

class DataForwardingProtocol(basic.LineReceiver):
    # ----------------------------------------------------------------------------------
    def __init__(self):
        self.output = None
        self._deferreds = {}
        self.connectState=False
    # ----------------------------------------------------------------------------------
    def dataReceived(self, data):
        gui = self.factory.gui
        gui.protocol = self
        gui.control.protocol= self
        print "data received from server:" ,data
        print repr(data)

        if gui:
            val = gui.control.logBox.GetValue()
            self.timestamp()
            gui.control.logBox.SetValue(val+stamp+data+'\n')
            gui.control.logBox.SetInsertionPointEnd()
            gui.target.logBox.SetValue(val+stamp+data+'\n')
            gui.target.logBox.SetInsertionPointEnd()
            gui.init.logBox.SetValue(val+stamp+data+'\n')
            gui.init.logBox.SetInsertionPointEnd()
            sep_data= data.split(" ")
            if sep_data[0] in self._deferreds:
                self._deferreds.pop(sep_data[0]).callback(sep_data[1])
    # ----------------------------------------------------------------------------------
    def sendCommand(self, data):
        self.transport.write(data)
        d=self._deferreds[data.split(" ")[0]]=defer.Deferred()
        return d

    # ----------------------------------------------------------------------------------
    def connectionMade(self):
        gui=self.factory.gui
        gui.protocol=self
        self.output = self.factory.gui.control.logBox
        self.connectState=True

    # ----------------------------------------------------------------------------------
    def timestamp(self):
    	t=datetime.now()
    	if len(str(t.month))==1:
    		month='0'+str(t.month)
    	else:
    		month=str(t.month)
    	if len(str(t.day))==1:
    		day='0'+str(t.day)
    	else:
    		day=str(t.day)
    	if len(str(t.hour))==1:
    		hour='0'+str(t.hour)
    	else:
    		hour=str(t.hour)
    	if len(str(t.minute))==1:
    		minute='0'+str(t.minute)
    	else:
    		minute=str(t.minute)
    	if len(str(t.second))==1:
    		second='0'+str(t.second)
    	else:
    		second=str(t.second)
    	global stamp
    	stamp=str(t.year)+str(month)+str(day)+'  '+str(hour)+':'+str(minute)+':'+str(second)+': '
    	return stamp
