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

def addToList(self,event):
    """
    Add a manual text item from the target panel to the list control. Requires valid inputs for coordinate sorter.
    This includes valid formats for RA and DEC which are consistent with one another.
    Epoch should be inputted as J2000 or J1950. addToList runs a dynamic airmass calculation as per these inputs.

    Args:
            event: handler to allow function to be tethered to a wx widget. Tethered to the "Add Item to List" button in the target list tab.

    Returns:
            None

    """
    t_name = self.target.nameText.GetValue()
    input_ra = self.target.raText.GetValue()
    input_dec = self.target.decText.GetValue()
    epoch = self.target.epochText.GetValue()
    mag  = self.target.magText.GetValue()
    epoch_now = self.control.currentEpochPos.GetLabel()

    if not str(epoch[0]).isalpha():
        dlg = wx.MessageDialog(self,
                       "Entry Error: Epoch Entry is missing identifier ('J'2000 or 'B'1950). Please enter the appropriate identifier.",
                       "Error", wx.OK|wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return

    self.inputcoordSorter(input_ra,input_dec,epoch)

    if self.galactic_coords==True:
        input_ra=self.coordinates.ra.degree
        input_dec=self.coordinates.dec.degree

    if self.telescope_status.get('precession')==True:
        self.coordprecess(self.coordinates,epoch_now,epoch)

    #airmass= self.MRO.altaz(Time.now(),self.obstarget).secz
    self.obstarget=FixedTarget(name=t_name,coord=self.coordinates)
    #airmass= self.MRO.altaz(Time.now(),self.obstarget).secz


    #add transformation, the epoch should be current
    if self.validity==True:

        self.target.targetList.InsertStringItem(self.list_count,str(t_name))
        self.target.targetList.SetStringItem(self.list_count,1,str(input_ra))
        self.target.targetList.SetStringItem(self.list_count,2,str(input_dec))
        self.target.targetList.SetStringItem(self.list_count,3,str(epoch))
        self.target.targetList.SetStringItem(self.list_count,4,str(mag))
        t = threading.Thread(target=self.dyn_airmass, args=(self.obstarget,self.MRO,self.list_count,), name="airmass_"+str(self.list_count))
        t.daemon = True
        t.start()
        self.active_threads["airmass_"+str(self.list_count)] = t
        self.list_count+=1
    return

# ----------------------------------------------------------------------------------
def readToList(self,event):
    """
    Read in a target list file to the ctrl list.
    Format is: name;ra;dec;epoch

    Args:
            event: handler to allow function to be tethered to a wx widget.
            Tethered to the "Retrieve List" button in the target list tab.

    Returns:
            None

    """
    frame = wx.Frame(None, -1, '')
    frame.SetDimensions(0,0,200,50)

    openBox = wx.FileDialog(frame, "Open", "", "", "Text Files (*.txt)|*.txt", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
    openBox.ShowModal()
    f_in = open(openBox.GetPath())
    openBox.Destroy()

    # try:
    #     f_in=open('/home/mro/Desktop/targetlists/'+self.target.fileText.GetValue())
    #     #f_in=open('/home/doug/TCC/targetlists/'+self.target.fileText.GetValue())
    # except IOError:
    #     dlg = wx.MessageDialog(self,
    #                    "Path Error: File not Found. Verify that the file exists in /home/mro/Desktop/targetlists/\n\nNote: This is the folder on the desktop.",
    #                    "Error", wx.OK|wx.ICON_ERROR)
    #     dlg.ShowModal()
    #     dlg.Destroy()
    #     return
    #f_in=open(self.target.fileText.GetValue())
    for line in f_in:
        l = line.split(';')
        print l
        t_name = l[0]
        input_ra = l[1]
        input_dec = l[2]
        epoch = l[3]
        mag=l[4][0:-1]
        epoch_now = self.control.currentEpochPos.GetLabel()

        self.inputcoordSorter(input_ra,input_dec,epoch)

        if self.galactic_coords==True:
            input_ra=self.coordinates.ra.degree
            input_dec=self.coordinates.dec.degree

        if self.telescope_status.get('precession')==True:
            self.coordprecess(self.coordinates,epoch_now,epoch)

        self.obstarget=FixedTarget(name=t_name,coord=self.coordinates)

        if self.validity==True:

            self.target.targetList.InsertStringItem(self.list_count,str(t_name))
            self.target.targetList.SetStringItem(self.list_count,1,str(input_ra))
            self.target.targetList.SetStringItem(self.list_count,2,str(input_dec))
            self.target.targetList.SetStringItem(self.list_count,3,str(epoch))
            self.target.targetList.SetStringItem(self.list_count,4,str(mag))
            #self.target.targetList.SetStringItem(0,5,str(airmass))
            #thread.start_new_thread(self.dyn_airmass,(self.obstarget,self.MRO,self.list_count,))
            t = threading.Thread(target=self.dyn_airmass, args=(self.obstarget,self.MRO,self.list_count,), name="airmass_"+str(self.list_count))
            t.daemon = True
            t.start()
            self.active_threads["airmass_"+str(self.list_count)] = t
            self.list_count+=1

    f_in.close()
    return
# ----------------------------------------------------------------------------------
def refreshList(self,event):
    """
    Updates the choices of the file path combobox on the target tab to the current files in
    the Desktop folder.

    Use Case: User starts software and adds new file to targetlist folder, the "Refresh Choices"
    button is clicked and then the new file is accessible via dropdown in the combobox.

    Args:
            event: handler to allow function to be tethered to a wx widget.
            Tethered to the "Refresh Choices" button in the target list tab.

    Returns:
            None

    """
    listpath = '/home/mro/Desktop/targetlists/*'
    #listpath = '/home/doug/TCC/targetlists/*'
    targetlists=glob.glob(listpath)
    self.target.fileText.Clear()
    for list in targetlists:
        list=list.split('/')[-1]
        self.target.fileText.Append(list)
    #self.target.fileText.SetParameters(list_format)
# ------------------w----------------------------------------------------------------
def removeFromList(self,event):
    """
    Remove selected item from list. Operates by clearing list and then regenerating surviving entries.

    Args:
            event: handler to allow function to be tethered to a wx widget.
            Tethered to the "Retrieve List" button in the target list tab.

    Returns:
            None

    """
    del_item=self.target.targetList.GetFocusedItem()
    self.calculate=False
    for key in self.active_threads:
        self.active_threads[key].join()

    self.object_list=[]
    self.listrange=np.arange(0,self.target.targetList.GetItemCount())
    for row in self.listrange:
        if row!=del_item:
            name=self.target.targetList.GetItem(itemId=row, col=0).GetText()
            ra=self.target.targetList.GetItem(itemId=row, col=1).GetText()
            dec=self.target.targetList.GetItem(itemId=row, col=2).GetText()
            epoch=self.target.targetList.GetItem(itemId=row, col=3).GetText()
            vmag=self.target.targetList.GetItem(itemId=row, col=4).GetText()

            objectdata=str(name)+';'+str(ra)+';'+str(dec)+';'+str(epoch)+';'+str(vmag)
            self.object_list.append(objectdata)

    self.target.targetList.DeleteAllItems()
    self.active_threads={}
    self.list_count=0
    self.calculate=True

    for entry in self.object_list:
        l=entry.split(';')
        t_name = l[0]
        input_ra = l[1]
        input_dec = l[2]
        epoch = l[3]
        mag=l[4]
        epoch_now = self.control.currentEpochPos.GetLabel()

        self.inputcoordSorter(input_ra,input_dec,epoch)

        if self.telescope_status.get('precession')==True:
            self.coordprecess(self.coordinates,epoch_now,epoch)

        self.obstarget=FixedTarget(name=t_name,coord=self.coordinates)
        self.target.targetList.InsertStringItem(self.list_count,str(t_name))
        self.target.targetList.SetStringItem(self.list_count,1,str(input_ra))
        self.target.targetList.SetStringItem(self.list_count,2,str(input_dec))
        self.target.targetList.SetStringItem(self.list_count,3,str(epoch))
        self.target.targetList.SetStringItem(self.list_count,4,str(mag))
        t = threading.Thread(target=self.dyn_airmass, args=(self.obstarget,self.MRO,self.list_count,), name="airmass_"+str(self.list_count))
        t.daemon = True
        t.start()
        self.active_threads["airmass_"+str(self.list_count)] = t
        self.list_count+=1

# ----------------------------------------------------------------------------------
