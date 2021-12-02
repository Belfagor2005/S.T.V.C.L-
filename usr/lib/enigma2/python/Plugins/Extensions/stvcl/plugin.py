#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Info http://t.me/tivustream
****************************************
*        coded by Lululla              *
*                                      *
*             30/11/2021               *
****************************************
'''
from __future__ import print_function
from . import _
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.ConfigList import ConfigListScreen
# from Components.HTMLComponent import HTMLComponent
from Components.Input import Input
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap, MultiPixmap
from Components.PluginComponent import plugins
from Components.PluginList import *
from Components.ProgressBar import ProgressBar
from Components.ScrollLabel import ScrollLabel
from Components.SelectionList import SelectionList
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.ServiceList import ServiceList
from Components.Sources.List import List
from Components.Sources.Progress import Progress
from Components.Sources.Source import Source
from Components.Sources.StaticText import StaticText
from Components.config import *
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.InfoBar import InfoBar
from Screens.InfoBar import MoviePlayer
from Screens.InfoBarGenerics import InfoBarMenu, InfoBarSeek, InfoBarAudioSelection, \
    InfoBarSubtitleSupport, InfoBarNotifications
from Screens.InputBox import InputBox
from Screens.LocationBox import LocationBox
from Screens.MessageBox import MessageBox
from Screens.PluginBrowser import PluginBrowser
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop, Standby
from Screens.VirtualKeyBoard import VirtualKeyBoard
from ServiceReference import ServiceReference
from Tools.Directories import SCOPE_PLUGINS, resolveFilename
from Tools.Downloader import downloadWithProgress
from Tools.LoadPixmap import LoadPixmap
from enigma import *
from enigma import RT_HALIGN_CENTER, RT_VALIGN_CENTER
from enigma import RT_HALIGN_LEFT, RT_HALIGN_RIGHT
from enigma import eSize, eListbox, eListboxPythonMultiContent, eServiceCenter, eServiceReference, iPlayableService
from enigma import eTimer
from enigma import ePicLoad, gPixmapPtr
from enigma import loadPNG, gFont
from os.path import splitext
from sys import version_info
from time import sleep
from twisted.web.client import downloadPage, getPage
from xml.dom import Node, minidom
import base64
import glob
import os
import re
import shutil
import six
# import socket
import ssl
import sys
import time
from six.moves.urllib.request import urlopen
from six.moves.urllib.request import Request
# from six.moves.urllib.error import HTTPError
# from six.moves.urllib.error import URLError
from six.moves.urllib.parse import urlparse
from six.moves.urllib.parse import quote
from six.moves.urllib.parse import urlencode
from six.moves.urllib.request import urlretrieve
# import six.moves.urllib.request
from Plugins.Extensions.stvcl.getpics import GridMain
from Plugins.Extensions.stvcl.getpics import getpics
try:
    from Plugins.Extensions.stvcl.Utils import *
except:
    from . import Utils
try:
    import io
except:
    import StringIO
try:
    import http.cookiejar
except:
    import cookielib
try:
    import httplib
except:
    import http.client

if sys.version_info >= (2, 7, 9):
	try:
		import ssl
		sslContext = ssl._create_unverified_context()
	except:
		sslContext = None

global Path_Movies, defpic, skin_path
currversion = '1.2'
Version = currversion + ' - 24.11.2021'
title_plug = '..:: S.T.V.C.L. V.%s ::..' % Version
name_plug = 'Smart Tv Channels List'
plugin_fold    = os.path.dirname(sys.modules[__name__].__file__)
# Credits = 'http://t.me/tivustream'
Maintainer2 = 'Maintener @Lululla'
dir_enigma2 = '/etc/enigma2/'
service_types_tv = '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 134) || (type == 195)'
res_plugin_fold=plugin_fold + '/res/'
defpic = resolveFilename(SCOPE_PLUGINS, "Extensions/stvcl/res/pics/{}".format('defaultL.png'))
dblank = resolveFilename(SCOPE_PLUGINS, "Extensions/stvcl/res/pics/{}".format('blankL.png'))
#================
def add_skin_font():
    font_path = plugin_fold + '/res/fonts/'
    # addFont(font_path + 'verdana_r.ttf', 'OpenFont1', 100, 1)
    addFont(font_path + 'verdana_r.ttf', 'OpenFont2', 100, 1)
try:
    from OpenSSL import SSL
    from twisted.internet import ssl
    from twisted.internet._sslverify import ClientTLSOptions
    sslverify = True
except:
    sslverify = False

if sslverify:
    class SNIFactory(ssl.ClientContextFactory):
        def __init__(self, hostname=None):
            self.hostname = hostname

        def getContext(self):
            ctx = self._contextFactory(self.method)
            if self.hostname:
                ClientTLSOptions(self.hostname, ctx)
            return ctx
modechoices = [
                ("4097", _("ServiceMp3(4097)")),
                ("1", _("Hardware(1)")),
                ]
if os.path.exists("/usr/bin/gstplayer"):
    modechoices.append(("5001", _("Gstreamer(5001)")))
if os.path.exists("/usr/bin/exteplayer3"):
    modechoices.append(("5002", _("Exteplayer3(5002)")))
if os.path.exists("/usr/sbin/streamlinksrv"):
    modechoices.append(("5002", _("Streamlink(5002)")))
if os.path.exists("/usr/bin/apt-get"):
    modechoices.append(("8193", _("eServiceUri(8193)")))
sessions = []
config.plugins.stvcl = ConfigSubsection()
config.plugins.stvcl.pthm3uf = ConfigDirectory(default='/media/hdd/movie')
try:
    from Components.UsageConfig import defaultMoviePath
    downloadpath = defaultMoviePath()
    config.plugins.stvcl.pthm3uf  = ConfigDirectory(default=downloadpath)
except:
    if os.path.exists("/usr/bin/apt-get"):
        config.plugins.stvcl.pthm3uf  = ConfigDirectory(default='/media/hdd/movie/')
config.plugins.stvcl.bouquettop             = ConfigSelection(default='Bottom', choices=['Bottom', 'Top'])
config.plugins.stvcl.services               = ConfigSelection(default='4097', choices=modechoices)
config.plugins.stvcl.cachefold              = ConfigDirectory(default='/media/hdd/')
config.plugins.stvcl.filter                = ConfigYesNo(default=False)
config.plugins.stvcl.strtext                = ConfigYesNo(default=True)
config.plugins.stvcl.strtmain               = ConfigYesNo(default=True)
config.plugins.stvcl.thumb                  = ConfigYesNo(default=False)
config.plugins.stvcl.thumbpic               = ConfigYesNo(default=False)
tvstrvl = str(config.plugins.stvcl.cachefold.value) + "stvcl"
tmpfold = str(config.plugins.stvcl.cachefold.value) + "stvcl/tmp"
picfold = str(config.plugins.stvcl.cachefold.value) + "stvcl/pic"

Path_Movies = str(config.plugins.stvcl.pthm3uf.value)
if Path_Movies.endswith("\/\/"):
    Path_Movies = Path_Movies[:-1]
print('patch movies: ', Path_Movies)

if not os.path.exists(tvstrvl):
    os.system("mkdir " + tvstrvl)

if not os.path.exists(tmpfold):
    os.system("mkdir " + tmpfold)

if not os.path.exists(picfold):
    os.system("mkdir " + picfold)

if isFHD():
    skin_path=res_plugin_fold + 'skins/fhd/'
    defpic = resolveFilename(SCOPE_PLUGINS, "Extensions/stvcl/res/pics/{}".format('defaultL.png'))
else:
    skin_path=res_plugin_fold + 'skins/hd/'
    defpic = resolveFilename(SCOPE_PLUGINS, "Extensions/stvcl/res/pics/{}".format('default.png'))
if os.path.exists('/var/lib/dpkg/status'):
    skin_path=skin_path + 'dreamOs/'

def m3ulistEntry(download):
    res = [download]
    white = 16777215
    yellow = 16776960
    green = 3828297
    col = 16777215
    backcol = 0
    blue = 4282611429
    png = resolveFilename(SCOPE_PLUGINS, "Extensions/stvcl/res/pics/{}".format('setting2.png'))
    if isFHD():
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1200, 50), font=7, text=download, color = 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1000, 50), font=2, text=download, color = 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res

def m3ulist(data, list):
    icount = 0
    mlist = []
    for line in data:
        name = data[icount]
        mlist.append(m3ulistEntry(name))
        icount = icount + 1
    list.setList(mlist)

class tvList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setFont(0, gFont('OpenFont2', 20))
        self.l.setFont(1, gFont('OpenFont2', 22))
        self.l.setFont(2, gFont('OpenFont2', 24))
        self.l.setFont(3, gFont('OpenFont2', 26))
        self.l.setFont(4, gFont('OpenFont2', 28))
        self.l.setFont(5, gFont('OpenFont2', 30))
        self.l.setFont(6, gFont('OpenFont2', 32))
        self.l.setFont(7, gFont('OpenFont2', 34))
        self.l.setFont(8, gFont('OpenFont2', 36))
        self.l.setFont(9, gFont('OpenFont2', 40))
        if isFHD():
            self.l.setItemHeight(50)
        else:
            self.l.setItemHeight(50)

def tvListEntry(name,png):
    res = [name]
    png = resolveFilename(SCOPE_PLUGINS, "Extensions/stvcl/res/pics/{}".format('setting.png'))
    if isFHD():
            res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(png)))
            res.append(MultiContentEntryText(pos=(60, 0), size=(1200, 50), font=7, text=name, color = 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
            res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(png)))
            res.append(MultiContentEntryText(pos=(60, 0), size=(1000, 50), font=2, text=name, color = 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res

Panel_list = [
 ('SMTVCL')
 ]

class OpenScript(Screen):
    def __init__(self, session):
        self.session = session
        skin = skin_path + '/OpenScript.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        # f.close()
        Screen.__init__(self, session)
        self.setup_title = _('Smart Tv Channel List')
        self['list'] = tvList([])
        self.icount = 0
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
        self.downloading = False
        self['title'] = Label(_(title_plug))
        self['Maintainer2'] = Label('%s' % Maintainer2)
        self['path'] = Label(_('Folder path %s') % Path_Movies)
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button('')
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self["key_green"].hide()
        self["key_yellow"].hide()
        self["key_blue"].hide()
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'MenuActions', 'TimerEditActions'],
         {'ok': self.okRun,
         'menu': self.scsetup,
         'red': self.close,
         # 'green': self.messagereload,
         'info': self.close,
         # 'yellow': self.messagedellist,
         # 'blue': self.ChannelList,
         'back': self.close,
         'cancel': self.close}, -1)
        # self.onFirstExecBegin.append(self.updateMenuList)
        self.onLayoutFinish.append(self.updateMenuList)

    def updateMenuList(self):
        self.menu_list = []
        for x in self.menu_list:
            del self.menu_list[0]
        list = []
        idx = 0
        png = resolveFilename(SCOPE_PLUGINS, "Extensions/stvcl/res/pics/{}".format('setting.png'))
        for x in Panel_list:
            list.append(tvListEntry(x, png))
            self.menu_list.append(x)
            idx += 1
        self['list'].setList(list)

    def okRun(self):
        self.keyNumberGlobalCB(self['list'].getSelectedIndex())

    def keyNumberGlobalCB(self, idx):
        sel = self.menu_list[idx]
        url = ''
        if sel == ("SMTVCL"):
            url = 'http://i.mjh.nz/'
        else:
            return
        self.downlist(sel, url)

    def downloadProgress(self, recvbytes, totalbytes):
        self["progress"].show()
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

    def check(self, fplug):
        self.downloading = False
        self['progresstext'].text = ''
        self.progclear = 0
        self['progress'].setValue(self.progclear)
        self["progress"].hide()

    def showError(self, error):
        self.downloading = False
        self.session.open(MessageBox, _('Download Failed!!!'), MessageBox.TYPE_INFO, timeout=5)

    def downlist(self, sel, url):
        global in_tmp
        namem3u = str(sel)
        urlm3u = checkStr(url.strip())
        if six.PY3:
            urlm3u.encode()
        # if six.PY3:
            # urlm3u = six.ensure_str(urlm3u)
        print('urlmm33uu ', urlm3u)
        try:
            fileTitle = re.sub(r'[\<\>\:\"\/\\\|\?\*\[\]]', '_', namem3u)
            fileTitle = re.sub(r' ', '_', fileTitle)
            fileTitle = re.sub(r'_+', '_', fileTitle)
            fileTitle = fileTitle.replace("(", "_").replace(")", "_").replace("#", "").replace("+", "_").replace("\'", "_").replace("'", "_").replace("!", "_").replace("&", "_")
            fileTitle = fileTitle.lower() #+ ext
            in_tmp = str(Path_Movies) + str(fileTitle) + '.m3u'
            if os.path.isfile(in_tmp):
                os.remove(in_tmp)
            print('in tmp' , in_tmp)
            # # self.download = downloadWithProgress(urlm3u, in_tmp)
            # # self.download.addProgress(self.downloadProgress)
            # # self.download.start().addCallback(self.check).addErrback(self.showError)
            urlretrieve(urlm3u, in_tmp)
            sleep(4)
            self.session.open(ListM3u1, namem3u, urlm3u)
        except Exception as e:
            print('errore e : ', e)

    def scsetup(self):
        self.session.open(OpenConfig)

class ListM3u1(Screen):
    def __init__(self, session, namem3u, url):
        self.session = session
        skin = skin_path + '/ListM3u.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        # f.close()
        Screen.__init__(self, session)
        self.list = []
        self['list'] = tvList([])
        global SREF
        self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
        SREF = self.initialservice
        self['title'] = Label(title_plug + ' ' + namem3u)
        self['Maintainer2'] = Label('%s' % Maintainer2)
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
        self.downloading = False
        self.convert = False
        self.url = url
        self.name = namem3u
        self['path'] = Label(_('Folder path %s') % Path_Movies)
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button('')
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self["key_green"].hide()
        self["key_yellow"].hide()
        self["key_blue"].hide()
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'MenuActions', 'TimerEditActions'],
        {
         # 'green': self.message2,
         # 'yellow': self.message1,
         # 'blue': self.message1,
         'cancel': self.cancel,
         'ok': self.runList}, -2)
        if not os.path.exists(Path_Movies):
            self.mbox = self.session.open(MessageBox, _('Check in your Config Plugin - Path Movie'), MessageBox.TYPE_INFO, timeout=5)
            self.scsetup()
        self.onFirstExecBegin.append(self.openList)
        sleep(3)
        # self.onLayoutFinish.append(self.openList2)
        self.onLayoutFinish.append(self.passing)

    def passing(self):
        pass

    def scsetup(self):
        self.session.openWithCallback(self.close, OpenConfig)

    def openList(self):
        self.names = []
        self.urls = []
        content = ReadUrl(self.url)
        if six.PY3:
            content = six.ensure_str(content)
        print('content: ',content)
        try:
            regexvideo = '<a href="(.*?)">'
            match = re.compile(regexvideo, re.DOTALL).findall(content)
            print('ListM3u match = ', match)
            items = []
            for url in match:
                if '..' in url:
                    continue
                name = url.replace('/', '')
                url = self.url + url + '/'
                # item = name + "###" + url
                # print('ListM3u url-name Items sort: ', item)
                # items.append(item)
            # items.sort()
            # for item in items:
                # name = item.split('###')[0]
                # url = item.split('###')[1]
                self.names.append(checkStr(name))
                self.urls.append(checkStr(url))
            m3ulist(self.names, self['list'])
        except Exception as e:
            print('errore e : ', e)

    def runList(self):
        idx = self["list"].getSelectionIndex()
        sel = self.names[idx]
        urlm3u = self.urls[idx]
        if idx == -1 or None or '':
            return
        else:
            self.session.open(ListM3u, sel, urlm3u)

    def cancel(self):
        self.close()

class ListM3u(Screen):
    def __init__(self, session, namem3u, url):
        self.session = session
        skin = skin_path + '/ListM3u.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        # f.close()
        Screen.__init__(self, session)
        self.list = []
        self['list'] = tvList([])
        global SREF
        self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
        SREF = self.initialservice
        self['title'] = Label(title_plug + ' ' + namem3u)
        self['Maintainer2'] = Label('%s' % Maintainer2)
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
        self.downloading = False
        self.convert = False
        self.url = url
        self.name = namem3u
        self['path'] = Label(_('Folder path %s') % Path_Movies)
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button('')
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self["key_green"].hide()
        self["key_yellow"].hide()
        self["key_blue"].hide()
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'MenuActions', 'TimerEditActions'],
        {
         # 'green': self.message2,
         # 'yellow': self.message1,
         # 'blue': self.message1,
         'cancel': self.cancel,
         'ok': self.runList}, -2)
        if not os.path.exists(Path_Movies):
            self.mbox = self.session.open(MessageBox, _('Check in your Config Plugin - Path Movie'), MessageBox.TYPE_INFO, timeout=5)
            self.scsetup()
        self.onFirstExecBegin.append(self.openList)
        sleep(3)
        # self.onLayoutFinish.append(self.openList2)
        self.onLayoutFinish.append(self.passing)

    def passing(self):
        pass

    def scsetup(self):
        self.session.openWithCallback(self.close, OpenConfig)

    def openList(self):
        self.names = []
        self.urls = []
        content = ReadUrl(self.url)
        if six.PY3:
            content = six.ensure_str(content)
        print('content: ',content)
        #<a href="br.xml.gz">br.xml.gz</a>  21-Oct-2021 07:05   108884
        #<a href="raw-radio.m3u8">raw-radio.m3u8</a>    22-Oct-2021 06:08   9639
        try:
            regexvideo = '<a href="(.*?)">.*?</a>.*?-(.*?)-(.*?) '
            match = re.compile(regexvideo, re.DOTALL).findall(content)
            print('ListM3u match = ', match)
            items = []
            for url, mm, aa in match:
                if '.m3u8' in url:
                    name = url.replace('.m3u8', '')
                    name = name + ' ' + mm + '-' + aa
                    url = self.url + url
                    item = name + "###" + url
                    print('ListM3u url-name Items sort: ', item)
                    items.append(item)
            items.sort()
            for item in items:
                name = item.split('###')[0]
                url = item.split('###')[1]
                self.names.append(checkStr(name))
                self.urls.append(checkStr(url))
            m3ulist(self.names, self['list'])
        except Exception as e:
            print('errore e : ', e)

    def runList(self):
        idx = self["list"].getSelectionIndex()
        sel = self.names[idx]
        urlm3u = self.urls[idx]
        if idx == -1 or None or '':
            return
        else:
            self.session.open(ChannelList, sel, urlm3u)

    def cancel(self):
        self.close()

class ChannelList(Screen):
    def __init__(self, session, name, url ):
        self.session = session
        skin = skin_path + '/ChannelList.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        # f.close()
        Screen.__init__(self, session)
        self.list = []
        self.picload = ePicLoad()
        self.scale = AVSwitch().getFramebufferScale()
        self['list'] = tvList([])
        self.setTitle(title_plug + ' ' + name)
        self['title'] = Label(title_plug + ' ' + name)
        self['Maintainer2'] = Label('%s' % Maintainer2)
        service = config.plugins.stvcl.services.value
        self['service'] = Label(_('Service Reference used %s') % service)
        self['live'] = Label('')
        self['path'] = Label(_('Folder path %s') % Path_Movies)
        self['poster'] = Pixmap()
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_('Convert ExtePlayer3'))
        self['key_yellow'] = Button(_('Convert Gstreamer'))
        self["key_blue"] = Button(_("Search"))
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
        self.downloading = False
        self.pin = False
        global search_ok
        global in_tmp
        global search_ok
        global servicx
        self.servicx = ''
        search_ok = False
        in_tmp = Path_Movies
        self.search = ''
        search_ok = False
        self.name = name
        self.url = url
        self.names = []
        self.urls = []
        self.pics = []
        self['setupActions'] = ActionMap(['SetupActions', 'DirectionActions', 'ColorActions', 'MenuActions', 'TimerEditActions', 'InfobarInstantRecord'], {'red': self.cancel,
         # 'green': self.runRec,
         'menu': self.AdjUrlFavo,
         'green': self.message2,
         'yellow': self.message1,
         'cancel': self.cancel,
         'up': self.up,
         'down': self.down,
         'left': self.left,
         'right': self.right,
         "blue": self.search_m3u,
         "rec": self.runRec,
         "instantRecord": self.runRec,
         "ShortRecord": self.runRec,
         'ok': self.runChannel}, -2)
        # if 'http' in self.url:
        self.currentList = 'list'
        self.onLayoutFinish.append(self.downlist)
        # self.onFirstExecBegin.append(self.downlist)
        print('ChannelList sleep 4 - 1')
        self.onLayoutFinish.append(self.__layoutFinished)

    def __layoutFinished(self):
        # self.setTitle(self.setup_title)
        sleep(3)
        if config.plugins.stvcl.thumb.value == False:
            self.load_poster()

    def message1(self):
        global servicx
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None or '':
            return
        else:
            servicx = 'iptv'
            self.session.openWithCallback(self.check10, MessageBox, _("Do you want to Convert Bouquet IPTV?"), MessageBox.TYPE_YESNO)

    def message2(self):
        global servicx
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None or '':
            return
        else:
            servicx = 'gst'
            self.session.openWithCallback(self.check10, MessageBox, _("Do you want to Convert Bouquet GSTREAMER?"), MessageBox.TYPE_YESNO)

    def check10(self, result):
            global in_tmp, namebouquett
            print('in folder tmp : ', in_tmp)
            idx = self["list"].getSelectionIndex()
            if idx == -1 or None or '':
                return
            self.convert = True
            name = self.name + ' ' + self.names[idx]
            namebouquett = name.replace(' ','-').strip()
            print('namebouquett in folder tmp : ', namebouquett)
            try:
                sleep(3)
                if os.path.isfile(in_tmp) and os.stat(in_tmp).st_size > 0:
                    print('ChannelList is_tmp exist in playlist')
                    bqtname = 'userbouquet.%s.tv' % namebouquett.lower()
                    desk_tmp = ''
                    in_bouquets = 0
                    with open('/etc/enigma2/%s' % bqtname, 'w') as outfile:
                        outfile.write('#NAME %s\r\n' % namebouquett.capitalize())
                        if servicx == 'iptv':
                            for line in open(in_tmp):
                                if line.startswith('http://') or line.startswith('https'):
                                    outfile.write('#SERVICE 4097:0:1:1:0:0:0:0:0:0:%s' % line.replace(':', '%3a'))
                                    outfile.write('#DESCRIPTION %s' % desk_tmp)
                                elif line.startswith('#EXTINF'):
                                    desk_tmp = '%s' % line.split(',')[-1]
                                elif '<stream_url><![CDATA' in line:
                                    outfile.write('#SERVICE 4097:0:1:1:0:0:0:0:0:0:%s\r\n' % line.split('[')[-1].split(']')[0].replace(':', '%3a'))
                                    outfile.write('#DESCRIPTION %s\r\n' % desk_tmp)
                                elif '<title>' in line:
                                    if '<![CDATA[' in line:
                                        desk_tmp = '%s\r\n' % line.split('[')[-1].split(']')[0]
                                    else:
                                        desk_tmp = '%s\r\n' % line.split('<')[1].split('>')[1]
                        else:
                            if servicx == 'gst':
                                for line in open(in_tmp):
                                    if line.startswith('http://') or line.startswith('https'):
                                        outfile.write('#SERVICE 5002:0:1:1:0:0:0:0:0:0:%s' % line.replace(':', '%3a'))
                                        outfile.write('#DESCRIPTION %s' % desk_tmp)
                                    elif line.startswith('#EXTINF'):
                                        desk_tmp = '%s' % line.split(',')[-1]
                                    elif '<stream_url><![CDATA' in line:
                                        outfile.write('#SERVICE 5002:0:1:1:0:0:0:0:0:0:%s\r\n' % line.split('[')[-1].split(']')[0].replace(':', '%3a'))
                                        outfile.write('#DESCRIPTION %s\r\n' % desk_tmp)
                                    elif '<title>' in line:
                                        if '<![CDATA[' in line:
                                            desk_tmp = '%s\r\n' % line.split('[')[-1].split(']')[0]
                                        else:
                                            desk_tmp = '%s\r\n' % line.split('<')[1].split('>')[1]
                        outfile.close()
                    self.mbox = self.session.open(MessageBox, _('Check out the favorites list ...'), MessageBox.TYPE_INFO, timeout=5)
                    if os.path.isfile('/etc/enigma2/bouquets.tv'):
                        for line in open('/etc/enigma2/bouquets.tv'):
                            if bqtname in line:
                                in_bouquets = 1

                        if in_bouquets == 0:
                            if os.path.isfile('/etc/enigma2/%s' % bqtname) and os.path.isfile('/etc/enigma2/bouquets.tv'):
                                remove_line('/etc/enigma2/bouquets.tv', bqtname)
                                with open('/etc/enigma2/bouquets.tv', 'a') as outfile:
                                    outfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % bqtname)
                                    outfile.close()
                    self.mbox = self.session.open(MessageBox, _('Shuffle Favorite List in Progress') + '\n' + _('Wait please ...'), MessageBox.TYPE_INFO, timeout=5)
                    ReloadBouquet()
                else:
                    self.session.open(MessageBox, _('Conversion Failed!!!'), MessageBox.TYPE_INFO, timeout=5)
                    return
            except Exception as e:
                print('error convert iptv ',e)

    def cancel(self):
        if search_ok == True:
            self.resetSearch()
        else:
            self.close()

    def search_m3u(self):
        text = ''
        self.session.openWithCallback(
            self.filterM3u,
            VirtualKeyBoard,
            title = _("Filter this category..."),
            text=self.search)

    def filterM3u(self, result):
        if result:
            self.names = []
            self.urls = []
            self.pics = []
            pic = plugin_fold + "/res/pics/default.png"
            search = result
            try:
                f1 = open(in_tmp, "r+")
                fpage = f1.read()
                regexcat = "EXTINF.*?,(.*?)\\n(.*?)\\n"
                match = re.compile(regexcat, re.DOTALL).findall(fpage)
                for  name, url in match:
                    if str(search).lower() in name.lower():
                        global search_ok
                        search_ok = True
                        url = url.replace(" ", "")
                        url = url.replace("\\n", "")
                        self.names.append(name)
                        self.urls.append(url)
                        self.pics.append(pic)
                if search_ok == True:
                    m3ulist(self.names, self["list"])
                    self["live"].setText('N.' + str(len(self.names)) + " Stream")
                else:
                    search_ok = False
                    self.resetSearch()
            except:
                pass
        else:
            self.playList()

    def resetSearch(self):
        global re_search
        re_search = False
        if len(self.names):
            for x in self.names:
                del x
        self.playList()

    def runRec(self):
        global urlm3u, namem3u
        idx = self["list"].getSelectionIndex()
        namem3u = self.names[idx]
        urlm3u = self.urls[idx]
        if idx == -1 or None or '':
            return
        if self.downloading == True:
            self.session.open(MessageBox, _('You are already downloading!!!'), MessageBox.TYPE_INFO, timeout=5)
        else:
            if '.mp4' in urlm3u or '.mkv' in urlm3u or '.flv' in urlm3u or '.avi' in urlm3u :
                self.downloading = True
                self.session.openWithCallback(self.download_m3u, MessageBox, _("DOWNLOAD VIDEO?" ) , type=MessageBox.TYPE_YESNO, timeout = 10, default = False)
            else:
                self.downloading = False
                self.session.open(MessageBox, _('Only VOD Movie allowed or not .ext Filtered!!!'), MessageBox.TYPE_INFO, timeout=5)

    def download_m3u(self, result):
        if result:
            global in_tmp
            try:
                if self.downloading == True:
                    idx = self["list"].getSelectionIndex()
                    namem3u = self.names[idx]
                    urlm3u = self.urls[idx]
                    path = urlparse(urlm3u).path
                    ext = splitext(path)[1]
                    fileTitle = re.sub(r'[\<\>\:\"\/\\\|\?\*\[\]]', '_', namem3u)
                    fileTitle = re.sub(r' ', '_', fileTitle)
                    fileTitle = re.sub(r'_+', '_', fileTitle)
                    fileTitle = fileTitle.replace("(", "_").replace(")", "_").replace("#", "").replace("+", "_")
                    fileTitle = fileTitle.replace("\'", "_").replace("'", "_").replace("!", "_").replace("&", "_")
                    fileTitle = fileTitle.lower() + ext
                    in_tmp = Path_Movies + fileTitle
                    if os.path.isfile(in_tmp):
                        os.remove(in_tmp)
                    # urlretrieve(urlm3u, in_tmp)
                    # sleep(3)
                    self.download = downloadWithProgress(urlm3u, in_tmp)
                    self.download.addProgress(self.downloadProgress)
                    self.download.start().addCallback(self.check).addErrback(self.showError)
                else:
                    self.downloading = False
                    self.session.open(MessageBox, _('Download Failed!!!'), MessageBox.TYPE_INFO, timeout=5)
                    pass
                return
            except Exception as e:
                print('error m3u', e)

    def downloadProgress(self, recvbytes, totalbytes):
        self["progress"].show()
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))
        print('ChannelList downloadprogress ok')

    def check(self, fplug):
        self.downloading = False
        self['progresstext'].text = ''
        self.progclear = 0
        self['progress'].setValue(self.progclear)
        self["progress"].hide()
        print('ChannelList check ok')
        sleep(3)
        self.playList()

    def showError(self, error):
        self.downloading = False
        self.session.open(MessageBox, _('Download Failed!!!'), MessageBox.TYPE_INFO, timeout=5)
        print('ChannelList DownloadError')

    def downlist(self):
        global in_tmp
        namem3u = self.name
        urlm3u = self.url
        if six.PY3:
            urlm3u = six.ensure_str(urlm3u)
        print('urlmm33uu ', urlm3u)
        try:
            fileTitle = re.sub(r'[\<\>\:\"\/\\\|\?\*\[\]]', '_', namem3u)
            fileTitle = re.sub(r' ', '_', fileTitle)
            fileTitle = re.sub(r'_+', '_', fileTitle)
            fileTitle = fileTitle.replace("(", "_").replace(")", "_").replace("#", "").replace("+", "_").replace("\'", "_").replace("'", "_").replace("!", "_").replace("&", "_")
            fileTitle = fileTitle.lower() #+ ext
            in_tmp = Path_Movies + fileTitle + '.m3u'
            if os.path.isfile(in_tmp):
                os.remove(in_tmp)
            print('path tmp : ', in_tmp)
            urlretrieve(urlm3u, in_tmp)
            sleep(7)
            self.playList()
            # self.download = downloadWithProgress(urlm3u, in_tmp)
            # self.download.addProgress(self.downloadProgress)
            # self.download.start().addCallback(self.check).addErrback(self.showError)
            print('ChannelList Downlist sleep 3 - 2')        # return

        except Exception as e:
            print('errore e : ', e)
            # self.mbox = self.session.open(MessageBox, _('DOWNLOAD ERROR'), MessageBox.TYPE_INFO, timeout=5)
        return

    def playList(self):
        global search_ok
        search_ok = False
        self.names = []
        self.urls = []
        self.pics = []
        items = []
        # pic = resolveFilename(SCOPE_PLUGINS, "Extensions/stvcl/res/pics/{}".format('default.png'))
        pic = plugin_fold + "/res/pics/default.png"
        try:
            if os.path.isfile(in_tmp) and os.stat(in_tmp).st_size > 0:
                print('ChannelList is_tmp exist in playlist')
                f1 = open(in_tmp, 'r+')
                fpage = f1.read()
                # fpage.seek(0)
                # if "#EXTM3U" and 'tvg-logo' in fpage:
                if 'tvg-logo="http' in fpage:
                    print('tvg-logo in fpage: True')
                    #EXTINF:-1 tvg-id="externallinearfeed-04-21-2020-213519853-04-21-2020" tvg-logo="https://3gz8cg829c.execute-api.us-west-2.amazonaws.com/prod/image-renderer/16x9/full/600/center/90/5086119a-3424-4a9d-afc9-07cdcd962d4b-large16x9_STIRR_0721_EPG_MavTV_1920x1080.png?1625778769447?cb=c4ca4238a0b923820dcc509a6f75849b",MavTv
                    regexcat = 'EXTINF.*?tvg-logo="(.*?)".*?,(.*?)\\n(.*?)\\n'
                    match = re.compile(regexcat, re.DOTALL).findall(fpage)
                    for pic, name, url in match:
                        if url.startswith('http'):
                            url = url.replace(' ', '%20')
                            url = url.replace('\\n', '')
                            if 'samsung' in self.url.lower() or config.plugins.stvcl.filter.value == True:
                                regexcat = '(.*?).m3u8'
                                match = re.compile(regexcat, re.DOTALL).findall(url)
                                for url in match:
                                    url = url + '.m3u8'
                            # if pic.startswith('http'):
                            if pic.endswith('.png') or pic.endswith('.jpg'):
                                pic = pic
                            else:
                                pic = pic + '.png'
                            item = name + "###" + url + "###" + pic
                            print('url-name Items sort: ', item)
                            items.append(item)
                    items.sort()
                    for item in items:
                        name = item.split('###')[0]
                        url = item.split('###')[1]
                        pic = item.split('###')[2]

                        self.names.append(checkStr(name))
                        self.urls.append(checkStr(url))
                        self.pics.append(checkStr(pic))
                else:
                    regexcat = '#EXTINF.*?,(.*?)\\n(.*?)\\n'
                    match = re.compile(regexcat, re.DOTALL).findall(fpage)
                    for name, url in match:
                        if url.startswith('http'):
                            url = url.replace(' ', '%20')
                            url = url.replace('\\n', '')
                            if 'samsung' in self.url.lower() or config.plugins.stvcl.filter.value == True:
                                regexcat = '(.*?).m3u8'
                                match = re.compile(regexcat, re.DOTALL).findall(url)
                                for url in match:
                                    url = url + '.m3u8'
                            pic = pic
                            item = name + "###" + url + "###" + pic
                            print('url-name Items sort: ', item)
                            items.append(item)
                    items.sort()
                    for item in items:
                        name = item.split('###')[0]
                        url = item.split('###')[1]
                        pic = item.split('###')[2]

                        self.names.append(checkStr(name))
                        self.urls.append(checkStr(url))
                        self.pics.append(checkStr(pic))
                #####
                if config.plugins.stvcl.thumb.value == True:
                    self["live"].setText('N.' + str(len(self.names)) + " Stream")
                    self.gridmaint = eTimer()
                    try:
                        self.gridmaint.callback.append(self.gridpic)
                    except:
                        self.gridmaint_conn = self.gridmaint.timeout.connect(self.gridpic)
                    self.gridmaint.start(5000, True)
                    # self.session.open(GridMain, self.names, self.urls, self.pics)
                #####
                else:
                    m3ulist(self.names, self['list'])
                    self.load_poster()
                    self["live"].setText('N.' + str(len(self.names)) + " Stream")


        except Exception as ex:
            print('error exception: ', ex)

    def gridpic(self):
        self.session.open(GridMain, self.names, self.urls, self.pics)
        self.close()

    def runChannel(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None or '':
            return
        else:
            self.pin = True
            if config.ParentalControl.configured.value:
                a = '+18', 'adult', 'hot', 'porn', 'sex', 'xxx'
                if any(s in str(self.names[idx]).lower() for s in a):
                    self.allow2()
                else:
                    self.pin = True
                    self.pinEntered2(True)
            else:
                self.pin = True
                self.pinEntered2(True)

    def allow2(self):
        from Screens.InputBox import PinInput
        self.session.openWithCallback(self.pinEntered2, PinInput, pinList = [config.ParentalControl.setuppin.value], triesEntry = config.ParentalControl.retries.servicepin, title = _("Please enter the parental control pin code"), windowTitle = _("Enter pin code"))

    def pinEntered2(self, result):
        if not result:
            self.pin = False
            self.session.open(MessageBox, _("The pin code you entered is wrong."), type=MessageBox.TYPE_ERROR, timeout=5)
        self.runChannel2()

    def runChannel2(self):
        if self.pin is False:
            return
        else:
            idx = self['list'].getSelectionIndex()
            name = self.names[idx]
            url = self.urls[idx]
            self.session.open(M3uPlay2, name, url)
            return

    def play2(self):
        if os.path.isfile("/usr/sbin/streamlinksrv"):
            idx = self['list'].getSelectionIndex()
            name = self.names[idx]
            url = self.urls[idx]
            url = url.replace(':', '%3a')
            print('In revolution url =', url)
            ref = '5002:0:1:0:0:0:0:0:0:0:' + 'http%3a//127.0.0.1%3a8088/' + str(url)
            sref = eServiceReference(ref)
            print('SREF: ', sref)
            sref.setName(name)
            self.session.open(M3uPlay2, name, sref)
            self.close()
        else:
            self.session.open(MessageBox, _('Install Streamlink first'), MessageBox.TYPE_INFO, timeout=5)

    def AdjUrlFavo(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None or '':
            return

        else:
            name = self.names[idx]
            url = self.urls[idx]
            regexcat = '(.*?).m3u8'
            match = re.compile(regexcat, re.DOTALL).findall(url)
            for url in match:
                url = url + '.m3u8'
            self.session.open(AddIpvStream, name, url)

    def up(self):
        self[self.currentList].up()
        self.load_poster()

    def down(self):
        self[self.currentList].down()
        self.load_poster()

    def left(self):
        self[self.currentList].pageUp()
        self.load_poster()

    def right(self):
        self[self.currentList].pageDown()
        self.load_poster()

    def load_poster(self):
        idx = self['list'].getSelectionIndex()
        pic = self.pics[idx]
        pixmaps = defpic
        if pic and pic.find('http') == -1:
            self.poster_resize(pixmaps)
            return
        else:
            if pic.startswith('http'):
                pixmaps = str(pic)
                if six.PY3:
                    pixmaps = six.ensure_binary(pixmaps)
                print('pic xxxxxxxxxxxxx', pixmaps)
                path = urlparse(pixmaps).path
                ext = splitext(path)[1]
                pictmp = '/tmp/posterst' + str(ext)
                if fileExists(pictmp):
                    pictmp = '/tmp/posterst' + str(ext)
                try:
                    if pixmaps.startswith(b"https") and sslverify:
                        parsed_uri = urlparse(pixmaps)
                        domain = parsed_uri.hostname
                        sniFactory = SNIFactory(domain)
                        if six.PY3:
                            pixmaps = six.ensure_binary(pixmaps)
                        # if six.PY3:
                            # pixmaps = pixmaps.encode()
                        print('uurrll: ', pixmaps)
                        downloadPage(pixmaps, pictmp, sniFactory, timeout=5).addCallback(self.downloadPic, pictmp).addErrback(self.downloadError)
                    else:
                        downloadPage(pixmaps, pictmp).addCallback(self.downloadPic, pictmp).addErrback(self.downloadError)
                except Exception as ex:
                    print(ex)
                    print("Error: can't find file or read data")
        return

    def downloadError(self, raw):
        try:
            self.poster_resize(defpic)
        except Exception as ex:
            print(ex)
            print('exe downloadError')

    def downloadPic(self, data, pictmp):
        if fileExists(pictmp):
            try:
                self.poster_resize(pictmp)
            except Exception as ex:
                print("* error ** %s" % ex)
                pass

    def poster_resize(self, png):
        self["poster"].show()
        pixmaps = png
        if os.path.exists(pixmaps):
            size = self['poster'].instance.size()
            self.picload = ePicLoad()
            self.scale = AVSwitch().getFramebufferScale()
            self.picload.setPara([size.width(), size.height(), self.scale[0], self.scale[1], 0, 1, '#00000000'])
            if os.path.exists('/var/lib/dpkg/status'):
                self.picload.startDecode(pixmaps, False)
            else:
                self.picload.startDecode(pixmaps, 0, 0, False)
            ptr = self.picload.getData()
            if ptr != None:
                self['poster'].instance.setPixmap(ptr)
                self['poster'].show()
            else:
                print('no cover.. error')
            return

class TvInfoBarShowHide():
    """ InfoBar show/hide control, accepts toggleShow and hide actions, might start
    fancy animations. """
    STATE_HIDDEN = 0
    STATE_HIDING = 1
    STATE_SHOWING = 2
    STATE_SHOWN = 3
    skipToggleShow = False

    def __init__(self):
        self["ShowHideActions"] = ActionMap(["InfobarShowHideActions"], {"toggleShow": self.OkPressed,
         "hide": self.hide}, 0)
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evStart: self.serviceStarted})
        self.__state = self.STATE_SHOWN
        self.__locked = 0
        self.hideTimer = eTimer()
        try:
            self.hideTimer_conn = self.hideTimer.timeout.connect(self.doTimerHide)
        except:
            self.hideTimer.callback.append(self.doTimerHide)
        self.hideTimer.start(5000, True)
        self.onShow.append(self.__onShow)
        self.onHide.append(self.__onHide)

    def OkPressed(self):
        self.toggleShow()

    def toggleShow(self):
        if self.skipToggleShow:
            self.skipToggleShow = False
            return

        if self.__state == self.STATE_HIDDEN:
            self.show()
            self.hideTimer.stop()
        else:
            self.hide()
            self.startHideTimer()
    def serviceStarted(self):
        if self.execing:
            if config.usage.show_infobar_on_zap.value:
                self.doShow()

    def __onShow(self):
        self.__state = self.STATE_SHOWN
        self.startHideTimer()

    def startHideTimer(self):
        if self.__state == self.STATE_SHOWN and not self.__locked:
            self.hideTimer.stop()
            idx = config.usage.infobar_timeout.index
            if idx:
                self.hideTimer.start(idx * 1500, True)

    def __onHide(self):
        self.__state = self.STATE_HIDDEN
    def doShow(self):
        self.hideTimer.stop()
        self.show()
        self.startHideTimer()

    def doTimerHide(self):
        self.hideTimer.stop()
        if self.__state == self.STATE_SHOWN:
            self.hide()

    def lockShow(self):
        try:
            self.__locked += 1
        except:
            self.__locked = 0
        if self.execing:
            self.show()
            self.hideTimer.stop()
            self.skipToggleShow = False

    def unlockShow(self):
        try:
            self.__locked -= 1
        except:
            self.__locked = 0
        if self.__locked < 0:
            self.__locked = 0
        if self.execing:
            self.startHideTimer()

    def debug(obj, text = ""):
        print(text + " %s\n" % obj)

class M3uPlay2(InfoBarBase, InfoBarMenu, InfoBarSeek, InfoBarAudioSelection, InfoBarSubtitleSupport, InfoBarNotifications, TvInfoBarShowHide, Screen):
    STATE_IDLE = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    screen_timeout = 5000
    def __init__(self, session, name, url):
        global SREF, streml
        Screen.__init__(self, session)
        self.session = session
        self.skinName = 'MoviePlayer'
        title = name
        streaml = False
        for x in InfoBarBase, \
                InfoBarMenu, \
                InfoBarSeek, \
                InfoBarAudioSelection, \
                InfoBarSubtitleSupport, \
                InfoBarNotifications, \
                TvInfoBarShowHide:
            x.__init__(self)
        try:
            self.init_aspect = int(self.getAspect())
        except:
            self.init_aspect = 0
        self.new_aspect = self.init_aspect
        self['actions'] = ActionMap(['MoviePlayerActions',

         'MovieSelectionActions',
         'MediaPlayerActions',
         'EPGSelectActions',
         'MediaPlayerSeekActions',
         'SetupActions',
         'ColorActions',
         'InfobarShowHideActions',
         'InfobarActions',
         'InfobarSeekActions'], {'leavePlayer': self.cancel,
         'epg': self.showIMDB,
         'info': self.showIMDB,
         # 'info': self.cicleStreamType,
         'tv': self.cicleStreamType,
         'stop': self.cancel,
         'cancel': self.cancel,
         'back': self.cancel}, -1)
        self.url = url.replace(':', '%3a').replace(' ','%20')
        self.name = decodeHtml(name)
        self.state = self.STATE_PLAYING
        SREF = self.session.nav.getCurrentlyPlayingServiceReference()
        if '8088' in str(self.url):
            self.onFirstExecBegin.append(self.slinkPlay)
        else:
            self.onFirstExecBegin.append(self.cicleStreamType)
        self.onClose.append(self.cancel)

    def getAspect(self):
        return AVSwitch().getAspectRatioSetting()

    def getAspectString(self, aspectnum):
        return {0: _('4:3 Letterbox'),
         1: _('4:3 PanScan'),
         2: _('16:9'),
         3: _('16:9 always'),
         4: _('16:10 Letterbox'),
         5: _('16:10 PanScan'),
         6: _('16:9 Letterbox')}[aspectnum]

    def setAspect(self, aspect):
        map = {0: '4_3_letterbox',
         1: '4_3_panscan',
         2: '16_9',
         3: '16_9_always',
         4: '16_10_letterbox',
         5: '16_10_panscan',
         6: '16_9_letterbox'}
        config.av.aspectratio.setValue(map[aspect])
        try:
            AVSwitch().setAspectRatio(aspect)
        except:
            pass

    def av(self):
        temp = int(self.getAspect())
        temp = temp + 1
        if temp > 6:
            temp = 0
        self.new_aspect = temp
        self.setAspect(temp)

    def showinfo(self):
        sTitle = ''
        sServiceref = ''
        try:
            servicename, serviceurl = getserviceinfo(sref)
            if servicename != None:
                sTitle = servicename
            else:
                sTitle = ''
            if serviceurl != None:
                sServiceref = serviceurl
            else:
                sServiceref = ''
            currPlay = self.session.nav.getCurrentService()
            sTagCodec = currPlay.info().getInfoString(iServiceInformation.sTagCodec)
            sTagVideoCodec = currPlay.info().getInfoString(iServiceInformation.sTagVideoCodec)
            sTagAudioCodec = currPlay.info().getInfoString(iServiceInformation.sTagAudioCodec)
            message = 'stitle:' + str(sTitle) + '\n' + 'sServiceref:' + str(sServiceref) + '\n' + 'sTagCodec:' + str(sTagCodec) + '\n' + 'sTagVideoCodec:' + str(sTagVideoCodec) + '\n' + 'sTagAudioCodec: ' + str(sTagAudioCodec)
            self.mbox = self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        except:
            pass

        return
    def showIMDB(self):
        TMDB = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('TMDB'))
        IMDb = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('IMDb'))
        if os.path.exists(TMDB):
            from Plugins.Extensions.TMBD.plugin import TMBD
            text_clear = self.name
            text = charRemove(text_clear)
            self.session.open(TMBD, text, False)
        elif os.path.exists(IMDb):
            from Plugins.Extensions.IMDb.plugin import IMDB
            text_clear = self.name
            text = charRemove(text_clear)
            HHHHH = text
            self.session.open(IMDB, HHHHH)
        else:
            text_clear = self.name
            self.session.open(MessageBox, text_clear, MessageBox.TYPE_INFO)

    def slinkPlay(self, url):
        name = self.name
        ref = "{0}:{1}".format(url.replace(":", "%3A"), name.replace(":", "%3A"))
        print('final reference:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def openPlay(self, servicetype, url):
        name = self.name
        ref = "{0}:0:0:0:0:0:0:0:0:0:{1}:{2}".format(servicetype, url.replace(":", "%3A"), name.replace(":", "%3A"))
        print('reference:   ', ref)
        if streaml == True:
            url = 'http://127.0.0.1:8088/' + str(url)
            ref = "{0}:0:1:0:0:0:0:0:0:0:{1}:{2}".format(servicetype, url.replace(":", "%3A"), name.replace(":", "%3A"))
            print('streaml reference:   ', ref)
        print('final reference:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def cicleStreamType(self):
        global streaml
        streaml = False
        from itertools import cycle, islice
        self.servicetype = str(config.plugins.stvcl.services.value) #+':0:1:0:0:0:0:0:0:0:'#  '4097'
        print('servicetype1: ', self.servicetype)
        url = str(self.url)
        if str(os.path.splitext(self.url)[-1]) == ".m3u8":
            if self.servicetype == "1":
                self.servicetype = "4097"
        currentindex = 0
        streamtypelist = ["4097"]
        # if "youtube" in str(self.url):
            # self.mbox = self.session.open(MessageBox, _('For Stream Youtube coming soon!'), MessageBox.TYPE_INFO, timeout=5)
            # return
        if isStreamlinkAvailable():
            streamtypelist.append("5002") #ref = '5002:0:1:0:0:0:0:0:0:0:http%3a//127.0.0.1%3a8088/' + url
            streaml = True
        if os.path.exists("/usr/bin/gstplayer"):
            streamtypelist.append("5001")
        if os.path.exists("/usr/bin/exteplayer3"):
            streamtypelist.append("5002")
        if os.path.exists("/usr/bin/apt-get"):
            streamtypelist.append("8193")
        for index, item in enumerate(streamtypelist, start=0):
            if str(item) == str(self.servicetype):
                currentindex = index
                break
        nextStreamType = islice(cycle(streamtypelist), currentindex + 1, None)
        self.servicetype = str(next(nextStreamType))
        print('servicetype2: ', self.servicetype)
        self.openPlay(self.servicetype, url)

    def up(self):
        pass

    def down(self):
        # pass
        self.up()

    def doEofInternal(self, playing):
        self.close()

    def __evEOF(self):
        self.end = True

    def showVideoInfo(self):
        if self.shown:
            self.hideInfobar()
        if self.infoCallback != None:
            self.infoCallback()
        return

    def showAfterSeek(self):
        if isinstance(self, TvInfoBarShowHide):
            self.doShow()

    def cancel(self):
        if os.path.isfile('/tmp/hls.avi'):
            os.remove('/tmp/hls.avi')
        self.session.nav.stopService()
        self.session.nav.playService(SREF)
        if not self.new_aspect == self.init_aspect:
            try:
                self.setAspect(self.init_aspect)
            except:
                pass
        streaml = False
        self.close()

    def leavePlayer(self):
        self.close()



class AddIpvStream(Screen):
    def __init__(self, session, name, url):
        self.session = session
        skin = skin_path + '/AddIpvStream.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)
        self['title'] = Label(_(title_plug))
        self['Maintainer2'] = Label('%s' % Maintainer2)
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_('Ok'))
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self["key_yellow"].hide()
        self["key_blue"].hide()
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.keyOk,
         'cancel': self.keyCancel,
         'green': self.keyOk,
         'red': self.keyCancel}, -2)
        self['statusbar'] = Label()
        self.list = []
        self['menu'] = MenuList([])
        self.mutableList = None
        self.servicelist = ServiceList(None)
        self.onLayoutFinish.append(self.createTopMenu)
        self.namechannel = name
        self.urlchannel = url
        return

    def initSelectionList(self):
        self.list = []
        self['menu'].setList(self.list)

    def createTopMenu(self):
        self.setTitle(_('Add Stream IPTV'))
        self.initSelectionList()
        self.list = []
        tmpList = []
        self.list = self.getBouquetList()
        self['menu'].setList(self.list)
        self['statusbar'].setText(_('Select the Bouquet and press OK to add'))

    def getBouquetList(self):
        self.service_types = service_types_tv
        if config.usage.multibouquet.value:
            self.bouquet_rootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'
        else:
            self.bouquet_rootstr = '%s FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet' % self.service_types
        self.bouquet_root = eServiceReference(self.bouquet_rootstr)
        bouquets = []
        serviceHandler = eServiceCenter.getInstance()
        if config.usage.multibouquet.value:
            list = serviceHandler.list(self.bouquet_root)
            if list:
                while True:
                    s = list.getNext()
                    if not s.valid():
                        break
                    if s.flags & eServiceReference.isDirectory:
                        info = serviceHandler.info(s)
                        if info:
                            bouquets.append((info.getName(s), s))
                return bouquets
        else:
            info = serviceHandler.info(self.bouquet_root)
            if info:
                bouquets.append((info.getName(self.bouquet_root), self.bouquet_root))
            return bouquets
        return None

    def keyOk(self):
        if len(self.list) == 0:
            return
        self.name = ''
        self.url = ''
        self.session.openWithCallback(self.addservice, VirtualKeyBoard, title=_('Enter Name'), text=self.namechannel)

    def addservice(self, res):
        if res:
            self.url = res
            str = '4097:0:0:0:0:0:0:0:0:0:%s:%s' % (quote(self.url), quote(self.name))
            ref = eServiceReference(str)
            self.addServiceToBouquet(self.list[self['menu'].getSelectedIndex()][1], ref)
            self.close()

    def addServiceToBouquet(self, dest, service = None):
        mutableList = self.getMutableList(dest)
        if mutableList != None:
            if service is None:
                return
            if not mutableList.addService(service):
                mutableList.flushChanges()
        return

    def getMutableList(self, root = eServiceReference()):
        if self.mutableList != None:
            return self.mutableList
        else:
            serviceHandler = eServiceCenter.getInstance()
            if not root.valid():
                root = self.getRoot()
            list = root and serviceHandler.list(root)
            if list != None:
                return list.startEdit()
            return
            return

    def getRoot(self):
        return self.servicelist.getRoot()

    def keyCancel(self):
        self.close()

class OpenConfig(Screen, ConfigListScreen):
        def __init__(self, session):
            skin = skin_path + '/OpenConfig.xml'
            f = open(skin, 'r')
            self.skin = f.read()
            f.close()
            Screen.__init__(self, session)
            self.setup_title = _("stvcl Config")
            self.onChangedEntry = [ ]
            self.list = []
            self.session = session
            info = '***YOUR SETUP***'
            self['title'] = Label(_(title_plug))
            self['Maintainer2'] = Label('%s' % Maintainer2)
            self['key_red'] = Button(_('Back'))
            self['key_green'] = Button(_('Save'))
            self["key_blue"] = Button(_('Empty Pic Cache'))
            self['key_yellow'] = Button('')
            self['key_yellow'].hide()
            # self["key_blue"].hide()
            self['text'] = Label(info)
            self["description"] = Label(_(''))
            self['actions'] = ActionMap(["SetupActions", "ColorActions", "VirtualKeyboardActions"  ], {
                'cancel': self.extnok,
                "red": self.extnok,
                "green": self.cfgok,
                "blue": self.cachedel,
                # 'yellow': self.msgupdt1,
                'showVirtualKeyboard': self.KeyText,
                'ok': self.Ok_edit,
            }, -2)

            ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
            self.createSetup()
            # self.onLayoutFinish.append(self.checkUpdate)
            self.onLayoutFinish.append(self.layoutFinished)
            if self.setInfo not in self['config'].onSelectionChanged:
                self['config'].onSelectionChanged.append(self.setInfo)

        def layoutFinished(self):
            self.setTitle(self.setup_title)

        def cachedel(self):
            fold = config.plugins.stvcl.cachefold.value + "stvcl"
            cmd = "rm -rf " + tvstrvl + "/*"
            if os.path.exists(fold):
                os.system(cmd)
            self.mbox = self.session.open(MessageBox, _('All cache fold are empty!'), MessageBox.TYPE_INFO, timeout=5)

        def createSetup(self):
            self.editListEntry = None
            self.list = []
            self.list.append(getConfigListEntry(_('IPTV bouquets location '), config.plugins.stvcl.bouquettop, _("Configure position of the bouquets of the converted lists")))
            self.list.append(getConfigListEntry(_('Player folder List <.m3u>:'), config.plugins.stvcl.pthm3uf, _("Folder path containing the .m3u files")))
            self.list.append(getConfigListEntry(_('Services Player Reference type'), config.plugins.stvcl.services, _("Configure Service Player Reference")))
            self.list.append(getConfigListEntry(_('Filter M3U link regex type'), config.plugins.stvcl.filter, _("Set On for line link m3u full")))
            self.list.append(getConfigListEntry(_('Show thumpics?'), config.plugins.stvcl.thumb,  _("Show Thumbpics ? Enigma restart required")))
            if config.plugins.stvcl.thumb.value == True:
                self.list.append(getConfigListEntry(_('Download thumpics?'), config.plugins.stvcl.thumbpic, _("Download thumpics in Player M3U (is very Slow)?")))
            self.list.append(getConfigListEntry(_('Folder Cache for Thumbpics:'), config.plugins.stvcl.cachefold, _("Configure position folder for temporary Thumbpics")))
            self.list.append(getConfigListEntry(_('Link in Extensions Menu:'), config.plugins.stvcl.strtext, _("Show Plugin in Extensions Menu")))
            self.list.append(getConfigListEntry(_('Link in Main Menu:'), config.plugins.stvcl.strtmain, _("Show Plugin in Main Menu")))
            self['config'].list = self.list
            self["config"].setList(self.list)
            self.setInfo()

        def setInfo(self):
            entry = str(self.getCurrentEntry())
            if entry == _('IPTV bouquets location '):
                self['description'].setText(_("Configure position of the bouquets of the converted lists"))
                return
            if entry == _('Player folder List <.m3u>:'):
                self['description'].setText(_("Folder path containing the .m3u files"))
                return
            if entry == _('Filter M3U link regex type'):
                self['description'].setText(_("Set On for line link m3u full"))
                return
            if entry == _('Services Player Reference type'):
                self['description'].setText(_("Configure Service Player Reference"))
                return
            if entry == _('Show thumpics?'):
                self['description'].setText(_("Show Thumbpics ? Enigma restart required"))
                return
            if entry == _('Download thumpics?'):
                self['description'].setText(_("Download thumpics in Player M3U (is very Slow)?"))
                return
            if entry == _('Folder Cache for Thumbpics:'):
                self['description'].setText(_("Configure position folder for temporary Thumbpics"))
                return
            if entry == _('Link in Extensions Menu:'):
                self['description'].setText(_("Show Plugin in Extensions Menu"))
                return
            if entry == _('Link in Main Menu:'):
                self['description'].setText(_("Show Plugin in Main Menu"))
            return

        def changedEntry(self):
            sel = self['config'].getCurrent()
            for x in self.onChangedEntry:
                x()
            try:
                if isinstance(self['config'].getCurrent()[1], ConfigEnableDisable) or isinstance(self['config'].getCurrent()[1], ConfigYesNo) or isinstance(self['config'].getCurrent()[1], ConfigSelection):
                    self.createSetup()
            except:
                pass

        def getCurrentEntry(self):
            return self['config'].getCurrent() and self['config'].getCurrent()[0] or ''

        def getCurrentValue(self):
            return self['config'].getCurrent() and str(self['config'].getCurrent()[1].getText()) or ''

        def createSummary(self):
            from Screens.Setup import SetupSummary
            return SetupSummary

        def Ok_edit(self):
            ConfigListScreen.keyOK(self)
            sel = self['config'].getCurrent()[1]
            if sel and sel == config.plugins.stvcl.pthm3uf:
                self.setting = 'pthm3uf'
                self.openDirectoryBrowser(config.plugins.stvcl.pthm3uf.value)
            elif sel and sel == config.plugins.stvcl.cachefold:
                self.setting = 'cachefold'
                self.openDirectoryBrowser(config.plugins.stvcl.cachefold.value)
            else:
                pass

        def openDirectoryBrowser(self, path):
            try:
                self.session.openWithCallback(
                 self.openDirectoryBrowserCB,
                 LocationBox,
                 windowTitle=_('Choose Directory:'),
                 text=_('Choose Directory'),
                 currDir=str(path),
                 bookmarks=config.movielist.videodirs,
                 autoAdd=False,
                 editDir=True,
                 inhibitDirs=['/bin', '/boot', '/dev', '/home', '/lib', '/proc', '/run', '/sbin', '/sys', '/var'],
                 minFree=15)
            except Exception as ex:
                print(ex)

        def openDirectoryBrowserCB(self, path):
            if path != None:
                if self.setting == 'pthm3uf':
                    config.plugins.stvcl.pthm3uf.setValue(path)
                elif self.setting == 'cachefold':
                    config.plugins.stvcl.cachefold.setValue(path)
            return

        def cfgok(self):
            self.save()

        def save(self):
            if not os.path.exists(config.plugins.stvcl.pthm3uf.value):
                self.mbox = self.session.open(MessageBox, _('M3u list folder not detected!'), MessageBox.TYPE_INFO, timeout=4)
                return
            if self['config'].isChanged():
                for x in self['config'].list:
                    x[1].save()
                configfile.save()
                plugins.clearPluginList()
                plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
                self.mbox = self.session.open(MessageBox, _('Settings saved correctly!'), MessageBox.TYPE_INFO, timeout=5)
                self.close()
            else:
                self.close()

        def VirtualKeyBoardCallback(self, callback = None):
            if callback != None and len(callback):
                self["config"].getCurrent()[1].setValue(callback)
                self["config"].invalidate(self["config"].getCurrent())

        def KeyText(self):
            sel = self['config'].getCurrent()
            if sel:
                self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self['config'].getCurrent()[0], text=self['config'].getCurrent()[1].value)

        def cancelConfirm(self, result):
            if not result:
                return
            for x in self['config'].list:
                x[1].cancel()
            self.close()

        def extnok(self):
            if self['config'].isChanged():
                self.session.openWithCallback(self.cancelConfirm, MessageBox, _('Really close without saving the settings?'))
            else:
                self.close()

def checks():
    from Plugins.Extensions.stvcl.Utils import checkInternet
    checkInternet()
    chekin= False
    if checkInternet():
        chekin = True
    return chekin

def main(session, **kwargs):
    if checks:
        try:
           from Plugins.Extensions.stvcl.Update import upd_done
           upd_done()
        except:
               pass
        add_skin_font()
        session.open(OpenScript)
    else:
        session.open(MessageBox, "No Internet", MessageBox.TYPE_INFO)

def cfgmain(menuid):
    if menuid == 'mainmenu':
        return [('S.T.V.C.L.',
         main,
         'Smart TV Channels List',
         44)]
    else:
        return []

def Plugins(**kwargs):
    piclogox = 'logo.png'
    if not os.path.exists('/var/lib/dpkg/status'):
        piclogox = skin_path + '/logo.png'
    extDescriptor = PluginDescriptor(name=name_plug, description=_(title_plug), where=PluginDescriptor.WHERE_EXTENSIONSMENU, icon=piclogox, fnc=main)
    mainDescriptor = PluginDescriptor(name=name_plug, description=_(title_plug), where=PluginDescriptor.WHERE_MENU, icon=piclogox, fnc=cfgmain)
    result = [PluginDescriptor(name=name_plug, description=_(title_plug), where=[PluginDescriptor.WHERE_PLUGINMENU], icon=piclogox, fnc=main)]
    if config.plugins.stvcl.strtext.value:
        result.append(extDescriptor)
    if config.plugins.stvcl.strtmain.value:
        result.append(mainDescriptor)
    return result
