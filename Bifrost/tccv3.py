#!/user/local/bin python
#Bifrost Telescope Control Computer Software
#For use at Manastash Ridge Observatory in Ellensburg, WA

#Version 1.0

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
wxreactor.install()
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

#----------------------------------------------------------------------------------
'''
    These were all their own classes in the original file.
    They have been split into their own files.
'''
from ControlClass import Control
from TargetClass import Target
from GuiderTab import GuiderPerformance, GuiderControl
from Initialization import Initialization
from NightLog import NightLog
from Export import TargetExportWindow, Export
from Twisted import DataForwardingProtocol

#----------------------------------------------------------------------------------
'''
    These files consist of various functions that were all originally in the TCC
    Class. I split them up according to their function. If any are deemed to be in
    the wrong place feel free to change them or contact Anoop.
'''
import exiting, Offset, Focus, SlewVelmeasure, Coordinates, FinderFuncs, ListFuncs
import SetParams, TelescopePosition, TimeFuncs, LogFuncs, PlotFuncs, GUI_Options
import ReadConfigFiles
###########################################################################################

class TCC(wx.Frame):
    """Frame class for the Telescope Control Computer (TCC)."""
    title='Bifrost Telescope Control Computer'

    # ----------------------------------------------------------------------------------
    def __init__(self):
        """Create the TCC Frame"""
        wx.Frame.__init__(self, None, -1, self.title,size=(900,675)) #Wxpython frame object

        #############################################################

        #Dictionaries of relevant telescope information

        #Most of Bifrost's functions rely on and alter the contents of these dictionaries.
        #Bifrost has been designed such that these dictionaries provide a quick summary of the overall observing
        #session.

        #Telescope Status: Contains information on dynamic processes in GUI operation
        self.telescope_status={'connectState':False,'RA':'Unknown', 'Dec':'Unknown', 'slewing':False,'tracking':False,
                               'guiding':False, 'pointState': False,'precession': True,
                               'initState':False,'guider_rot' :False}

        #Initilization Status: Contains information on (typically) static processes in GUI operation or information
        #from past observing sessions.
        self.dict={'lat':None, 'lon':None,'elevation':None, 'lastRA':None, 'lastDEC':None,'lastGuiderRot':None,
                   'lastFocusPos':None,'maxdRA':None,'maxdDEC':None, 'RAtrackingRate':None }

        #Target Coordinates: For pointing, align telescope coordinates with these values once pointing is carried out.
        self.target_coords={"Name":None, "RA": None, "Dec": None}

        #############################################################

        #Additional variables

        self.protocol = None  # twisted python connection protocol to server, overwrite during connection
        self.server = DataForwardingProtocol()  # Twisted Python server identification
        self.calculate = True  # Flag for dynamic airmass calculation
        self.night = True  # Send GUI to night mode
        self.export_active = False  # Track the status of the export target list window
        self.d_color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BACKGROUND) #Default background color for OS
        self.list_count=0 #Tracks the number of targets currently in the targetlist.
        self.active_threads={} #Keep track of threads open in GUI
        self.thread_to_close=-1
        self.current_timezone="PST" #Current timezone is Pacific Standard Time at MRO
        self.mro=ephem.Observer() #Ephem object for mro location (To do: Roll this into Astroplan's Observer object)
        self.mrolat=46.9528*u.deg #Latitude of Manastash Ridge Observatory
        self.MRO = Observer(longitude = -120.7278 *u.deg, #Astroplan Observer Object for MRO
                latitude = 46.9528*u.deg,
                elevation = 1198*u.m,
                name = "Manastash Ridge Observatory"
                )
        #self.at_MRO = True #Dev variable for ease of development offsite
        self.process_list=[]
        debug=True #Debug mode, currently no functionality
        ico = wx.Icon("bifrost_small.ico", wx.BITMAP_TYPE_ICO) #GUI Icon
        self.SetIcon(ico)
        self.dir=os.getcwd() #Current path for file IO
        #if self.at_MRO == True:
        self.stordir = "/home/mro/storage/tcc_data"
        #else:
        #self.stordir = self.dir
        self.plot_open = False

        self.code_timer_W = wx.Timer(self)
        self.code_timer_E = wx.Timer(self)
        self.code_timer_N = wx.Timer(self)
        self.code_timer_S = wx.Timer(self)
        self.code_timer_Slew = wx.Timer(self)

        self.stop_time = 250 #Waiting time for tracking to finish 500 works

        #self.targetlists=glob.glob('/home/mro/Desktop/targetlists/*')
        #self.targetlists=glob.glob('/home/doug/TCC/targetlists/*')

        #############################################################

        #Setup Notebook

        p=wx.Panel(self)
        nb=wx.Notebook(p)
        controlPage=Control(nb, debug, self.night) #Telescope Control Tab
        targetPage=Target(nb, debug, self.night) #Target List Tab
        guiderControlPage=GuiderControl(nb,debug,self.night) #Guider Control Tab
        initPage=Initialization(nb, debug, self.night) #Initialization Tab
        logPage=NightLog(nb, debug, self.night) #Night Log Tab


        nb.AddPage(controlPage,"Telescope Control")
        self.control=nb.GetPage(0)

        nb.AddPage(targetPage,"Target List")
        self.target=nb.GetPage(1)

        nb.AddPage(guiderControlPage,"Guider Control")
        self.guiderControl=nb.GetPage(2)

        nb.AddPage(initPage,"Initialization")
        self.init=nb.GetPage(3)

        #nb.AddPage(logPage,"Night Log")
        #self.nl=nb.GetPage(3)

        #Control Tab Bindings
        self.Bind(wx.EVT_BUTTON, self.startSlew, self.control.slewButton)
        self.Bind(wx.EVT_BUTTON,self.toggletracksend,self.control.trackButton)
        self.Bind(wx.EVT_BUTTON, self.pointing, self.control.pointButton)
        self.Bind(wx.EVT_BUTTON,self.haltmotion,self.control.stopButton)
        self.Bind(wx.EVT_BUTTON,self.Noffset,self.control.jogNButton)
        self.Bind(wx.EVT_BUTTON,self.Soffset,self.control.jogSButton)
        self.Bind(wx.EVT_BUTTON,self.Eoffset,self.control.jogEButton)
        self.Bind(wx.EVT_BUTTON,self.Woffset,self.control.jogWButton)
        self.Bind(wx.EVT_BUTTON,self.focusIncPlus,self.control.focusIncPlusButton)
        self.Bind(wx.EVT_BUTTON,self.focusIncNeg,self.control.focusIncNegButton)
        self.Bind(wx.EVT_BUTTON,self.setfocus,self.control.focusAbsMove)

        #Target Tab Bindings
        self.Bind(wx.EVT_BUTTON, self.set_target, self.target.selectButton)
        self.Bind(wx.EVT_BUTTON, self.addToList, self.target.enterButton)
        self.Bind(wx.EVT_BUTTON, self.populateCurrPos, self.target.popButton)
        self.Bind(wx.EVT_BUTTON, self.readToList, self.target.listButton)
        self.Bind(wx.EVT_BUTTON, self.removeFromList,self.target.removeButton)
        self.Bind(wx.EVT_BUTTON, self.ExportOpen,self.target.exportButton)
        self.Bind(wx.EVT_BUTTON, self.target_plot, self.target.plot_button)
        self.Bind(wx.EVT_BUTTON, self.airmass_plot, self.target.airmass_button)
        self.Bind(wx.EVT_BUTTON,self.FinderOpen,self.target.finder_button)
        #self.Bind(wx.EVT_BUTTON,self.refreshList,self.target.refresh_button)

        #Guider Control Tab Bindings
        #self.Bind(wx.EVT_BUTTON,self.on_Rot,self.guiderControl.guiderRotButton)

        # Init Tab Bindings
        self.Bind(wx.EVT_BUTTON,self.setTelescopeZenith ,self.init.atZenithButton)
        self.Bind(wx.EVT_BUTTON, self.setTelescopePosition, self.init.syncButton)
        self.Bind(wx.EVT_BUTTON, self.onInit, self.init.initButton)
        self.Bind(wx.EVT_BUTTON, self.setRATrackingRate,self.init.rateRAButton)
        self.Bind(wx.EVT_BUTTON, self.resetRATrackingRate,self.init.resetTRButton)
        self.Bind(wx.EVT_BUTTON, self.setmaxdRA, self.init.dRAButton)
        self.Bind(wx.EVT_BUTTON, self.setmaxdDEC, self.init.dDECButton)
        self.Bind(wx.EVT_BUTTON, self.coverpos, self.init.coverposButton)
        self.Bind(wx.EVT_BUTTON, self.parkscope, self.init.parkButton)
        #self.Bind(wx.EVT_BUTTON, self.pointing, self.init.onTargetButton)

        self.Bind(wx.EVT_TIMER,self.timeW,self.code_timer_W)
        self.Bind(wx.EVT_TIMER,self.timeE,self.code_timer_E)
        self.Bind(wx.EVT_TIMER,self.timeN,self.code_timer_N)
        self.Bind(wx.EVT_TIMER,self.timeS,self.code_timer_S)

        self.Bind(wx.EVT_TIMER,self.timeSlew,self.code_timer_Slew)

        self.createMenu()

        self.sb = self.CreateStatusBar(5)
        self.sb.SetStatusWidths([150,150,150,-2,-1])

        sizer=wx.BoxSizer()
        sizer.Add(nb,1, wx.EXPAND|wx.ALL)
        p.SetSizer(sizer)
        p.Layout()

        #############################################################

        self.readConfig()

        """Target testing parameters """
        #self.target.nameText.SetValue('M31')
        #self.target.raText.SetValue('00h42m44.330s')
        #self.target.decText.SetValue('+41d16m07.50s')
        #self.target.epochText.SetValue('J2000')
        #self.target.magText.SetValue('3.43')

	try:
        	img_default=os.path.join(self.dir,'gcam_56901_859.jpg')
        	img=mpimg.imread(img_default)
		self.guiderControl.ax_r.imshow(img, picker=False)
        	self.guiderControl.canvas_l.mpl_connect('pick_event', self.on_pick)
	except:
		print('');
        

    # ----------------------------------------------------------------------------------

    def createMenu(self):
        '''
        Generates the menu bar for the WX application.

            Args:
                None
            Returns:
                None
        '''
        self.menubar = wx.MenuBar()

        menu_file = wx.Menu()
        m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")

        tool_file = wx.Menu()
        #m_night = tool_file.Append(-1, 'Night\tCtrl-N','Night Mode')

        tz_choice = wx.Menu()
        tz_choice.Append(1110, "Pacific", "Set Time Zone", kind=wx.ITEM_RADIO)
        tz_choice.Append(1111, "Mountain", "Set Time Zone", kind=wx.ITEM_RADIO)
        tz_choice.Check(id=1110, check=True)
        tool_file.AppendMenu(1112,'Time Zone',tz_choice)

        precess = wx.Menu()
        precess.Append(1120, "On", "Set Precession", kind=wx.ITEM_RADIO)
        precess.Append(1121, "Off", "Set Precession", kind=wx.ITEM_RADIO)
        precess.Check(id=1120, check=True)
        tool_file.AppendMenu(1122,'Precession',precess)

        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)
        self.Bind(wx.EVT_CLOSE, self.on_exit)
        #self.Bind(wx.EVT_MENU, self.on_night, m_night)
        self.Bind(wx.EVT_MENU, self.on_Pacific, id=1110)
        self.Bind(wx.EVT_MENU, self.on_Mountain, id=1111)
        self.Bind(wx.EVT_MENU, self.pre_on, id=1120)
        self.Bind(wx.EVT_MENU, self.pre_off, id=1121)

        helpMenu = wx.Menu()
        helpMenu.Append(1300, "&Help")
        self.Bind(wx.EVT_MENU, self.onHelp, id=1300)

        self.menubar.Append(menu_file, "&File")
        self.menubar.Append(tool_file, "&Tools")
        self.menubar.Append(helpMenu, "&Help")

        self.SetMenuBar(self.menubar)

    # ----------------------------------------------------------------------------------

    def on_exit(self, event):
         exiting.on_exit(self,event)
    # ----------------------------------------------------------------------------------

    def quit(self):
         exiting.quit(self)
    # ----------------------------------------------------------------------------------

    def on_night(self,event):
        GUI_Options.on_night(self, event)
    # ----------------------------------------------------------------------------------
    def on_Pacific(self,event):
        TimeFuncs.on_Pacific(self,event)

    # ----------------------------------------------------------------------------------
    def on_Mountain(self,event):
        TimeFuncs.on_Mountain(self,event)

    # ----------------------------------------------------------------------------------
    def pre_on(self,event):
        GUI_Options.pre_on(self, event)
    # ----------------------------------------------------------------------------------
    def pre_off(self,event):
        GUI_Options.pre_off(self, event)
    # ----------------------------------------------------------------------------------
    def onHelp(self, event):
        GUI_Options.onHelp(self, event)
    # ----------------------------------------------------------------------------------
    def log(self, input):
        LogFuncs.log(self,input)
    # ----------------------------------------------------------------------------------
    def readConfig(self):
        ReadConfigFiles.readConfig(self)
    # ----------------------------------------------------------------------------------
    def Noffset(self,event):
        Offset.Noffset(self,event)
    #  # ----------------------------------------------------------------------------------

    def timeN(self,event):
        Offset.timeN(self,event)
    # # ----------------------------------------------------------------------------------

    def Woffset(self,event):
        Offset.Woffset(self,event)
	#  # ----------------------------------------------------------------------------------

    def timeW(self,event):
        Offset.timeW(self,event)
    # # ----------------------------------------------------------------------------------

    def Eoffset(self,event):
        Offset.Eoffset(self,event)
	# ----------------------------------------------------------------------------------

    def timeE(self,event):
        Offset.timeE(self,event)
    # ----------------------------------------------------------------------------------

    def Soffset(self,event):
        Offset.Soffset(self,event)
	# ----------------------------------------------------------------------------------

    def timeS(self,event):
        Offset.timeS(self,event)
    # # ----------------------------------------------------------------------------------

    def checkhandPaddle(self):
        """
        Tell the server to check for a handpaddle signal. This is done client side due to stability issues
        in multithreaded server application. GTCC matched rate should be a command every 10 ms, will push down to that
        if testing shows the server can handle it.

            Args:
                None

            Returns:
                None
        """
        time.sleep(2.0)
        while True:
            #self.protocol.sendCommand("paddle")
            self.command_queue.put("checkhandPaddle")
            time.sleep(0.123)

    # ----------------------------------------------------------------------------------

    def focusIncPlus(self,event):
        Focus.focusIncPlus(self,event)
    # # ----------------------------------------------------------------------------------

    def focusIncNeg(self,event):
        Focus.focusIncNeg(self,event)
    # # ----------------------------------------------------------------------------------

    def setfocus(self,event):
        Focus.setfocus(self,event)
    # # ----------------------------------------------------------------------------------

    def haltmotion(self,event):
        SlewVelmeasure.haltmotion(self,event)
    # ----------------------------------------------------------------------------------

    def toggletracksend(self,evt):
        '''
        Passes a command to the telescope to toggle tracking.

            Args:
                evt: handler to allow function to be tethered to a wx widget. Tethered to the "Start Tracking" button in the telescope control tab.

            Returns:
                None
        '''
        RATR=self.control.currentRATRPos.GetLabel()
        #DECTR=self.control.currentDECTRPos.GetLabel()
        print RATR
        if str(RATR)=='Unknown':
        	dlg = wx.MessageDialog(self,"Please input a valid RA tracking rate. Range is between -10.0 and 25.0. Use 15.04108 if unsure.", "Error", wx.OK|wx.ICON_ERROR)
        	dlg.ShowModal()
        	dlg.Destroy()
        	return
        if self.telescope_status.get('tracking')==False:
            self.sb.SetStatusText('Tracking: True',0)
            #self.protocol.sendCommand("track on "+str(self.dict.get('RAtrackingRate')))
            self.command_queue.put("track on "+str(self.dict.get('RAtrackingRate')))
            self.control.trackButton.SetLabel('Stop Tracking')
            self.control.trackButton.SetBackgroundColour('Light Steel Blue')
        if self.telescope_status.get('tracking')==True:
            self.sb.SetStatusText('Tracking: False',0)
            #self.protocol.sendCommand("track off")
            self.command_queue.put("track off")
            self.control.trackButton.SetLabel('Start Tracking')
            self.control.trackButton.SetBackgroundColour('Light Slate Blue')
        self.telescope_status['tracking']= not self.telescope_status.get('tracking')
        return

    # ----------------------------------------------------------------------------------
    def inputcoordSorter(self,ra,dec,epoch):
        Coordinates.inputcoordSorter(self,ra,dec,epoch)
    # # ----------------------------------------------------------------------------------

    def coordprecess(self,coords,epoch_now,epoch):
        Coordinates.coordprecess(self,coords,epoch_now,epoch)
    # # ----------------------------------------------------------------------------------

    def startSlew(self,event):
        SlewVelmeasure.startSlew(self,event)
    # # ----------------------------------------------------------------------------------

    def timeSlew(self,event):
        SlewVelmeasure.timeSlew(self,event)
    # # ----------------------------------------------------------------------------------
    def velwatch(self, secondary_slew = False, data=None):
        SlewVelmeasure.velwatch(self, secondary_slew = Galse, data=None)
    # # ----------------------------------------------------------------------------------

    def velmeasure(self,msg):
        SlewVelmeasure.velmeasure(self,msg)
    # # ----------------------------------------------------------------------------------

    def velmeasureSS(self,msg):
        SlewVelmeasure.velmeasureSS(self,msg)
    # # ----------------------------------------------------------------------------------

    def checkslew(self):
        SlewVelmeasure.checkslew(self)
    # # ----------------------------------------------------------------------------------
    def slewbuttons_on(self,bool,track):
        SlewVelmeasure.slewbuttons_on(self,bool,track)
    # # ----------------------------------------------------------------------------------
    def slewbutton_toggle(self):
        SlewVelmeasure.slewbutton_toggle(self)
    # # ----------------------------------------------------------------------------------
    def getstatus(self):
        LogFuncs.getstatus(self)
    # # ----------------------------------------------------------------------------------
    def watchstatus(self):
        LogFuncs.watchstatus(self)
    # # ----------------------------------------------------------------------------------
    def displaystatus(self):
        ReadConfigFiles.displaystatus(self)
    # ----------------------------------------------------------------------------------
    def set_target(self, event):
        """
        Take a selected item from the list and set it as the current target.
        Load it into the control tab and load it's coordinates into the guider control tab for finder charts
        This is slow, getFocusedItem might be lagging

            Args:
                event: handler to allow function to be tethered to a wx widget. Tethered to the "Select as Current
                Target" button in the target list tab.
            Returns:
                None
        """
        sel_item=self.target.targetList.GetFocusedItem()

        name=str(self.target.targetList.GetItem(sel_item,col=0).GetText())
        input_ra=str(self.target.targetList.GetItem(sel_item,col=1).GetText())
        input_dec=str(self.target.targetList.GetItem(sel_item,col=2).GetText())
        input_epoch=str(self.target.targetList.GetItem(sel_item,col=3).GetText())
        mag = str(self.target.targetList.GetItem(sel_item,4).GetText())

        #print name, ra, dec, epoch
        self.control.targetNameText.SetValue(name)
        self.control.targetRaText.SetValue(input_ra)
        self.control.targetDecText.SetValue(input_dec)
        self.control.targetEpochText.SetValue(input_epoch)
        self.control.targetMagText.SetValue(mag)
        #self.init.onTargetButton.Enable()
        self.control.pointButton.Enable()

        self.log("Current target is '"+name+"'")

        #Load Finder Chart
        #thread.start_new_thread(self.LoadFinder,(input_ra,input_dec,input_epoch,))
        #return

    # ----------------------------------------------------------------------------------
    def LoadFinder(self, input_ra,input_dec,input_epoch):
        PlotFuncs.LoadFinder(self,input_ra,input_dec,input_epoch)
    # ----------------------------------------------------------------------------------
    def on_pick(self,event):
        """
        Get pixel coordinates and rotate periscope angle on click.
            Args:
                event: handler to interface with interactive plot
            Returns:
                None
        """
        artist = event.artist
        if isinstance(artist, AxesImage):
            im = artist
            A = im.get_array()
            center_x=A.shape[0]/2.0
            center_y=A.shape[1]/2.0
            mouseevent = event.mouseevent
            self.x = mouseevent.xdata
            self.y = mouseevent.ydata
            #print('onpick4 image', self.x,self.y, center_x, center_y)
            dx=self.x-center_x
            dy=self.y-center_y
            rho = np.sqrt(dx**2 + dy**2)
            phi = np.arctan2(dy, dx)
            phi_or=(phi*180./np.pi)-90
            print A.shape,rho,phi_or
	    if self.telescope_status.get('guider_rot')==False:
                thread.start_new_thread(self.Rotate,(phi_or,))

    # ----------------------------------------------------------------------------------
    def populateCurrPos(self,event):
        ListFuncs.populateCurrPos(self,event)
    # ----------------------------------------------------------------------------------
    def addToList(self,event):
        ListFuncs.addToList(self,event)
    # # ----------------------------------------------------------------------------------
    def readToList(self,event):
        ListFuncs.readToList(self, event)
    # # ----------------------------------------------------------------------------------
    # def refreshList(self,event):
    #     ListFuncs.refreshList(self,event)
    # # ------------------w----------------------------------------------------------------
    def removeFromList(self,event):
        ListFuncs.removeFromList(self,event)
    # # ----------------------------------------------------------------------------------
    def FinderOpen(self,event):
        FinderFuncs.FinderOpen(self,event)
    # # ----------------------------------------------------------------------------------
    def GenerateFinder(self, target, survey='DSS', fov_radius=18*u.arcmin,
                           log=False, ax=None, grid=False, reticle=False,
                           style_kwargs=None, reticle_style_kwargs=None):
        FinderFuncs.GenerateFinder(self, target, survey='DSS', fov_radius=18*u.arcmin,
                               log=False, ax=None, grid=False, reticle=False,
                               style_kwargs=None, reticle_style_kwargs=None)
    # # ----------------------------------------------------------------------------------
    #
    def plotFinder(self, ax, hdu, grid, log, fov_radius,reticle,style_kwargs, reticle_style_kwargs, target_name):
        FinderFuncs.plotFinder(self, ax, hdu, grid, log, fov_radius,reticle,style_kwargs, reticle_style_kwargs, target_name)
    # # ----------------------------------------------------------------------------------
    def timeout(self,t,value):
        FinderFuncs.timeout(self,t,value)
    # # ----------------------------------------------------------------------------------
    def ExportOpen(self,event):
        """
        Launch Export Window. Pull in current target list to window.
            Args:
                event: handler to allow function to be tethered to a wx widget. Tethered to the "Retrieve List" button in the target list tab.
            Returns:
                None
        """
        self.window=TargetExportWindow(self)
        self.window.Show()

        self.window.list=[]

        self.listrange=np.arange(0,self.target.targetList.GetItemCount())

        for row in self.listrange:
            name=self.target.targetList.GetItem(itemId=row, col=0).GetText()
            ra=self.target.targetList.GetItem(itemId=row, col=1).GetText()
            dec=self.target.targetList.GetItem(itemId=row, col=2).GetText()
            epoch=self.target.targetList.GetItem(itemId=row, col=3).GetText()
            vmag=self.target.targetList.GetItem(itemId=row, col=4).GetText()

            objectdata=str(name)+';'+str(ra)+';'+str(dec)+';'+str(epoch)+';'+str(vmag)
            self.window.list.append(objectdata)


        self.export_active=True


    # ----------------------------------------------------------------------------------
    def dyn_airmass(self,tgt,obs,count):
        PlotFuncs.dyn_airmass(self,tgt,obs,count)
    # ----------------------------------------------------------------------------------
    def target_plot(self,event):
        PlotFuncs.target_plot(self,event)
    # ----------------------------------------------------------------------------------
    def airmass_plot(self,event):
        PlotFuncs.airmass_plot(self,event)
    # ----------------------------------------------------------------------------------
    def setTelescopeZenith(self, event):
        TelescopePosition.setTelescopeZenith(self,event)
    # # ----------------------------------------------------------------------------------
    def setTelescopePosition(self,event):
        TelescopePosition.setTelescopePosition(self,event)
    # # ----------------------------------------------------------------------------------
    def parkscope(self,event):
        TelescopePosition.parkscope(self,event)
    # # ----------------------------------------------------------------------------------
    def coverpos(self,event):
        TelescopePosition.coverpos(self,event)
    # # ----------------------------------------------------------------------------------
    def pointing(self,event):
        TelescopePosition.pointing(self,event)
    # # ----------------------------------------------------------------------------------
    def setRATrackingRate(self,event):
        SetParams.setRATrackingRate(self,event)
    # # ----------------------------------------------------------------------------------
    def resetRATrackingRate(self,event):
        SetParams.resetRATrackingRate(self,event)
    # # ----------------------------------------------------------------------------------
    def setmaxdRA(self,event):
        SetParams.setmaxdRA(self,event)
    # # ----------------------------------------------------------------------------------
    def setmaxdDEC(self,event):
        SetParams.setmaxdDEC(self,event)
    # # ----------------------------------------------------------------------------------
    def onInit(self,event):
        ReadConfigFiles.onInit(self,event)
    # ----------------------------------------------------------------------------------
    def watchcommand(self):
        """
        Watch self.command_queue and send commands to the server in a first-in first-out basis
        Args:
            None
        Returns:
            None
        """
        while True:
            #print self.command_queue.qsize()
            #print self.command_queue.empty()
            if not self.command_queue.empty():
                command = self.command_queue.get()
                #print "Queue Size: ",self.command_queue.qsize()
                print command
                if self.command_queue.qsize() >= 10:
                    print "WARNING: Backlog of commands present. Consider Restarting Application."
                if self.telescope_status.get("connectState") == True:

                    if command == "velmeasureSS":
                        d = self.protocol.sendCommand("velmeasure;")
                        d.addCallback(self.velmeasureSS)
                        self.command_queue.task_done()
                    elif command == "velmeasure":
                        d = self.protocol.sendCommand("velmeasure;")
                        d.addCallback(self.velmeasure)
                        self.command_queue.task_done()
                    elif command == "shutdown":
                        d= self.protocol.sendCommand("shutdown;")
                        d.addCallback(self.quit)
                        self.command_queue.task_done()
                    elif command == "checkhandPaddle":
                        self.protocol.sendCommand("paddle;")
                        self.command_queue.task_done()
                    else:
                        self.protocol.sendCommand(command+";")
                        self.command_queue.task_done()
            time.sleep(0.0137)
    # ----------------------------------------------------------------------------------
    def logstatus(self):
        LogFuncs.logstatus(self)
    # ----------------------------------------------------------------------------------
    def timer(self):
        TimeFuncs.timer(self)
    # ----------------------------------------------------------------------------------
    def timeCalc(self):
        TimeFuncs.timeCalc(self)
    # ----------------------------------------------------------------------------------
    def getFocus(self,event):
        Focus.getFocus(self,event)

class TCCClient(protocol.ClientFactory):
    # ----------------------------------------------------------------------------------
    def __init__(self, gui):
        self.gui = gui
        self.protocol = DataForwardingProtocol
    # ----------------------------------------------------------------------------------
    def clientConnectionLost(self, transport, reason):
        reactor.stop()
    # ----------------------------------------------------------------------------------
    def clientConnectionFailed(self, transport, reason):
        reactor.stop()
###########################################################################################
if __name__=="__main__":
	#global pipe
	try:
  		app = wx.App(False)
  		app.frame = TCC()
  		app.frame.Show()
  		reactor.registerWxApp(app)
  		pipe= subprocess.Popen("../TelescopeServer/TelescopeServer",shell=True, preexec_fn=os.setsid)
  		time.sleep(2.0)
  		reactor.connectTCP('localhost',5501,TCCClient(app.frame))
  		reactor.run()
  		app.MainLoop()
	except KeyboardInterrupt:
		os.killpg(os.getpgid(pipe.pid),signal.SIGTERM)
		sys.exit(0)
	except ValueError:
		pass
