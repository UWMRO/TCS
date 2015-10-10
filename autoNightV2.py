#! /user/bin/env python

__author__ = "Joseph Huehnerhoff"
__date__="Date: 2010/10/13"
"""
A GUI intended to automate many 3.5m Night Log tasks

Usage:  arch -i386 python2.6 autoNight.py
Build:  rm -rf build dist
        python setup.py py2app -p wx -p email

Updates:
10/17/2010  BetaV1.3   improved error handling for inputDat() including better error messages.  Changed getDate() to include the provision for opening file in morning.  Fixed error where there was discrepency between number date and day name.
10/20/2010  BetaV1.4  changed TUI version.  Verified new weather input file.
10/25/10    BetaV1.5  modified halfNight calculator. Change tspec and echelle names when input as ARCES or TripleSpec.  Recgnize EN01 program.  Determines quarter in findVer(). Added padding to output to line up spaces.
11/04/10    BetaV1.6  fixed quarter determination statements.
11/11/10    BetaV1.7  Added gedit support of linux, error handling of non string types in mac.
2/22/11     BetaV1.8  Changed to accept UTC time
5/2/11      BetaV1.9  Changed spacing of ACTUAL and Observing Specialist, made exception for eAur program
11/5/10     BetaV2.0  started to rewrite code in wxPython
5/7/11      BetaV2.0  Updated
5/13/11     V2.1      Added debug support, changed gridsizer to support 8 programs
6/1/11      V2.2      Fixed end of month bug
8/22/11     V2.3      Added automatic TUI version recognition
9/22/11     V2.4      New ObsSpec Added, tcc version config file and recognition
10/02/11    V2.5      Added email support
10/03/11    V2.6      updated username email list, added support for special programs and multiple observer programs
03/07/12    V2.7      increased error checking for program id
08/28/12    V2.8      added new obspec A.Shugart.
5/29/13     V2.9      Added config file for obs-spec names
"""

import wx, time, urllib, os, re, pickle, linecache,datetime, webbrowser, string,sys,thread, smtplib
from email.MIMEText import MIMEText
if sys.platform=='linux2':
    import wx.lib.agw.hyperlink as test
else:
    import wx.lib.hyperlink as test

class Log(wx.Frame):
    global debug
    global oneVar
    global twoVar
    global threeVar
    global fourVar
    oneVar=0
    twoVar=0
    threeVar=0
    fourVar=0

    
    def __init__(self,parent,title):
        wx.Frame.__init__(self,parent,title=title,size=(-1,-1))
        #color=(230,221,213,255)
        color=(0,0,255,10)
        self.SetBackgroundColour(color)
        if sys.platform=="linux2":
            self.ft=wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL)
        else:
            self.ft=wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL)
        self.debug='no'
        bugt='08'
        self.webbug='http://35m-schedule.apo.nmsu.edu/2012-02-10.1/html/days/2012-03-%s.html' % bugt
        self.debugdate=['03',bugt,'2012','Thursday','March']
        peeps=len(self.findProID())
        self.CreateStatusBar()
        filemenu=wx.Menu()
        menuAbout=filemenu.Append(wx.ID_ANY, "&About\tCtrl+A","Information about this program")
        self.Bind(wx.EVT_MENU,self.onAbout,menuAbout)

        filemenu.AppendSeparator()
        menuExit=filemenu.Append(wx.ID_ANY,'&Exit\tCtrl+Q','Terminate the program',)
        self.Bind(wx.EVT_MENU,self.onExit,menuExit)

        subMenu=wx.Menu()

        menuSave=subMenu.Append(wx.ID_SAVE, '&Save\tCtrl+S','Save the file without showing displaying text')
        self.Bind(wx.EVT_MENU, self.saveNight,menuSave)

        menuSaveAs=subMenu.Append(wx.ID_ANY, '&Save As\tCtrl+Alt+S','Save file with name as specified in pop up menu')
        self.Bind(wx.EVT_MENU, self.saveAs, menuSaveAs)

        menuGenerate=subMenu.Append(wx.ID_ANY,'&Generate\tCtrl+G', 'Generate the Night Log and display it in text editor')
        self.Bind(wx.EVT_MENU, self.generate, menuGenerate)

        menuEmail=subMenu.Append(wx.ID_ANY,'&Email\tCtrl+E', 'Email Night Log')
        self.Bind(wx.EVT_MENU, self.email, menuEmail)

        subMenu.AppendSeparator()
        menuWeather=subMenu.Append(wx.ID_ANY,'&Get Weather Data\tCtrl+W','Input data from file weather.txt')
        self.Bind(wx.EVT_MENU,self.getWeather,menuWeather)

        subMenu.AppendSeparator()
        menuFocus=subMenu.Append(wx.ID_ANY,'&Get Focus Lines\tCtrl+F','Input specified lines from nfocus.txt')
        self.Bind(wx.EVT_MENU,self.getFocus, menuFocus)
        
        addMenu=wx.Menu()
        menuAdd1=addMenu.Append(wx.ID_ANY,'&Add 1\tCtrl+Alt+1','Add set of lines after first observing program')
        self.Bind(wx.EVT_MENU,self.addOne,menuAdd1)

        menuAdd2=addMenu.Append(wx.ID_ANY,'&Add 2\tCtrl+Alt+2','Add set of lines after first observing program')
        self.Bind(wx.EVT_MENU,self.addTwo,menuAdd2)
        
        if peeps >2:
            menuAdd3=addMenu.Append(wx.ID_ANY,'&Add 3\tCtrl+Alt+3','Add set of lines after first observing program')
            self.Bind(wx.EVT_MENU,self.addThree,menuAdd3)
        if peeps>3:
            menuAdd4=addMenu.Append(wx.ID_ANY,'&Add 4\tCtrl+Alt+4','Add set of lines after first observing program')
            self.Bind(wx.EVT_MENU,self.addFour,menuAdd4)

        menuBar=wx.MenuBar()
        menuBar.Append(filemenu, '&File')
        menuBar.Append(subMenu, '&Submit')
        menuBar.Append(addMenu,'&Add')
        self.SetMenuBar(menuBar)       
        
        timearr=self.getDate()
        
        self.APO=wx.StaticText(self,label="Apache Point Observatory\n"\
                               "3.5m Telescope Night Log",size=(175,-1))  
        self.APO.SetFont(self.ft)

        self.link=test.HyperLinkCtrl(self)
        self.link.SetURL(URL="http://35m-schedule.apo.nmsu.edu/%s/html/days/%s-%s-%s.html" % (self.findVer(),timearr[2],timearr[0],timearr[1]))
        self.link.SetFont(self.ft)
      

        self.link.SetLabel(label="%s, %s %s, %s" % (timearr[3],timearr[4], timearr[1]
, timearr[2]))

        self.userHeader=wx.StaticText(self,label="                                                                ACTUAL\n"\
                       " ASTRONOMER               OBSERVER(S)              INST      START  FINISH\n",size=(575,-1))
        self.userHeader.SetFont(self.ft)
        
        self.usastr0=wx.TextCtrl(self,size=(180,-1))
        self.usastr0.SetFont(self.ft)
        self.usobs0=wx.TextCtrl(self,size=(180,-1))
        self.usobs0.SetFont(self.ft)
        self.usinst0=wx.TextCtrl(self,size=(75,-1))
        self.usinst0.SetFont(self.ft)
        self.usstart0=wx.TextCtrl(self,size=(50,-1))
        self.usstart0.SetFont(self.ft)
        self.usend0=wx.TextCtrl(self,size=(50,-1))
        self.usend0.SetFont(self.ft)

        self.usastr1=wx.TextCtrl(self,size=(180,-1))
        self.usastr1.SetFont(self.ft)
        self.usobs1=wx.TextCtrl(self,size=(180,-1))
        self.usobs1.SetFont(self.ft)
        self.usinst1=wx.TextCtrl(self,size=(75,-1))
        self.usinst1.SetFont(self.ft)
        self.usstart1=wx.TextCtrl(self,size=(50,-1))
        self.usstart1.SetFont(self.ft)
        self.usend1=wx.TextCtrl(self,size=(50,-1))
        self.usend1.SetFont(self.ft)

        if peeps >2: 
            self.usastr2=wx.TextCtrl(self,size=(180,-1))
            self.usastr2.SetFont(self.ft)
            self.usobs2=wx.TextCtrl(self,size=(180,-1))
            self.usobs2.SetFont(self.ft)
            self.usinst2=wx.TextCtrl(self,size=(75,-1))
            self.usinst2.SetFont(self.ft)
            self.usstart2=wx.TextCtrl(self,size=(50,-1))
            self.usstart2.SetFont(self.ft)
            self.usend2=wx.TextCtrl(self,size=(50,-1))
            self.usend2.SetFont(self.ft)

        if peeps >3: 
            self.usastr3=wx.TextCtrl(self,size=(180,-1))
            self.usastr3.SetFont(self.ft)
            self.usobs3=wx.TextCtrl(self,size=(180,-1))
            self.usobs3.SetFont(self.ft)
            self.usinst3=wx.TextCtrl(self,size=(75,-1))
            self.usinst3.SetFont(self.ft)
            self.usstart3=wx.TextCtrl(self,size=(50,-1))
            self.usstart3.SetFont(self.ft)
            self.usend3=wx.TextCtrl(self,size=(50,-1))
            self.usend3.SetFont(self.ft)

        self.schedHalf=wx.StaticText(self,label="   INST       SCHEDULED     WEATH     EQUIP      OBS     NOT USED\n"\
                         " I/ROW/DN   START  FINISH   D    B    D    B    D    B    D    B\n",size=(500,-1))
        self.schedHalf.SetFont(self.ft)
       
        self.sc1=wx.TextCtrl(self,style=wx.TE_MULTILINE,size=(500,20))
        self.sc1.SetFont(self.ft)
        self.sc2=wx.TextCtrl(self,style=wx.TE_MULTILINE,size=(500,20))
        self.sc2.SetFont(self.ft)
        if peeps>2:
            self.sc3=wx.TextCtrl(self,style=wx.TE_MULTILINE,size=(-1,20))
            self.sc3.SetFont(self.ft)
        if peeps>3:
            self.sc4=wx.TextCtrl(self,style=wx.TE_MULTILINE,size=(-1,20))
            self.sc4.SetFont(self.ft)
        self.infoBlock=wx.TextCtrl(self,style=wx.TE_MULTILINE|wx.TE_READONLY|wx.NO_BORDER,size=(575,50))
        self.infoBlock.SetFont(self.ft)
        self.infoText=wx.TextCtrl(self,style=wx.TE_MULTILINE|wx.TE_READONLY|wx.NO_BORDER,size=(-1,65))
        self.infoText.SetFont(self.ft)

        self.actLog=wx.StaticText(self,label="             ------------- ACTIVITY LOG --------------")
        self.actLog.SetFont(self.ft)

        self.obsspec=wx.StaticText(self, label="Observing Specialist: %s" % self.findUser()[0])
        self.obsspec.SetFont(self.ft)
        self.actText=wx.TextCtrl(self,style=wx.TE_MULTILINE|wx.RAISED_BORDER,size=(-1,150))
        self.actText.SetFont(self.ft)
        
        self.fail=wx.StaticText(self,label="                    ------- FAILURE LOG -------\n"\
                        "PROG   INST   FAILURE MODE     TIME\n"\
                        "    (SEDFNVOG)   TI/SHU    START  FINISH  DESCRIPTION",size=(500,-1))
        self.fail.SetFont(self.ft)
        self.failLog=wx.TextCtrl(self,style=wx.TE_MULTILINE,size=(-1,35))
        self.failLog.SetFont(self.ft)

        self.focus=wx.StaticText(self,label="            ---------------- FOCUS LOG ---------------\n"\
                         "Time  Instrument  Focus     Az  El  Temp Strc Prim  Sec  Air  filt  FWHM\n"\
                         "--------------------------------------------------------------------------")
        self.focus.SetFont(self.ft)
        self.focusLog=wx.TextCtrl(self,size=(-1,75),style=wx.TE_MULTILINE)
        self.focusLog.SetFont(self.ft)

        self.focusButton=wx.Button(self,label="Number of Focus Lines")
        self.Bind(wx.EVT_BUTTON,self.getFocus,self.focusButton)
        self.focusNum=wx.TextCtrl(self,size=(30,-1))
        self.focusNum.SetFont(self.ft)
        self.focusNum.AppendText('1')

        self.weathHead=wx.StaticText(self,label="                   ---------- Weather ---------")
        self.weathHead.SetFont(self.ft)
        self.weathText=wx.TextCtrl(self,size=(-1,75),style=wx.TE_MULTILINE)
        self.weathText.SetFont(self.ft)


        self.stat=wx.StaticText(self,label="                          TELESCOPE STATUS")
        self.stat.SetFont(self.ft)
        self.statTCC=wx.StaticText(self,label="Telescope drives operational. Current TCC version:")
        self.statTCC.SetFont(self.ft)
        self.statTCCText=wx.TextCtrl(self)
        self.statTCCText.SetFont(self.ft)
        self.statTUI=wx.StaticText(self,label='Current TUI version:')
        self.statTUI.SetFont(self.ft)
        self.statTUIText=wx.TextCtrl(self)
        self.statTUIText.SetFont(self.ft)

        self.findTCC()

        #make sizers
        self.topSizer=wx.BoxSizer(wx.VERTICAL)
        self.titleSizer=wx.BoxSizer(wx.VERTICAL)
        self.sizer=wx.BoxSizer(wx.VERTICAL)
        self.bottomSizer=wx.FlexGridSizer(rows=3,cols=2)
        self.focusSizer=wx.BoxSizer(wx.HORIZONTAL)

        self.sizer2=wx.FlexGridSizer(rows=10, cols=5)
        """if peeps ==3:
            self.sizer2=wx.FlexGridSizer(rows=4, cols=5)
        if peeps==4:
            self.sizer2=wx.FlexGridSizer(rows=10, cols=5)
       """

        self.titleSizer.Add(self.APO, 0,wx.ALIGN_CENTER)
        self.titleSizer.Add(self.link,0,wx.ALIGN_CENTER)

        self.sizer2.Add(self.usastr0,0,wx.EXPAND)
        self.sizer2.Add(self.usobs0,0,wx.EXPAND)
        self.sizer2.Add(self.usinst0,0,wx.EXPAND)
        self.sizer2.Add(self.usstart0,0)
        self.sizer2.Add(self.usend0,0)

        self.sizer2.Add(self.usastr1,0,wx.EXPAND)
        self.sizer2.Add(self.usobs1,0,wx.EXPAND)
        self.sizer2.Add(self.usinst1,0,wx.EXPAND)
        self.sizer2.Add(self.usstart1,0,wx.EXPAND)
        self.sizer2.Add(self.usend1,0,wx.EXPAND)      
      

        if peeps > 2:
            self.sizer2.Add(self.usastr2,0,wx.EXPAND)
            self.sizer2.Add(self.usobs2,0,wx.EXPAND)
            self.sizer2.Add(self.usinst2,0,wx.EXPAND)
            self.sizer2.Add(self.usstart2,0,wx.EXPAND)
            self.sizer2.Add(self.usend2,0,wx.EXPAND)      

        if peeps > 3:
            self.sizer2.Add(self.usastr3,0,wx.EXPAND)
            self.sizer2.Add(self.usobs3,0,wx.EXPAND)
            self.sizer2.Add(self.usinst3,0,wx.EXPAND)
            self.sizer2.Add(self.usstart3,0,wx.EXPAND)
            self.sizer2.Add(self.usend3,0,wx.EXPAND)      

        
        self.titleSizer.Add(self.userHeader,0,wx.ALIGN_LEFT)
        self.sizer.Add(wx.StaticLine(self),0,wx.ALL|wx.EXPAND,5)
        self.sizer.Add(self.infoBlock,0,wx.EXPAND)
        self.infoBlock.SetBackgroundColour(wx.Colour(230,221,213,255))

        
        self.sizer.Add(self.infoText,0,wx.EXPAND)
        self.infoText.SetBackgroundColour(wx.Colour(230,221,213,255))
        self.sizer.Add(wx.StaticLine(self),0,wx.ALL|wx.EXPAND,5)
        self.sizer.Add(self.schedHalf,0,wx.ALIGN_LEFT)
        self.sizer.Add(self.sc1,0,wx.EXPAND)
        self.sizer.Add(self.sc2,0,wx.EXPAND)
        if peeps >2:
            self.sizer.Add(self.sc3,0,wx.EXPAND)
        if peeps>3:
            self.sizer.Add(self.sc4,0,wx.EXPAND)
        self.sizer.Add(wx.StaticLine(self),0,wx.ALL|wx.EXPAND,5)
        self.sizer.Add(self.actLog,0,wx.ALIGN_LEFT)
        self.sizer.Add(self.obsspec,0,wx.ALIGN_LEFT)
        self.sizer.Add(self.actText,0,wx.EXPAND)
        self.sizer.Add(self.fail,0,wx.ALIGN_LEFT)
        self.sizer.Add(self.failLog,0,wx.EXPAND)
        self.sizer.Add(self.focus,0,wx.ALIGN_LEFT)
        self.sizer.Add(self.focusLog,0,wx.EXPAND)

        self.sizer.Add(self.focusSizer,0,wx.ALIGN_CENTER)
        self.focusSizer.Add(self.focusButton,0,wx.ALIGN_CENTER|wx.EXPAND)
        self.focusSizer.Add(self.focusNum,0,wx.ALIGN_CENTER|wx.EXPAND)  
        

        self.sizer.Add(self.weathHead,0,wx.ALIGN_LEFT)
        self.sizer.Add(self.weathText,0,wx.EXPAND)

        self.sizer.Add(self.stat,0,wx.ALIGN_LEFT)

        self.bottomSizer.Add(self.statTCC,0,wx.ALIGN_RIGHT)
        self.bottomSizer.Add(self.statTCCText,0)
        self.bottomSizer.Add(self.statTUI,0,wx.ALIGN_RIGHT)
        self.bottomSizer.Add(self.statTUIText,0,wx.ALIGN_LEFT)
        
        self.topSizer.Add(self.titleSizer,0,wx.ALIGN_CENTER|wx.EXPAND)
        self.topSizer.Add(self.sizer2,0,wx.EXPAND)
        self.topSizer.Add(self.sizer,0,wx.EXPAND)
        self.topSizer.Add(self.bottomSizer,0,wx.EXPAND)
  
        self.SetSizer(self.topSizer)
        self.SetAutoLayout(1)
        self.topSizer.Fit(self)
        self.topSizer.SetSizeHints(self)
    
        self.Show(True)
        thread.start_new_thread(self.halfNight,())
        thread.start_new_thread(self.inputDat,())
        thread.start_new_thread(self.findTUI,())

    def runInt(self):
        thread.start_new_thread(self.integrityCheck,())
        self.stop=0
      
    def integrityCheck(self):
        self.stop=0
        while self.stop==0:
            wx.CallAfter(self.saveText)
            time.sleep(600)

    def addOne(self,event):
        global oneVar
        self.usastr0b=wx.TextCtrl(self,size=(180,-1))
        self.usobs0b=wx.TextCtrl(self,size=(180,-1))
        self.usinst0b=wx.TextCtrl(self,size=(75,-1))
        self.usstart0b=wx.TextCtrl(self,size=(50,-1))
        self.usend0b=wx.TextCtrl(self,size=(50,-1))

        self.sizer2.Insert(5,self.usastr0b,0,wx.EXPAND)
        self.sizer2.Insert(6,self.usobs0b,0,wx.EXPAND)
        self.sizer2.Insert(7,self.usinst0b,0,wx.EXPAND)
        self.sizer2.Insert(8,self.usstart0b,0)
        self.sizer2.Insert(9,self.usend0b,0)
        self.sizer2.Layout()
        self.topSizer.Layout()
        oneVar=1

    def addTwo(self,event):
        global oneVar,twoVar
        self.usastr1b=wx.TextCtrl(self,size=(180,-1))
        self.usobs1b=wx.TextCtrl(self,size=(180,-1))
        self.usinst1b=wx.TextCtrl(self,size=(75,-1))
        self.usstart1b=wx.TextCtrl(self,size=(50,-1))
        self.usend1b=wx.TextCtrl(self,size=(50,-1))

        x=[10,11,12,13,14]
        if oneVar==1:
            x=[15,16,17,18,19]

        self.sizer2.Insert(x[0],self.usastr1b,0,wx.EXPAND)
        self.sizer2.Insert(x[1],self.usobs1b,0,wx.EXPAND)
        self.sizer2.Insert(x[2],self.usinst1b,0,wx.EXPAND)
        self.sizer2.Insert(x[3],self.usstart1b,0,wx.EXPAND)
        self.sizer2.Insert(x[4],self.usend1b,0,wx.EXPAND)
        self.sizer2.Layout()
        self.topSizer.Layout()
        twoVar= 1

    def addThree(self,event):
        global oneVar,twoVar,threeVar
        self.usastr2b=wx.TextCtrl(self,size=(180,-1))
        self.usobs2b=wx.TextCtrl(self,size=(180,-1))
        self.usinst2b=wx.TextCtrl(self,size=(75,-1))
        self.usstart2b=wx.TextCtrl(self,size=(50,-1))
        self.usend2b=wx.TextCtrl(self,size=(50,-1))

        x=[15,16,17,18,19]

        if oneVar==1 and twoVar==1:
            x=[25,26,27,28,29]
        elif oneVar==1 or twoVar==1:
            x=[25,26,27,28,29]

        self.sizer2.Insert(x[0],self.usastr2b,0,wx.EXPAND)

        self.sizer2.Insert(x[1],self.usobs2b,0,wx.EXPAND)

        self.sizer2.Insert(x[2],self.usinst2b,0,wx.EXPAND)
        self.sizer2.Insert(x[3],self.usstart2b,0)
        self.sizer2.Insert(x[4],self.usend2b,0)
        self.sizer2.Layout()
        self.topSizer.Layout()
        threeVar= 1

    def addFour(self,event):
        global oneVar,twoVar,threeVar
        self.usastr3b=wx.TextCtrl(self,size=(180,-1))
        self.usobs3b=wx.TextCtrl(self,size=(180,-1))
        self.usinst3b=wx.TextCtrl(self,size=(75,-1))
        self.usstart3b=wx.TextCtrl(self,size=(50,-1))
        self.usend3b=wx.TextCtrl(self,size=(50,-1))
        
        
        if oneVar==1 and twoVar==1:
            x=[35,36,37,38,39]
        elif oneVar==1 or twoVar==1:
            x=[45,46,47,48,49]
        elif oneVar==1 or twoVar==1 or threeVar==1:
            x=[55,56,57,58,59]
        else:
            x=[20,21,22,23,24]
        self.sizer2.Insert(x[0],self.usastr3b,0,wx.EXPAND)
        self.sizer2.AddGrowableCol(0)
        self.sizer2.Insert(x[1],self.usobs3b,0,wx.EXPAND)
        self.sizer2.AddGrowableCol(1)
        self.sizer2.Insert(x[2],self.usinst3b,0,wx.EXPAND)
        self.sizer2.Insert(x[3],self.usstart3b,0)
        self.sizer2.Insert(x[4],self.usend3b,0)
        self.sizer2.Layout()
        self.topSizer.Layout()
        fourVar=1

    def email(self,event):
        box=wx.TextEntryDialog(None, 'Please type your password:','Password', style=wx.OK|wx.TE_PASSWORD)
        if box.ShowModal()==wx.ID_OK:
            password=box.GetValue()
        try:
            day=self.getDate()
            smtp_server='xmail.apo.nmsu.edu'
            recipients='obs-report@apo.nmsu.edu'
            #recipients='jwhueh@apo.nmsu.edu'
            sender=self.emailAddr()
            subject='3.5m Night Log %s%s%s' %(day[2], day[0], day[1])
            file='/Users/%s/NightLogs/3.5mNightLog%s%s%s' % (os.getenv('USER'), day[2],day[0], day[1])
            f=open(file,'r')
            msg=MIMEText(f.read())
            f.close()
            msg['Subject']=subject
            msg['From']=sender
            msg['To']=recipients
        
            s=smtplib.SMTP_SSL()
            s.connect(smtp_server)
            s.login(sender,password)
            s.sendmail(sender,recipients,msg.as_string())
            s.close()
            dlg=wx.MessageDialog(self,'Email Sent','Completed',style=wx.OK|wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
        except smtplib.SMTPAuthenticationError:
            dlg=wx.MessageDialog(self,'password incorrect, try again','Fail',style=wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    def onMouse(self,event):
        self.SetFocus()

    def onAbout(self, event):
        dlg=wx.MessageDialog(self,'Automated Night Log Program\n'
                             'See web documentation:\n'
                             'web.nmsu.edu/~jwhueh/nightlog/nlogInst.html'
                             'Key Usage:'
                             '   command + Q    Quit\n'
                             '   command + S    Save file but not display\n'
                             '   command + G    Save file and display in textedit\n'
                             '   command + W    Get Weather data from desktop file weather.html\n'
                             '   command + F    Get specified number of focus lines\n'
                             '   command + E    Send Email\n'
                             '   command + alt + 1    Add line after first program\n'
                             '   command + alt + 2    Add line after second program\n'
                             '   command + alt + 3    Add line after third program\n'
                             '   command + alt + 4    Add line after fourth program\n'

                             ,'About', wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def onExit(self,event):
        self.Close()

    def emailAddr(self):
        user=os.getenv('USER')
        try:
            return user
        except:
            return ['None','None']

    def getDate(self):
        """This is designed to create the proper UT stamp to locate the corr
ect file.  A known problem is that the UT is advanced one day so if this scr
ipt is run after midnight in local time then the UT will be advanced one day
 too far and it will not be able to find the directory."""
        arr=[]
        dayarr=['Saturday','Sunday','Monday','Tuesday','Wednesday','Thursday','Friday']
        if self.debug =='yes':
            arr=self.debugdate
        else:
            
            hour = time.strftime('%H')
            month=time.strftime('%m')
            dayname=time.strftime('%A')
            monthname=time.strftime('%B')
            
            if time.strftime('%H') < '16':
                dayname=dayarr[int(time.strftime('%w'))]
                day = '%s' % str(int(time.strftime('%d'))-1)
                #print day
                if day == '0':
                    month,day,monthname=self.EOM(month)
                if int(day) < 10:
                    day= '0%s' % day
                else:
                    day=day
            else:
                day = time.strftime('%d')
                
            arr.append(month)
            arr.append(day)
            arr.append(time.strftime('%Y'))
            arr.append(dayname)
            arr.append(monthname)
        #print arr
        return  arr

    def EOM(self,month):
        if month=='01':
            return '12','31','December'
        if month=='02':
            return '01','31','January'
        if month=='03':
            return '02','28','February'
        if month=='04':
            return '03','31','March'
        if month=='05':
            return '04','30','April'
        if month=='06':
            return '05','31','May'
        if month=='07':
            return '06','30','June'
        if month=='08':
            return '07','31','July'
        if month=='09':
            return '08','31','August'
        if month=='10':
            return '09','30','September'
        if month=='11':
            return '10','31','October'
        if month=='12':
            return '11','30','Novermber'

    #return the current version of the schedule for the html address
    def findVer(self):
        time=self.getDate()
        month=time[0]
        if month >= '10':
            quarter=time[2]+'Q4'
        elif month>='07':
            quarter=time[2]+'Q3'
        elif month>='04':
            quarter=time[2]+'Q2'
        elif month>='01':
            quarter=time[2]+'Q1'
        web='http://35m-schedule.apo.nmsu.edu/%s.shtml' % quarter
        sock=urllib.urlopen(web)
        htmlVer = sock.readlines()
        sock.close()
        h=htmlVer[0]
        h=h[:-9]
        h=h[57:]
        return h
    
    def findTUI(self):
        web='http://www.apo.nmsu.edu/arc35m/TUIdownloads_ARC35m.html'
        sock=urllib.urlopen(web)
        tuiVer = sock.readlines()
        sock.close()
        for line in tuiVer:
            if re.search('<p>The current version',line):
                tui=line[len(line)-7:len(line)-2]
        self.statTUIText.AppendText(tui)
        return tui

    def findTCC(self):
        f=open('/Users/Shared/autoNight.dat','r')
        for index,line in enumerate(f.readlines()):
            if index==1:
                self.statTCCText.AppendText(str(line))
        f.close()

    def getFocus(self,event):
        num=self.focusNum.GetValue()
        files=os.popen('tail -%s /Users/%s/nfocus.txt' % (num, os.getenv('USER')), 'r')
        for l in files:
            self.focusLog.AppendText(l)

    def saveAs(self,event):
        filename=tkFileDialog.asksaveasfilename()
        output(filename)

    def saveNight(self,event):
        day=self.getDate()
        file='/Users/%s/NightLogs/3.5mNightLog%s%s%s' % (os.getenv('USER'), time
.strftime('%Y'),time.strftime('%m'), day[1])
        self.output(file)

    def saveText(self):
        day=self.getDate()
        file='/Users/%s/NightLogs/3.5mNightLog%s%s%s' % (os.getenv('USER'), time
.strftime('%Y'),time.strftime('%m'), day[1])
        self.output(file)

    def findUser(self):
        user_arr=[]
        user=os.getenv('USER')
        f_in=open('/Users/Shared/autoNightUsers.dat','r')
        for line in f_in:
            l=line.rstrip('\n').split('\t')
            user_arr.append(l)
        f_in.close()
        print user_arr
        for u in user_arr:
            if user==u[0]:
                name=u[1].split(' ')
                return [name[0][0:1]+'.'+name[1],u[1]]
        return ['Obs Spec','Obs Spec']

        """Get PI and Observer and inst to input in form.  This section tends to cause the most problem.  Rudimentary error handling seems to help.  If Observer cannot be found it places the PI as the observer."""
    def inputDat(self):
        arr=self.proDat()
        try:
            n1=arr[0][0].split()
            self.usastr0.AppendText(n1[0][0:1] + '.' + n1[1].rstrip(',')) 
            self.usastr0.SetFont(self.ft)
            n1o=arr[0][1].split()
            self.usobs0.AppendText(n1o[0][0:1] + '.' + n1o[1].rstrip(','))
        except:
            try:
                n1o=arr[0][1].split()
                self.usobs0.AppendText(n1o[0][0:1] + '.' + n1o[1].rstrip(','))
            except:
                print 'error usobs0, check proposal for first observing program'
        try:
            self.usinst0.AppendText(arr[0][2])
        except:
            print 'error usinst0, check proposal for first observing program instrument'
        try:
            n2=arr[1][0].split()
            self.usastr1.AppendText(n2[0][0:1] + '.' + n2[1].rstrip(','))
            n2o=arr[1][1].split()
            self.usobs1.AppendText(n2o[0][0:1] + '.' + n2o[1].rstrip(','))
        except:
            try:
                n2o=arr[1][0].split()
                self.usobs1.AppendText(n2o[0][0:1] + '.' + n2o[1].rstrip(','))
            except IndexError:
                print 'error usobs1, check proposal for second observing program'
        try:    
            self.usinst1.AppendText(arr[1][2])
        except :
            print 'error usinst1, check  proposal for second observing program instrument'
        peeps= self.findProID()
        if len(peeps) > int(2):
            try:
                n3=arr[2][0].split()
                self.usastr2.AppendText(n3[0][0:1] + '.' + n3[1].rstrip(',')) 
                n3o=arr[2][1].split()
                self.usobs2.AppendText(n3o[0][0:1] + '.' + n3o[1].rstrip(','))
            except:
                try:
                    n3o=arr[2][0].split()
                    self.usobs2.AppendText(n3o[0][0:1] + '.' + n3o[1].rstrip(','))

                except:
                    print 'error usbos2, or usinst2,check proposal for third observing program '
            try:
                self.usinst2.AppendText(arr[2][2])
            except:
                print 'error usinst2'

        if len(peeps) > int(3):
            try:
                n4=arr[3][0].split()
                self.usastr3.AppendText(n4[0][0:1] + '.' + n4[1].rstrip(',')) 
                n4o=arr[3][1].split()
                self.usobs3.AppendText(n4o[0][0:1] + '.' + n4o[1].rstrip(','))
            except:
                try:
                    n4o=arr[3][0].split()
                    self.usobs3.AppendText(n4o[0][0:1] + '.' + n4o[1].rstrip(','))
                except:
                    print 'error check proposal for fourth observing program'
            try:
                self.usinst3.AppendText(arr[3][2])
            except:
                print 'error usinst3, check  proposal for fourth observing program instrument'
        self.topSizer.Layout()

    def proDat(self):
        version=self.findVer()
        modarr=[]
        fin=[]
        arr= self.findProID()
        for item in arr:
            startarr=[]
            modarr=[]
            if item == 'EN01':
                startarr.append('PI: Mark Klaene\n')
                startarr.append('')
                startarr.append('X')
                startarr.append('O')
            web='http://35m-schedule.apo.nmsu.edu/%s/proposals/%s.txt' % (version,item)
            print web
            sock=urllib.urlopen(web)
            htmlProp = sock.readlines()
            sock.close()
            next=0
            try:
                for line in htmlProp:
                    if  re.search('Tom Murphy',line) !=None:
                        startarr=['PI: Tom Murphy','OBSERVER: Russet McMillan','INSTRUMENT: APOLLO']
                    elif re.match('PI:',line) != None:
                        if len(line)<=4:
                            next=1
                        else:
                            startarr.append(line)
                    elif next==1:
                        startarr.append(line)
                        next=0
                    elif re.match('OBSERVER',line) != None:
                        if len(line)<=14:
                            next=2
                        else:
                            user=line.split(',')
                            startarr.append(user[0])
                    elif next==2:
                        startarr.append(line)
                        next=0
                    elif re.match('INSTRUMENT',line) != None:
                        if len(line)<=14:
                            next=3
                        else:
                            startarr.append(line)
                    elif next==3:
                        startarr.append(line)
                        next=0
                    if  re.search('William Ketzeback',line) !=None:
                        startarr=['PI: William Ketzeback','OBSERVER: %s' % self.findUser(),'INSTRUMENT: ECHELLE/TSPEC'] 
            except:
                print 'problem line 782'
            print startarr
            try:
                for item in startarr:
                    t=item.lstrip('PIOBSERVER(S)INSTRUMENTOBSERVINGMODE:\t').rstrip('\n')
                    if re.search('ARCES', t)!=None:
                        t='ECHELLE'
                    if re.search('Triplespec',t)!=None:
                        t='TSPEC'
                    if re.search('DIS',t)!=None:
                        t='DIS'
                    t=t.lstrip('" "')
                    modarr.append(t.replace('\t',""))
                    if  re.search('William Ketzeback',startarr[0]) !=None:
                        modarr=['William Ketzeback',self.findUser()[1],'ECHELLE/TSPEC']
            except:
                print 'problem line 797'
            fin.append(modarr)
        return fin

    def timeData(self,day):
        version=self.findVer()
        arr=[]
        arrb=[]
        dict=['TR','TD','<B>','<','>','TH','a href','align=','left','/','TABLE','HTML','BODY','\n','BR','border=1',"'"] 
        timearr=self.getDate()
        if self.debug=='yes':
            web=self.webbug
        else:
            web='http://35m-schedule.apo.nmsu.edu/%s/html/days/%s-%s-%s.html' % (version,timearr[2],timearr[0],timearr[1])
        sock=urllib.urlopen(web)
        htmlSource = sock.readlines()
        sock.close()
        start=htmlSource.index('<TABLE>\n')
        startinfo=htmlSource.index('<TABLE border=1>\n')
        end=start+14
        for line in range(start,len(htmlSource)):
            l=htmlSource[line]
            l=l.replace("</B>", " ")
            for i in dict:
                l=l.replace(i,"")
            arr.append(l)
        dictSpace=['','  ']
        for j in dictSpace:
            x=0
            for item in arr:
                if item == j:
                    arr.pop(x)
                x=x+1
        for thing in arr:
            if re.search('Rule',thing) != None:
                data= arr.index(thing)+3
        halfarr=[]
        self.infoText.AppendText(arr[0] + '                              ' + arr[7]+'\n'\
                            +arr[2] +'           ' + arr[5]+'\n'\
                            +arr[3] +'                           '+arr[4]+'\n'\
                            +arr[8])
        id=self.findProID()
        ss= arr[0][7:12]
        ss=(float(ss[0:2])+(float(ss[3:6])/60))
        sr= arr[7][8:13]
        sr=(float(sr[0:2])+(float(sr[3:6])/60))
        mr= arr[3][10:15]
        ms= arr[4][9:14]
        
        try:
            mr=(float(mr[0:2])+(float(mr[3:6])/60))
        except:
            if re.search('Befor',mr)!=None:
                mr='b'
            if re.search('After',mr)!=None:
                mr='a'
        try:
            ms=(float(ms[0:2])+(float(ms[3:6])/60))
        except:
            if re.search('Befor',ms)!=None:
                ms='b'
            if re.search('After',ms)!=None:
                ms='a'

        halfarr.append([sr, ss, mr, ms])
        inst0=arr[data+5]
        if len(inst0) >10:
            inst0=inst0[:7]
        try:
            self.infoBlock.AppendText('Block  Program  Start   End    Location    Inst     BeginChange EndChange \n'\
                                          ' %s      %s  %s %s   %s    %s  %s  %s  ' % (arr[data],id[0],arr[data+2],arr[data+3],arr[data+4],inst0.ljust(7),arr[data+6].ljust(10),arr[data+7]))    
        except:
            selfinfoBlock.AppendText('restart program')
        fmt='%H:%M'
        fmt2="%M"
        schangeb=arr[data+6]
        if schangeb == " ":
            schangeb='00:00'
        echangeb=arr[data+7]
        if echangeb == " ":
            echangeb='00:00'

        sschb=datetime.datetime(*time.strptime(arr[data+2][1:6],fmt)[:6])-datetime.timedelta(minutes=int(schangeb[4:6]))
        eschb=datetime.datetime(*time.strptime(arr[data+3][1:6],fmt)[:6])+datetime.timedelta(minutes=int(echangeb[4:6]))
   
        dstartb=(float(arr[data+2][0:3])+(float(arr[data+2][4:6])/60))
        dendb=(float(arr[data+3][0:3])+(float(arr[data+3][4:6])/60))
        schangeb=(float(schangeb[0:2])+(float(schangeb[4:6])/60))
        echangeb=(float(echangeb[0:2])+(float(echangeb[4:6])/60))
    
        halfarr.append([id[0],"%02.f:%02.f"%(float(sschb.hour),float(sschb.minute)),"%02.f:%02.f"%(float(eschb.hour),float(eschb.minute)),dstartb-schangeb,dendb+echangeb,schangeb,echangeb])
        inst1=arr[data+16]
        if len(inst1) >7:
            inst1=inst1[:7]
        self.infoBlock.AppendText('\n %s      %s  %s %s   %s    %s  %s  %s  ' % (arr[data+11],id[1],arr[data+13],arr[data+14],arr[data+15],inst1.ljust(7),arr[data+17].ljust(10),arr[data+18]))    

        schangec=arr[data+17]
        if schangec == " ":
            schangec='00:00'
        echangec=arr[data+18]
        if echangec == " ":
            echangec='00:00'
        sschc=datetime.datetime(*time.strptime(arr[data+13][1:6],fmt)[:6])-datetime.timedelta(minutes=int(schangec[4:6]))
        eschc=datetime.datetime(*time.strptime(arr[data+14][1:6],fmt)[:6])+datetime.timedelta(minutes=int(echangec[4:6]))

        dstartc=(float(arr[data+13][0:3])+(float(arr[data+13][4:6])/60))
        dendc=(float(arr[data+14][0:3])+(float(arr[data+14][4:6])/60))
        schangec=(float(schangec[0:2])+(float(schangec[4:6])/60))
        echangec=(float(echangec[0:2])+(float(echangec[4:6])/60))  
        halfarr.append([id[1],"%02.f:%02.f"%(float(sschc.hour),float(sschc.minute)),"%02.f:%02.f"%(float(eschc.hour),float(eschc.minute)),dstartc-schangec,dendc+echangec,schangec,echangec])

        if len(id) >2:
            inst2=arr[data+27]
            if len(inst2) >10:
                inst2=inst2[:7]
            self.infoBlock.AppendText('\n %s      %s  %s %s   %s    %s  %s  %s  ' % (arr[data+22],id[2],arr[data+24],arr[data+25],arr[data+26],arr[data+27],arr[data+28].ljust(15),arr[data+29])) 

            schanged=arr[data+28]
            if schanged == " ":
                schanged='00:00'
            echanged=arr[data+29]
            if echanged == " ":
                echanged='00:00'
            sschd=datetime.datetime(*time.strptime(arr[data+24][1:6],fmt)[:6])-datetime.timedelta(minutes=int(schanged[4:6]))
            eschd=datetime.datetime(*time.strptime(arr[data+25][1:6],fmt)[:6])+datetime.timedelta(minutes=int(echanged[4:6]))

            dstartd=(float(arr[data+24][0:3])+(float(arr[data+24][4:6])/60))
            dendd=(float(arr[data+25][0:3])+(float(arr[data+25][4:6])/60))
            schanged=(float(schanged[0:2])+(float(schanged[4:6])/60))
            echanged=(float(echanged[0:2])+(float(echanged[4:6])/60))  
            halfarr.append([id[2],"%02.f:%02.f"%(float(sschd.hour),float(sschd.minute)),"%02.f:%02.f"%(float(eschd.hour),float(eschd.minute)),dstartd-schanged,dendd+echanged,schanged,echanged])

            if len(id) >3:
                inst3=arr[data+38]
                if len(inst3) >10:
                    inst3=inst3[:7]
                self.infoBlock.AppendText('\n %s      %s  %s %s   %s    %s  %s  %s  ' % (arr[data+33],id[3],arr[data+35],arr[data+36],arr[data+37],arr[data+38],arr[data+39].ljust(15),arr[data+40])) 

                schangee=arr[data+39]
                if schangee == " ":
                    schangee='00:00'
                echangee=arr[data+40]
                if echangee == " ":
                    echangee='00:00'
                ssche=datetime.datetime(*time.strptime(arr[data+35][1:6],fmt)[:6])-datetime.timedelta(minutes=int(schangee[4:6]))
                esche=datetime.datetime(*time.strptime(arr[data+36][1:6],fmt)[:6])+datetime.timedelta(minutes=int(echangee[4:6]))

                dstarte=(float(arr[data+35][0:3])+(float(arr[data+35][4:6])/60))
                dende=(float(arr[data+36][0:3])+(float(arr[data+36][4:6])/60))
                schangee=(float(schangee[0:2])+(float(schangee[4:6])/60))
                echangee=(float(echangee[0:2])+(float(echangee[4:6])/60))  
                halfarr.append([id[3],"%02.f:%02.f"%(float(ssche.hour),float(ssche.minute)),"%02.f:%02.f"%(float(esche.hour),float(esche.minute)),dstarte-schangee,dende+echangee,schangee,echangee])
        
        return halfarr
  
    def halfNight(self):
        peeps=len(self.findProID())
        half=self.timeData(self.getDate())

        sr=half[0][0]
        ss=half[0][1]
        mr=half[0][2]
        ms=half[0][3]
        bt1=None
        dt1=None
        bt2=None
        dt2=None
        bt3=None
        dt3=None
        bt4=None
        dt4=None
        sa=half[1][3]
        ea=half[1][4]
        sb=half[2][3]
        eb=half[2][4]
        if peeps >2:
            sc=half[3][3]
            ec=half[3][4]
        if peeps >3:
            sd=half[4][3]
            ed=half[4][4]

        if mr <=10 and mr >=0 and mr!=None:
            mr=mr+24.0
        if ms <=10 and ms >=0 and ms!=None:
            ms=ms+24.0
        if sa <=10 and sa >=0:
            sa=sa+24.0
        if ea <=10 and ea >=0:
            ea=ea+24.0
        if sb <=10 and sb >=0:
            sb=sb+24.0
        if eb <=10 and eb >=0:
            eb=eb+24.0
        if peeps >2:
            if sc <=10 and sc >=0:
                sc=sc+24.0
            if ec <=10 and ec >=0:
                ec=ec+24.0
        if peeps >3:
            if sd <=10 and sd >=0:
                sd=sd+24.0
            if ed <=10 and ed >=0:
                ed=ed+24.0
    #----
        if ms=='a' and mr=='b':
            bt1=ea-sa
            dt1=0
        elif mr !='b' and mr!='a' and mr >=sa:
            if mr<=ea:
                 bt1=ea-mr
                 dt1=mr-sa
            else:
                dt1 = ea-sa
                bt1=0
        elif mr!=None and mr <=sa:
            if ms==None:
                bt1=ea-sa
                dt1=0
            else:
                bt1=ms-mr
                dt1=0
        elif ms != None and ms<=sa:
            dt1=ea-sa
            bt1=0
        elif ms !=None and ms!='a' and ms>=sa:
             if ms <=ea:
                dt1=ea-ms
                bt1=ms-sa
             else:
                dt1=0
                bt1=ea-sa

    #----------------
        if ms=='a' and mr=='b':
            bt2=eb-sb
            dt2=0
        elif  mr !='b' and mr!='a' and mr >=sb:
            if mr<=eb:
                bt2=eb-mr
                dt2=mr-sb
            else:
                dt2 = eb-sb
                bt2=0
        elif mr!=None and mr <=sb:
            if ms==None or ms == 'a':
                bt2=eb-sb
                dt2=0
            else:
                bt2=ms-mr
                dt2=0
        elif ms != None and ms<=sb:
            dt2=eb-sb
            bt2=0
        elif ms !='b' and ms!='a' and ms>=sb:
             if ms <=eb:
                dt2=eb-ms
                bt2=ms-sb
             else:
                dt2=0
                bt2=eb-sb


    #----
        if peeps >2:
            #print sc,ec, mr, ms
            if ms=='a' and mr=='b':
                bt3=ec-sc
                dt3=0
            elif  mr !='b' and mr!='a' and mr >=sc:
                if mr<ec:
                    bt3=ec-mr
                    dt3=mr-sc
                else:
                    dt3 = ec-sc
                    bt3=0
            elif mr!=None and mr <=sc:
                if ms==None or ms == 'a':
                    bt3=ec-sc
                    dt3=0
                else:
                    bt3=ms-mr
                    dt3=0
            elif ms != None and ms<=sc:
                dt3=ec-sc
                bt3=0
            elif ms !=None  and ms!='a' and ms>=sc:
                if ms <=ec:
                    dt3=ec-ms
                    bt3=ms-sc 
                else:
                    dt3=0
                    bt3=ec-sc
    #----
        if peeps >3:
            if ms=='a' and mr=='b':
                bt4=ed-sd
                dt4=0
            elif  mr !='b' and mr!='a' and mr >=sd:
                if mr<=ed:
                    bt4=ed-mr
                    dt4=mr-sd
                else:
                    dt4 = ed-sd
                    bt4=0
            elif mr!=None and mr <=sd:
                if ms=='a':
                    bt4=ed-sd
                    dt4=0
                else:
                    bt4=ms-mr
                    dt4=0

            elif ms != None and ms<=sd:
                dt4=ed-sd
                bt4=0
            elif ms !=None  and ms!='a' and ms>=sd:
                if ms <=ed:
                    dt4=ed-ms
                    bt4=ms-sd
                else:
                    dt4=0
                    bt4=ed-sd

        try:
            self.line1='%s/R     %s   %s    0    0    0    0   %2.1f  %2.1f   0    0' % (half[1][0], str(half[1][1]), str(half[1][2]),dt1, bt1)
            self.sc1.AppendText(self.line1)
  
        except:
            None
        try:
            line2='%s/R     %s   %s    0    0    0    0   %2.1f  %2.1f   0    0' % (half[2][0], str(half[2][1]), str(half[2][2]), dt2, bt2)
            self.sc2.AppendText(line2)
        except:
            print 'error halfnight user2'
        if peeps > 2:
            try:
                line3='%s/R     %s   %s    0    0    0    0   %2.1f  %2.1f   0    0' % (half[3][0],  str(half[3][1]), str(half[3][2]), dt3, bt3)
                self.sc3.AppendText(line3)
            except:
                None
        if peeps > 3:
            try:
                line4='%s/R     %s   %s    0    0    0    0   %2.1f  %2.1f   0    0' % (half[4][0], str( half[4][1]), str(half[4][2]), dt4, bt4)
                self.sc4.AppendText(line4)
            except:
                None

    def findProID(self):
        global version
        arr=[]
        harr=[]
        if self.debug=='yes':
            web=self.webbug
        else:
            version=self.findVer()
            tarr=self.getDate()
            web='http://35m-schedule.apo.nmsu.edu/%s/html/days/%s-%s-%s.html' % (version,tarr[2],tarr[0], tarr[1])

        #print web
        sock=urllib.urlopen(web)
        htmlSource = sock.readlines()
        sock.close()
        for line in htmlSource:
            if '<TD><a href=' in line:
                arr.append(line)
        for pos in arr:
            t=pos[23:]
            t=t[:-16]
            harr.append(t.rstrip('h.'))
        try:
            harr.pop(0)
        except IndexError:
            print 'error, line 295'
        return harr

    def generate(self,event):
        day=self.getDate()
        file='/Users/%s/NightLogs/3.5mNightLog%s%s%s' % (os.getenv('USER'), day[2],day[0], day[1])
        self.output(file)
        if sys.platform=='linux2':
            os.system('gedit '+file +' &')
        else:
            os.system('open -a textedit '+file )

    def output(self,file):
        """Write the output file that is the log"""
        peep=len(self.findProID())
        f=open(file,'w')
        f.writelines("                      Apache Point Observatory\n"\
                               "                      3.5m Telescope Night Log\n")
        f.writelines("                      "+self.link.GetLabel()+'\n')
        #f.writelines('\n'+self.userHeader.GetLabel()+'\n')
        f.writelines("\n                                                           ACTUAL\n"\
                         " ASTRONOMER      OBSERVER(S)            INSTRUMENT     START  FINISH\n"\
                         "--------------------------------------------------------------------\n")
        f.writelines('%s%s%s%s%s\n' % (self.usastr0.GetValue().ljust(18),self.usobs0.GetValue().ljust(22),self.usinst0.GetValue().ljust(15),self.usstart0.GetValue().ljust(8), self.usend0.GetValue().ljust(8)))
        if oneVar==1:
            f.writelines('%s%s%s%s%s\n' % (self.usastr0b.GetValue().ljust(18),self.usobs0b.GetValue().ljust(22),self.usinst0b.GetValue().ljust(15),self.usstart0b.GetValue().ljust(8), self.usend0b.GetValue()))
        f.writelines('%s%s%s%s%s\n' % (self.usastr1.GetValue().ljust(18), self.usobs1.GetValue().ljust(22),self.usinst1.GetValue().ljust(15),self.usstart1.GetValue().ljust(8), self.usend1.GetValue()))
        if twoVar==1:
            f.writelines('%s%s%s%s%s\n' % (self.usastr1b.GetValue().ljust(18),self.usobs1b.GetValue().ljust(22),self.usinst1b.GetValue().ljust(15),self.usstart1b.GetValue().ljust(8), self.usend1b.GetValue()))
        if peep > 2:
            f.writelines('%s%s%s%s%s\n' % (self.usastr2.GetValue().ljust(18), self.usobs2.GetValue().ljust(22),self.usinst2.GetValue().ljust(15),self.usstart2.GetValue().ljust(8), self.usend2.GetValue()))
            if threeVar==1:
                f.writelines('%s%s%s%s%s\n' % (self.usastr2b.GetValue().ljust(18),self.usobs2b.GetValue().ljust(22),self.usinst2b.GetValue().ljust(15),self.usstart2b.GetValue().ljust(8), self.usend2b.GetValue()))
        if peep > 3:
            f.writelines('%s%s%s%s%s\n' % (self.usastr3.GetValue().ljust(18), self.usobs3.GetValue().ljust(22), self.usinst3.GetValue().ljust(15),self.usstart3.GetValue().ljust(8), self.usend3.GetValue()))
            if fourVar==1:
                f.writelines('%s%s%s%s%s\n' % (self.usastr3b.GetValue().ljust(18),self.usobs3b.GetValue().ljust(22),self.usinst3b.GetValue().ljust(15),self.usstart3b.GetValue().ljust(8), self.usend3b.GetValue()))

        f.writelines('\n' + self.schedHalf.GetLabel())
        f.writelines(" ----------------------------------------------------------------\n")
        f.writelines('%s\n' % self.sc1.GetValue())
        f.writelines('%s\n' % self.sc2.GetValue())
        if peep > 2:
            f.writelines('%s\n' %self.sc3.GetValue())
        if peep > 3:
            f.writelines('%s\n' % self.sc4.GetValue())
        f.writelines("\nnote: scheduled times listed include instrument change time\n\n"\
                        "              ------------- ACTIVITY LOG --------------\n")
        f.writelines(self.obsspec.GetLabel()+'\n\n')
        f.writelines(self.actText.GetValue()+'\n')
        f.writelines("\n                    ------- FAILURE LOG -------\n"\
                        "\n"\
                        "PROG   INST   FAILURE MODE     TIME\n"\
                        "    (SEDFNVOG)   TI/SHU    START  FINISH  DESCRIPTION\n"\
                        "----------------------------------------------------------------------\n")
        f.writelines(self.failLog.GetValue()+'\n')
        f.writelines('\n'+self.focus.GetLabel()+'\n')
        f.writelines(self.focusLog.GetValue()+'\n')
        f.writelines(self.weathText.GetValue()+'\n')
        f.writelines('     Note: the wind was coming from the azimuth listed.\n'\
                         '     The convention used is north=0 degrees, east=90 degrees.\n'\
                         '     The dust count is particles > 1u per 0.1 cubic feet.\n\n')
        f.writelines(self.stat.GetLabel()+'\n')
        f.writelines("    Telescope drives operational. Current TCC version: " + self.statTCCText.GetValue() + '\n')
        f.writelines("    Current TUI version: " + self.statTUIText.GetValue() + '\n') 
        f.close()

        """In safari save as page source with filename weather.html
    In firefox save as web page, html only with filename weather.html
    """
    def getWeather(self,event):
        file='/Users/%s/Desktop/weather.html' % os.getenv('USER')
        f=open(file,'r')
        x=0
        for line in f.readlines():
            if x >6:
                self.weathText.AppendText(line)
            x=x+1
        f.close()


app=wx.App(False)
frame=Log(None, 'Auto Night Log Version 2.9')
app.MainLoop()
                                

                        
