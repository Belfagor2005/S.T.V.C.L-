#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Info http://t.me/tivustream
****************************************
*        coded by Lululla              *
*                                      *
*             02/09/2024               *
****************************************
'''
from __future__ import print_function
from . import _, paypal, scramble, installer_url, developer_url
from . import Utils
from . import html_conv
from .Console import Console as xConsole

from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.config import (
    config,
    ConfigSubsection,
    ConfigSelection,
    getConfigListEntry,
    ConfigDirectory,
    ConfigYesNo,
    configfile,
    ConfigEnableDisable,
)
from Components.Button import Button
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import (MultiContentEntryText, MultiContentEntryPixmapAlphaTest)
from Components.Pixmap import Pixmap, MovingPixmap
from Components.PluginComponent import plugins
from Components.ProgressBar import ProgressBar
from Components.ServiceEventTracker import (ServiceEventTracker, InfoBarBase)
from Components.ServiceList import ServiceList
from Components.Sources.Progress import Progress
from Components.Sources.StaticText import StaticText
from PIL import Image
from Screens.InfoBarGenerics import (
    InfoBarMenu,
    InfoBarSeek,
    InfoBarAudioSelection,
    InfoBarNotifications,
    InfoBarSubtitleSupport,
)
from Screens.LocationBox import LocationBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.Directories import SCOPE_PLUGINS, resolveFilename
from Tools.Downloader import downloadWithProgress
from enigma import (
    RT_VALIGN_CENTER,
    RT_HALIGN_LEFT,
    eListboxPythonMultiContent,
    eTimer,
    ePicLoad,
    eServiceCenter,
    eServiceReference,
    loadPNG,
    gFont,
    iPlayableService,
    getDesktop,
)
from os.path import splitext, exists as file_exists
from time import sleep
from twisted.web.client import downloadPage
from requests import get, exceptions
from requests.exceptions import HTTPError as httperror
from twisted.internet.reactor import callInThread
from datetime import datetime
import codecs
import json
import os
import re
import requests
import six
import ssl
import sys
PY3 = False

try:
    from urllib.parse import quote, urlparse
    from urllib.request import Request, urlopen
    from urllib.error import URLError
    PY3 = True
    unicode = str
except ImportError:
    from urllib import quote
    from urlparse import urlparse
    from urllib2 import Request, urlopen, URLError


if sys.version_info >= (2, 7, 9):
    try:
        import ssl
        sslContext = ssl._create_unverified_context()
    except:
        sslContext = None

try:
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


def ssl_urlopen(url):
    if sslContext:
        return urlopen(url, context=sslContext)
    else:
        return urlopen(url)


def downloadFilest(url, target):
    try:
        if isinstance(url, bytes):
            url = url.decode('utf-8')  # Decodifica se è una byte string
        req = Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        # response = ssl_urlopen(req)
        response = urlopen(req, None, 15)
        with open(target, 'w') as output:
            if PY3:
                output.write(response.read().decode('utf-8'))
            else:
                output.write(response.read())
            print('response: ', response)
        return True
    except httperror:
        print('HTTP Error code: ', httperror.code)
    except URLError as e:
        print('URL Error: ', e.reason)
    except ValueError as ve:
        print("Errore di valore:", ve)


# ================
global Path_Movies, defpic
# ================
sessions = []
currversion = '1.4'
title_plug = 'Smart Tv Channels List'
name_plug = '..:: Smart Tv Channels List  V.%s ::.. ' % currversion
plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('stvcl'))
Maintainer2 = 'Maintener @Lululla'
dir_enigma2 = '/etc/enigma2/'
service_types_tv = '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 31) || (type == 134) || (type == 195)'
defpic = os.path.join(plugin_path, 'res/pics/default.png')
dblank = os.path.join(plugin_path, 'res/pics/blankL.png')
Panel_list = [('S.T.V.C.L.')]

modechoices = [("4097", _("ServiceMp3(4097)")),
               ("1", _("Hardware(1)"))]
if os.path.exists("/usr/bin/gstplayer"):
    modechoices.append(("5001", _("Gstreamer(5001)")))
if os.path.exists("/usr/bin/exteplayer3"):
    modechoices.append(("5002", _("Exteplayer3(5002)")))
if os.path.exists("/usr/sbin/streamlinksrv"):
    modechoices.append(("5002", _("Streamlink(5002)")))
if os.path.exists("/usr/bin/apt-get"):
    modechoices.append(("8193", _("eServiceUri(8193)")))

config.plugins.stvcl = ConfigSubsection()
cfg = config.plugins.stvcl
cfg.pthm3uf = ConfigDirectory(default='/media/hdd/movie/')
cfg.cachefold = ConfigDirectory('/media/hdd/', False)
cfg.bouquettop = ConfigSelection(default='Bottom', choices=['Bottom', 'Top'])
cfg.services = ConfigSelection(default='4097', choices=modechoices)
cfg.filterx = ConfigYesNo(default=False)
cfg.strtext = ConfigYesNo(default=True)
cfg.strtmain = ConfigYesNo(default=True)
cfg.thumb = ConfigYesNo(default=False)
cfg.thumbpic = ConfigYesNo(default=False)

try:
    from Components.UsageConfig import defaultMoviePath
    downloadpath = defaultMoviePath()
    cfg.pthm3uf = ConfigDirectory(default=downloadpath)
    # cfg.cachefold = str(cfg.pthm3uf.value)
except:
    if os.path.exists("/usr/bin/apt-get"):
        cfg.pthm3uf = ConfigDirectory(default='/media/hdd/movie/')
        # cfg.cachefold = str(cfg.pthm3uf.value)


# tvstrvl = str(cfg.cachefold.value).replace('movie', 'stvcl')
tvstrvl = os.path.join(cfg.cachefold.value, "stvcl")
tmpfold = os.path.join(tvstrvl, "tmp")
picfold = os.path.join(tvstrvl, "pic")

Path_Movies = str(cfg.pthm3uf.value)
if not Path_Movies.endswith(os.path.sep):
    Path_Movies += os.path.sep

for folder in [tvstrvl, tmpfold, picfold]:
    if not os.path.exists(folder):
        os.makedirs(folder)


screenwidth = getDesktop(0).size()
if screenwidth.width() == 2560:
    skin_path = plugin_path + '/res/skins/uhd/'
    defpic = plugin_path + '/res/pics/defaultL.png'

elif screenwidth.width() == 1920:
    skin_path = plugin_path + '/res/skins/fhd/'
    defpic = plugin_path + '/res/pics/defaultL.png'
else:
    skin_path = plugin_path + '/res/skins/hd/'
    defpic = plugin_path + '/res/pics/default.png'
if os.path.exists('/var/lib/dpkg/status'):
    skin_path = os.path.join(skin_path, 'dreamOs')


# ================Gui list
class mainList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        if screenwidth.width() == 2560:
            self.l.setItemHeight(450)
            textfont = int(90)
            self.l.setFont(0, gFont('Regular', textfont))
        elif screenwidth.width() == 1920:
            self.l.setItemHeight(370)
            textfont = int(70)
            self.l.setFont(0, gFont('Regular', textfont))
        else:
            self.l.setItemHeight(240)
            textfont = int(50)
            self.l.setFont(0, gFont('Regular', textfont))


class tvList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        if screenwidth.width() == 2560:
            self.l.setItemHeight(60)
            textfont = int(42)
            self.l.setFont(0, gFont('Regular', textfont))
        elif screenwidth.width() == 1920:
            self.l.setItemHeight(50)
            textfont = int(30)
            self.l.setFont(0, gFont('Regular', textfont))
        else:
            self.l.setItemHeight(45)
            textfont = int(24)
            self.l.setFont(0, gFont('Regular', textfont))


def m3ulistEntry(download):
    res = [download]
    png = os.path.join(plugin_path, 'res/pics/setting2.png')
    if screenwidth.width() == 2560:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(50, 50), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(90, 0), size=(1200, 50), font=0, text=download, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    elif screenwidth.width() == 1920:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(40, 40), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(70, 0), size=(1000, 50), font=0, text=download, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 0), size=(50, 40), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(65, 0), size=(500, 45), font=0, text=download, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res


def m3ulist(data, list):
    icount = 0
    mlist = []
    for line in data:
        name = data[icount]
        mlist.append(m3ulistEntry(name))
        icount += 1
    list.setList(mlist)


def tvListEntry(name, png):
    res = [name]
    png1 = os.path.join(plugin_path, 'res/pics/defaultL.png')
    png2 = os.path.join(plugin_path, 'res/pics/default.png')

    if screenwidth.width() == 2560:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(320, 450), png=loadPNG(png1)))
        res.append(MultiContentEntryText(pos=(400, 5), size=(1200, 70), font=0, text=name, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    elif screenwidth.width() == 1920:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(250, 370), png=loadPNG(png1)))
        res.append(MultiContentEntryText(pos=(280, 5), size=(1000, 70), font=0, text=name, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(3, 3), size=(165, 240), png=loadPNG(png2)))
        res.append(MultiContentEntryText(pos=(175, 3), size=(500, 50), font=0, text=name, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res


def returnIMDB(text_clear):
    TMDB = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('TMDB'))
    tmdb = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('tmdb'))
    IMDb = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('IMDb'))
    text = html_conv.html_unescape(text_clear)
    if os.path.exists(TMDB):
        try:
            from Plugins.Extensions.TMBD.plugin import TMBD
            _session.open(TMBD.tmdbScreen, text, 0)
        except Exception as e:
            print("[XCF] Tmdb: ", str(e))
        return True

    elif os.path.exists(tmdb):
        try:
            from Plugins.Extensions.tmdb.plugin import tmdb
            _session.open(tmdb.tmdbScreen, text, 0)
        except Exception as e:
            print("[XCF] Tmdb: ", str(e))
        return True

    elif os.path.exists(IMDb):
        try:
            from Plugins.Extensions.IMDb.plugin import main as imdb
            imdb(_session, text)
        except Exception as e:
            print("[XCF] imdb: ", str(e))
        return True
    else:
        _session.open(MessageBox, text, MessageBox.TYPE_INFO)
        return True
    return False


class StvclMain(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        skin = os.path.join(skin_path, 'StvclMain.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self['list'] = mainList([])
        self.icount = 0
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
        self.downloading = False
        self.setTitle(name_plug)
        self['title'] = Label(name_plug)
        self['Maintainer2'] = Label(Maintainer2)
        self['path'] = Label(_('Folder path %s' % str(Path_Movies)))
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button()
        self['key_yellow'] = Button(_('Update'))
        self["key_blue"] = Button(_('Remove'))
        self["key_green"].hide()
        self["key_yellow"].hide()
        self["key_blue"].hide()
        self.Update = False
        self['actions'] = ActionMap(['OkCancelActions',
                                     'DirectionActions',
                                     'HotkeyActions',
                                     'InfobarEPGActions',
                                     'ChannelSelectBaseActions',
                                     'MenuActions'], {'ok': self.okRun,
                                                      'menu': self.scsetup,
                                                      'back': self.exit,
                                                      'cancel': self.exit,
                                                      'yellow': self.update_me,  # update_me,
                                                      'green': self.update_dev,
                                                      'blue': self.msgdeleteBouquets,
                                                      'yellow_long': self.update_dev,
                                                      'info_long': self.update_dev,
                                                      'infolong': self.update_dev,
                                                      'showEventInfoPlugin': self.update_dev,
                                                      'red': self.exit}, -1)
        self.timer = eTimer()
        if os.path.exists('/var/lib/dpkg/status'):
            self.timer_conn = self.timer.timeout.connect(self.check_vers)
        else:
            self.timer.callback.append(self.check_vers)
        self.timer.start(200, True)
        self.onLayoutFinish.append(self.updateMenuList)

    def check_vers(self):
        remote_version = '0.0'
        remote_changelog = ''
        req = Utils.Request(Utils.b64decoder(installer_url), headers={'User-Agent': 'Mozilla/5.0'})
        page = Utils.urlopen(req).read()
        if PY3:
            data = page.decode("utf-8")
        else:
            data = page.encode("utf-8")
        if data:
            lines = data.split("\n")
            for line in lines:
                if line.startswith("version"):
                    remote_version = line.split("=")
                    remote_version = line.split("'")[1]
                if line.startswith("changelog"):
                    remote_changelog = line.split("=")
                    remote_changelog = line.split("'")[1]
                    break
        self.new_version = remote_version
        self.new_changelog = remote_changelog
        # if float(currversion) < float(remote_version):
        if currversion < remote_version:
            self.Update = True
            self['key_yellow'].show()
            # self['key_green'].show()
            self.session.open(MessageBox, _('New version %s is available\n\nChangelog: %s\n\nPress info_long or yellow_long button to start force updating.') % (self.new_version, self.new_changelog), MessageBox.TYPE_INFO, timeout=5)
        # self.update_me()

    def update_me(self):
        if self.Update is True:
            self.session.openWithCallback(self.install_update, MessageBox, _("New version %s is available.\n\nChangelog: %s \n\nDo you want to install it now?") % (self.new_version, self.new_changelog), MessageBox.TYPE_YESNO)
        else:
            self.session.open(MessageBox, _("Congrats! You already have the latest version..."),  MessageBox.TYPE_INFO, timeout=4)

    def update_dev(self):
        try:
            req = Utils.Request(Utils.b64decoder(developer_url), headers={'User-Agent': 'Mozilla/5.0'})
            page = Utils.urlopen(req).read()
            data = json.loads(page)
            remote_date = data['pushed_at']
            strp_remote_date = datetime.strptime(remote_date, '%Y-%m-%dT%H:%M:%SZ')
            remote_date = strp_remote_date.strftime('%Y-%m-%d')
            self.session.openWithCallback(self.install_update, MessageBox, _("Do you want to install update ( %s ) now?") % (remote_date), MessageBox.TYPE_YESNO)
        except Exception as e:
            print('error xcons:', e)

    def install_update(self, answer=False):
        if answer:
            cmd1 = 'wget -q "--no-check-certificate" ' + Utils.b64decoder(installer_url) + ' -O - | /bin/sh'
            self.session.open(xConsole, 'Upgrading...', cmdlist=[cmd1], finishedCallback=self.myCallback, closeOnSuccess=False)
        else:
            self.session.open(MessageBox, _("Update Aborted!"),  MessageBox.TYPE_INFO, timeout=3)

    def myCallback(self, result=None):
        print('result:', result)
        return

    def updateMenuList(self):
        self.menu_list = []
        for x in self.menu_list:
            del self.menu_list[0]
        list = []
        idx = 0
        png = os.path.join(plugin_path, 'res/pics/setting.png')
        for x in Panel_list:
            list.append(tvListEntry(x, png))
            self.menu_list.append(x)
            idx += 1
        self["key_green"].show()
        self["key_blue"].show()
        self['list'].setList(list)

    def okRun(self):
        self.keyNumberGlobalCB(self['list'].getSelectedIndex())

    def keyNumberGlobalCB(self, idx):
        sel = self.menu_list[idx]
        url = ''
        if sel == ("S.T.V.C.L."):
            url = Utils.b64decoder(scramble)
        else:
            return
        self.downlist(sel, url)

    def msgdeleteBouquets(self):
        self.session.openWithCallback(self.deleteBouquets, MessageBox, _("Remove all S.T.V.C.L. Favorite Bouquet ?"), MessageBox.TYPE_YESNO, timeout=5, default=True)

    def deleteBouquets(self, result):
        """
        Clean up routine to remove any previously made changes
        """
        if result:
            try:
                for fname in os.listdir(dir_enigma2):
                    if 'userbouquet.stvcl_' in fname:
                        # os.remove(os.path.join(dir_enigma2, fname))
                        Utils.purge(dir_enigma2, fname)
                    elif 'bouquets.tv.bak' in fname:
                        # os.remove(os.path.join(dir_enigma2, fname))
                        Utils.purge(dir_enigma2, fname)
                os.rename(os.path.join(dir_enigma2, 'bouquets.tv'), os.path.join(dir_enigma2, 'bouquets.tv.bak'))
                tvfile = open(os.path.join(dir_enigma2, 'bouquets.tv'), 'w+')
                bakfile = open(os.path.join(dir_enigma2, 'bouquets.tv.bak'))
                for line in bakfile:
                    if '.stvcl_' not in line:
                        tvfile.write(line)
                bakfile.close()
                tvfile.close()
                self.mbox = self.session.open(MessageBox, _('HasBahCa Favorites List have been removed'), MessageBox.TYPE_INFO, timeout=5)
                Utils.ReloadBouquets()
            except Exception as ex:
                print(str(ex))
                raise

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
        content = Utils.checkStr(url.strip())
        if PY3:
            content.encode()
        print('urlmm33uu ', content)
        try:
            fileTitle = re.sub(r'[<>:"/\\|?*\[\]]', '_', namem3u)  # Sostituisce i caratteri non permessi
            fileTitle = re.sub(r'[\s\(\)#\'\+\!&]', '_', fileTitle)  # Sostituisce spazi e altri caratteri con underscore
            fileTitle = re.sub(r'_+', '_', fileTitle)  # Rimuove underscore ripetuti
            fileTitle = fileTitle.lower()  # Converte tutto in minuscolo
            in_tmp = os.path.join(Path_Movies, fileTitle + '.m3u')
            if os.path.isfile(in_tmp):
                os.remove(in_tmp)
            downloadFilest(content, in_tmp)
            sleep(3)  # Attende il completamento del download
            self.session.open(ListM3u1, namem3u, content)
        except Exception as e:
            print('Errore: ', e)

    def scsetup(self):
        self.session.open(OpenConfig)

    def exit(self):
        Utils.deletetmp()
        self.close()


class ListM3u1(Screen):
    def __init__(self, session, namem3u, url):
        Screen.__init__(self, session)
        self.session = session
        skin = os.path.join(skin_path, 'ListM3u.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.list = []
        self['list'] = tvList([])
        global SREF
        SREF = self.session.nav.getCurrentlyPlayingServiceReference()
        self['title'] = Label(title_plug + ' ' + namem3u)
        self['Maintainer2'] = Label(Maintainer2)
        self['path'] = Label(_('Folder path %s' % str(Path_Movies)))
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
        self.downloading = False
        self.convert = False
        self.url = url
        self.name = namem3u
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_('Select'))
        self['key_yellow'] = Button()
        self["key_blue"] = Button()
        self["key_green"].hide()
        self["key_yellow"].hide()
        self["key_blue"].hide()
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'ButtonSetupActions',
                                     'DirectionActions'], {'cancel': self.cancel,
                                                           'ok': self.runList}, -2)
        if not os.path.exists(Path_Movies):
            self.mbox = self.session.open(MessageBox, _('Check in your Config Plugin - Path Movie'), MessageBox.TYPE_INFO, timeout=5)
            self.scsetup()
        # self.onFirstExecBegin.append(self.openList)
        # sleep(3)
        self.timer = eTimer()
        if os.path.exists('/var/lib/dpkg/status'):
            self.timer_conn = self.timer.timeout.connect(self.openList)
        else:
            self.timer.callback.append(self.openList)
        self.timer.start(200, True)
        # self.onLayoutFinish.append(self.openList2)
        self.onLayoutFinish.append(self.passing)

    def passing(self):
        pass

    def scsetup(self):
        self.session.openWithCallback(self.close, OpenConfig)

    def openList(self):
        self.names = []
        self.urls = []

        if sys.version_info.major == 3:
            import urllib.request as urllib2
        elif sys.version_info.major == 2:
            import urllib2
        req = urllib2.Request(self.url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        r = urllib2.urlopen(req, None, 15)
        content = r.read()
        r.close()
        if str(type(content)).find('bytes') != -1:
            try:
                content = content.decode("utf-8")
            except Exception as e:
                print("Error: ", e)
        try:
            # items = []
            self.names.append('Adelaide')
            self.urls.append('https://i.mjh.nz/au/Adelaide/')
            self.names.append('Brisbane')
            self.urls.append('https://i.mjh.nz/au/Brisbane')
            self.names.append('Canberra')
            self.urls.append('https://i.mjh.nz/au/Canberra')
            self.names.append('Darwin')
            self.urls.append('https://i.mjh.nz/au/Darwin')
            self.names.append('Hobart')
            self.urls.append('https://i.mjh.nz/au/Hobart')
            self.names.append('Melbourne')
            self.urls.append('https://i.mjh.nz/au/Melbourne')
            self.names.append('Perth')
            self.urls.append('https://i.mjh.nz/au/Perth')
            self.names.append('Sydney')
            self.urls.append('https://i.mjh.nz/au/Sydney')
            self.names.append('Au All')
            self.urls.append('https://i.mjh.nz/au/all')

            regexvideo = '<a href="(.*?)">'
            match = re.compile(regexvideo, re.DOTALL).findall(content)
            for url in match:
                if '..' in url:
                    continue
                if 'DONATE' in url:
                    continue
                if 'SUPPORT' in url:
                    continue
                name = url.replace('/', '')
                url = self.url + url  # + '/'
                self.urls.append(Utils.checkStr(url.strip()))
                self.names.append(Utils.checkStr(name.strip()))
            m3ulist(self.names, self['list'])
            self["key_green"].show()
        except Exception as e:
            print('error: ', e)

    def runList(self):
        i = len(self.names)
        if i < 0:
            return
        idx = self["list"].getSelectionIndex()
        sel = self.names[idx]
        urlm3u = self.urls[idx]
        self.session.open(ListM3u, sel, urlm3u)

    def cancel(self):
        self.close()


class ListM3u(Screen):
    def __init__(self, session, namem3u, url):
        Screen.__init__(self, session)
        self.session = session
        skin = os.path.join(skin_path, 'ListM3u.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.list = []
        self['list'] = tvList([])
        global SREF
        SREF = self.session.nav.getCurrentlyPlayingServiceReference()
        self['title'] = Label(title_plug + ' ' + namem3u)
        self['Maintainer2'] = Label(Maintainer2)
        self['path'] = Label(_('Folder path %s' % str(Path_Movies)))
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
        self.downloading = False
        self.convert = False
        self.url = url
        self.name = namem3u
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_('Select'))
        self['key_yellow'] = Button()
        self["key_blue"] = Button()
        self["key_green"].hide()
        self["key_yellow"].hide()
        self["key_blue"].hide()
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'ButtonSetupActions',
                                     'DirectionActions'], {'cancel': self.cancel,
                                                           'ok': self.runList}, -2)
        if not os.path.exists(Path_Movies):
            self.mbox = self.session.open(MessageBox, _('Check in your Config Plugin - Path Movie'), MessageBox.TYPE_INFO, timeout=5)
            self.scsetup()

        self.timer = eTimer()
        if os.path.exists('/var/lib/dpkg/status'):
            self.timer_conn = self.timer.timeout.connect(self.openList)
        else:
            self.timer.callback.append(self.openList)
        self.timer.start(200, True)
        self.onLayoutFinish.append(self.passing)

    def passing(self):
        pass

    def scsetup(self):
        self.session.openWithCallback(self.close, OpenConfig)

    def openList(self):
        self.names = []
        self.urls = []
        try:
            if sys.version_info.major == 3:
                import urllib.request as urllib2
            elif sys.version_info.major == 2:
                import urllib2
            req = urllib2.Request(self.url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
            r = urllib2.urlopen(req, None, 15)
            content = r.read()
            r.close()
            if str(type(content)).find('bytes') != -1:
                try:
                    content = content.decode("utf-8")
                except Exception as e:
                    print("Error: ", e)

            regexvideo = '<a href="(.*?)">.*?</a>.*?-(.*?)-(.*?) '
            match = re.compile(regexvideo, re.DOTALL).findall(content)
            items = []
            for url, mm, aa in match:
                if '.m3u8' in url:
                    name = url.replace('.m3u8', '')
                    name = name + ' ' + mm + '-' + aa
                    url = self.url + url
                    item = name + "###" + url + '\n'
                    items.append(item)
            items.sort()
            for item in items:
                name = item.split('###')[0]
                url = item.split('###')[1]
                self.urls.append(Utils.checkStr(url.strip()))
                self.names.append(Utils.checkStr(name.strip()))
            self["key_green"].show()
            m3ulist(self.names, self['list'])
        except Exception as e:
            print('error: ', e)

    def runList(self):
        i = len(self.names)
        if i < 0:
            return
        idx = self["list"].getSelectionIndex()
        sel = self.names[idx]
        urlm3u = self.urls[idx]
        self.session.open(ChannelList, sel, urlm3u)

    def cancel(self):
        self.close()


class ChannelList(Screen):
    def __init__(self, session, name, url):
        Screen.__init__(self, session)
        self.session = session
        skin = os.path.join(skin_path, 'ChannelList.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.list = []
        self['list'] = tvList([])
        self.setTitle(title_plug + ' ' + name)
        self['title'] = Label(title_plug + ' ' + name)
        self['Maintainer2'] = Label(Maintainer2)
        self['path'] = Label(_('Folder path %s' % str(Path_Movies)))
        service = cfg.services.value
        self['service'] = Label(_('Service Reference used %s') % service)
        self['live'] = Label()
        self['poster'] = Pixmap()
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_('Convert ExtePlayer3'))
        self['key_yellow'] = Button(_('Convert Gstreamer'))
        self["key_blue"] = Button(_("Search"))
        self["key_green"].hide()
        self["key_yellow"].hide()
        self["key_blue"].hide()
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
        self.downloading = False
        self.pin = False
        global in_tmp
        global search_ok
        self.servicx = 'gst'
        search_ok = False
        in_tmp = Path_Movies
        self.search = ''
        self.name = name
        self.url = url
        self.names = []
        self.urls = []
        self.pics = []
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'InfobarInstantRecord',
                                     'MenuActions',
                                     'ButtonSetupActions',
                                     'TimerEditActions',
                                     'DirectionActions'], {'red': self.cancel,
                                                           # 'green': self.runRec,
                                                           'menu': self.AdjUrlFavo,
                                                           'green': self.message2,
                                                           'yellow': self.message1,
                                                           'cancel': self.cancel,
                                                           'up': self.up,
                                                           'down': self.down,
                                                           'left': self.left,
                                                           'right': self.right,
                                                           'blue': self.search_m3u,
                                                           'rec': self.runRec,
                                                           'instantRecord': self.runRec,
                                                           'ShortRecord': self.runRec,
                                                           'ok': self.runChannel}, -2)
        self.currentList = 'list'
        print('ChannelList sleep 4 - 1')
        self.timer = eTimer()
        if os.path.exists('/var/lib/dpkg/status'):
            self.timer_conn = self.timer.timeout.connect(self.downlist)
        else:
            self.timer.callback.append(self.downlist)
        self.timer.start(200, True)
        self.onLayoutFinish.append(self.__layoutFinished)

    def __layoutFinished(self):
        pass

    def message1(self):
        i = len(self.names)
        if i < 0:
            return
        self.servicx = 'iptv'
        self.session.openWithCallback(self.check10, MessageBox, _("Do you want to Convert Bouquet IPTV?"), MessageBox.TYPE_YESNO)

    def message2(self):
        i = len(self.names)
        if i < 0:
            return
        self.servicx = 'gst'
        self.session.openWithCallback(self.check10, MessageBox, _("Do you want to Convert Bouquet GSTREAMER?"), MessageBox.TYPE_YESNO)

    def check10(self, result):
        if result:
            print('in folder tmp : ', in_tmp)
            idx = self["list"].getSelectionIndex()
            if idx == -1 or None or '':
                return
            self.convert = True
            if self.servicx == 'iptv':
                service = '4097'
            else:
                service = '5002'
            namebouquett = self.name.replace(' ', '_').replace('-', '_').strip()
            print('namebouquett in folder tmp : ', namebouquett)
            try:
                sleep(3)
                if os.path.isfile(in_tmp) and os.stat(in_tmp).st_size > 0:
                    bqtname = 'userbouquet.stvcl_%s.tv' % namebouquett.lower()
                    desk_tmp = ''
                    in_bouquets = 0
                    with open('%s%s' % (dir_enigma2, bqtname), 'w') as outfile:
                        outfile.write('#NAME %s\r\n' % namebouquett.capitalize())
                        # if self.servicx == 'iptv':
                        for line in open(in_tmp):
                            if line.startswith('http://') or line.startswith('https'):
                                outfile.write('#SERVICE %s:0:1:1:0:0:0:0:0:0:%s' % (service, line.replace(':', '%3a')))
                                outfile.write('#DESCRIPTION %s' % desk_tmp)
                            elif line.startswith('#EXTINF'):
                                desk_tmp = '%s' % line.split(',')[-1]
                            elif '<stream_url><![CDATA' in line:
                                outfile.write('#SERVICE %s:0:1:1:0:0:0:0:0:0:%s\r\n' % (service, line.split('[')[-1].split(']')[0].replace(':', '%3a')))
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
                            if os.path.isfile('%s%s' % (dir_enigma2, bqtname)) and os.path.isfile('/etc/enigma2/bouquets.tv'):
                                Utils.remove_line('/etc/enigma2/bouquets.tv', bqtname)
                                with open('/etc/enigma2/bouquets.tv', 'a+') as outfile:
                                    outfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % bqtname)
                                    outfile.close()
                                    in_bouquets = 1
                    self.mbox = self.session.open(MessageBox, _('Shuffle Favorite List in Progress') + '\n' + _('Wait please ...'), MessageBox.TYPE_INFO, timeout=5)
                    Utils.ReloadBouquets()
                else:
                    self.session.open(MessageBox, _('Conversion Failed!!!'), MessageBox.TYPE_INFO, timeout=5)
                    return
            except Exception as e:
                self.convert = False
                print('error convert iptv ', e)

    def cancel(self):
        if search_ok is True:
            self.resetSearch()
        else:
            self.close()

    def search_m3u(self):
        self.session.openWithCallback(
            self.filterM3u,
            VirtualKeyBoard,
            title=_("Filter this category..."),
            text=self.search)

    def filterM3u(self, result):
        global search_ok
        if result:
            self.names = []
            self.urls = []
            self.pics = []
            pic = plugin_path + "/res/pics/default.png"
            search = result
            try:
                f1 = open(in_tmp, "r+")
                fpage = f1.read()
                regexcat = "EXTINF.*?,(.*?)\\n(.*?)\\n"
                match = re.compile(regexcat, re.DOTALL).findall(fpage)
                for name, url in match:
                    if str(search).lower() in name.lower():
                        search_ok = True
                        url = url.replace(" ", "").replace("\\n", "")
                        self.names.append(name)
                        self.urls.append(url)
                        self.pics.append(pic)
                if search_ok is True:
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
        i = len(self.names)
        if i < 0:
            return
        global urlm3u, namem3u
        idx = self["list"].getSelectionIndex()
        namem3u = self.names[idx]
        urlm3u = self.urls[idx]
        if self.downloading is True:
            self.session.open(MessageBox, _('You are already downloading!!!'), MessageBox.TYPE_INFO, timeout=5)
        else:
            if '.mp4' in urlm3u or '.mkv' in urlm3u or '.flv' in urlm3u or '.avi' in urlm3u:
                self.downloading = True
                self.session.openWithCallback(self.download_m3u, MessageBox, _("DOWNLOAD VIDEO?"), type=MessageBox.TYPE_YESNO, timeout=10, default=False)
            else:
                self.downloading = False
                self.session.open(MessageBox, _('Only VOD Movie allowed or not .ext Filtered!!!'), MessageBox.TYPE_INFO, timeout=5)

    def download_m3u(self, result):
        if result:
            global in_tmp
            try:
                if self.downloading:
                    idx = self["list"].getSelectionIndex()
                    namem3u = self.names[idx]
                    urlm3u = self.urls[idx]
                    path = urlparse(urlm3u).path
                    ext = splitext(path)[1]
                    fileTitle = re.sub(r'[<>:"/\\|?*\[\]]', '_', namem3u)  # Sostituisce i caratteri non permessi
                    fileTitle = re.sub(r'[\s\(\)#\'\+\!&]', '_', fileTitle)  # Sostituisce spazi e altri caratteri con underscore
                    fileTitle = re.sub(r'_+', '_', fileTitle)  # Rimuove underscore ripetuti
                    fileTitle = fileTitle.lower() + ext  # Aggiunge l'estensione al nome del file
                    in_tmp = os.path.join(Path_Movies, fileTitle)
                    if os.path.isfile(in_tmp):
                        os.remove(in_tmp)
                    self.download = downloadWithProgress(urlm3u, in_tmp)
                    self.download.addProgress(self.downloadProgress)
                    self.download.start().addCallback(self.check).addErrback(self.showError)
                else:
                    self.downloading = False
                    self.session.open(MessageBox, _('Download Failed!!!'), MessageBox.TYPE_INFO, timeout=5)
            except Exception as e:
                print('Errore m3u:', e)
        return

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
        if PY3:
            urlm3u = six.ensure_str(urlm3u)
        else:
            if isinstance(urlm3u, unicode):
                urlm3u = urlm3u.encode('utf-8')
        print('urlmm33uu ', urlm3u)
        try:
            fileTitle = re.sub(r'[<>:"/\\|?*\[\]]', '_', namem3u)  # Sostituisce i caratteri non permessi
            fileTitle = re.sub(r'[\s\(\)#\'\+\!&]', '_', fileTitle)  # Sostituisce spazi e altri caratteri con underscore
            fileTitle = re.sub(r'_+', '_', fileTitle)  # Rimuove underscore ripetuti
            fileTitle = fileTitle.lower()  # Converte tutto in minuscolo
            in_tmp = os.path.join(Path_Movies, fileTitle + '.m3u')
            # Rimozione del file se esiste già
            if os.path.isfile(in_tmp):
                os.remove(in_tmp)
            if PY3:
                urlm3u = urlm3u.encode('utf-8')  # Codifica UTF-8 in Python 3
            downloadFilest(urlm3u, in_tmp)
            sleep(3)  # Attende il completamento del download
            self.playList()
            # Codice opzionale per il download con progresso (commentato)
            # self.download = downloadWithProgress(urlm3u, in_tmp)
            # self.download.addProgress(self.downloadProgress)
            # self.download.start().addCallback(self.check).addErrback(self.showError)
            print('ChannelList Downlist sleep 3 - 2')
        except Exception as e:
            print('Errore: ', e)
            # self.mbox = self.session.open(MessageBox, _('DOWNLOAD ERROR'), MessageBox.TYPE_INFO, timeout=5)
        return

    def playList(self):
        global search_ok
        search_ok = False
        self.names = []
        self.urls = []
        self.pics = []
        items = []
        pic = plugin_path + "/res/pics/default.png"
        try:
            if os.path.isfile(in_tmp) and os.stat(in_tmp).st_size > 0:
                print('ChannelList is_tmp exist in playlist')
                f1 = open(in_tmp, 'r+')
                fpage = f1.read()
                # fpage.seek(0)
                if 'tvg-logo="http' in fpage:
                    # #EXTINF:-1 tvg-id="externallinearfeed-04-21-2020-213519853-04-21-2020" tvg-logo="https://3gz8cg829c.execute-api.us-west-2.amazonaws.com/prod/image-renderer/16x9/full/600/center/90/5086119a-3424-4a9d-afc9-07cdcd962d4b-large16x9_STIRR_0721_EPG_MavTV_1920x1080.png?1625778769447?cb=c4ca4238a0b923820dcc509a6f75849b",MavTv
                    regexcat = 'EXTINF.*?tvg-logo="(.*?)".*?,(.*?)\\n(.*?)\\n'
                    match = re.compile(regexcat, re.DOTALL).findall(fpage)
                    for pic, name, url in match:
                        if url.startswith('http'):
                            url = url.replace(' ', '%20')
                            url = url.replace('\\n', '')
                            url = url.replace('%0A', '')
                            if 'samsung' in self.url.lower() or cfg.filterx.value is True:
                                regexcat = '(.*?).m3u8'
                                match = re.compile(regexcat, re.DOTALL).findall(url)
                                for url in match:
                                    url = url + '.m3u8'
                            if pic.endswith('.png') or pic.endswith('.jpg'):
                                pic = pic
                            else:
                                pic = pic + '.png'
                            item = name + "###" + url + "###" + pic  # + '\n'
                            items.append(item)
                    items.sort()
                    for item in items:
                        name = item.split('###')[0]
                        url = item.split('###')[1]
                        pic = item.split('###')[2]

                        self.names.append(Utils.checkStr(name))
                        self.urls.append(url)
                        self.pics.append(Utils.checkStr(pic))
                else:
                    regexcat = '#EXTINF.*?,(.*?)\\n(.*?)\\n'
                    match = re.compile(regexcat, re.DOTALL).findall(fpage)
                    for name, url in match:
                        if url.startswith('http'):
                            url = url.replace(' ', '%20')
                            url = url.replace('\\n', '')
                            url = url.replace('%0A', '')
                            if 'samsung' in self.url.lower() or cfg.filterx.value is True:
                                regexcat = '(.*?).m3u8'
                                match = re.compile(regexcat, re.DOTALL).findall(url)
                                for url in match:
                                    url = url + '.m3u8'
                            pic = pic
                            item = name + "###" + url + "###" + pic  # + '\n'
                            items.append(item)
                    items.sort()
                    for item in items:
                        name = item.split('###')[0]
                        url = item.split('###')[1]
                        pic = item.split('###')[2]

                        self.names.append(Utils.cleanName(name))
                        self.urls.append(url)
                        self.pics.append(pic)

            if cfg.thumb.value is True:
                self["live"].setText('N.' + str(len(self.names)) + " Stream")
                self.gridmaint = eTimer()
                try:
                    self.gridmaint.callback.append(self.gridpic)
                except:
                    self.gridmaint_conn = self.gridmaint.timeout.connect(self.gridpic)
                self.gridmaint.start(3000, True)
                # self.session.open(GridMain, self.names, self.urls, self.pics)
            else:
                m3ulist(self.names, self['list'])
                # self.load_poster()
                self["live"].setText('N.' + str(len(self.names)) + " Stream")
            # if cfg.thumb.value is False:
                self.load_poster()
                self["key_green"].show()
                self["key_yellow"].show()
                self["key_blue"].show()
        except Exception as e:
            print('error: ', e)

    def gridpic(self):
        self.session.open(GridMain, self.names, self.urls, self.pics)
        # self.GridMain(self.names, self.urls, self.pics)
        self.close()

    def runChannel(self):
        i = len(self.names)
        if i < 0:
            return
        idx = self['list'].getSelectionIndex()
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
        self.session.openWithCallback(self.pinEntered2, PinInput, pinList=[config.ParentalControl.setuppin.value], triesEntry=config.ParentalControl.retries.servicepin, title=_("Please enter the parental control pin code"), windowTitle=_("Enter pin code"))

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
            ref = '5002:0:1:0:0:0:0:0:0:0:' + 'http%3a//127.0.0.1%3a8088/' + str(url)
            sref = eServiceReference(ref)
            print('SREF: ', sref)
            sref.setName(str(name))
            self.session.open(M3uPlay2, name, sref)
            self.close()
        else:
            self.session.open(MessageBox, _('Install Streamlink first'), MessageBox.TYPE_INFO, timeout=5)

    def AdjUrlFavo(self):
        i = len(self.names)
        if i < 0:
            return
        idx = self['list'].getSelectionIndex()
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
        i = len(self.pics)
        if i < 0:
            return
        idx = self['list'].getSelectionIndex()
        pic = self.pics[idx]
        pixmaps = defpic
        if pic and pic.find('http') == -1:
            self.poster_resize(pixmaps)
            return
        else:
            if pic.startswith('http'):
                pixmaps = str(pic)
                if PY3:
                    pixmaps = six.ensure_binary(pixmaps)
                print('pic xxxxxxxxxxxxx', pixmaps)
                path = urlparse(pixmaps).path
                ext = splitext(path)[1]
                pictmp = '/tmp/posterst' + str(ext)
                if file_exists(pictmp):
                    pictmp = '/tmp/posterst' + str(ext)
                try:
                    if pixmaps.startswith(b"https") and sslverify:
                        parsed_uri = urlparse(pixmaps)
                        domain = parsed_uri.hostname
                        sniFactory = SNIFactory(domain)
                        if PY3:
                            pixmaps = six.ensure_binary(pixmaps)
                        # if six.PY3:
                            # pixmaps = pixmaps.encode()
                        print('uurrll: ', pixmaps)
                        downloadPage(pixmaps, pictmp, sniFactory, timeout=5).addCallback(self.downloadPic, pictmp).addErrback(self.downloadError)
                    else:
                        downloadPage(pixmaps, pictmp).addCallback(self.downloadPic, pictmp).addErrback(self.downloadError)
                except Exception as e:
                    print("Error: can't find file or read data ", e)
        return

    def downloadError(self, raw):
        try:
            self.poster_resize(defpic)
        except Exception as e:
            print(e)
            print('exe downloadError')

    def downloadPic(self, data, pictmp):
        if file_exists(pictmp):
            try:
                self.poster_resize(pictmp)
            except Exception as e:
                print("* error ", e)
                pass

    def poster_resize(self, png):
        self["poster"].show()
        pixmaps = png
        if file_exists(pixmaps):
            size = self['poster'].instance.size()
            self.picload = ePicLoad()
            self.scale = AVSwitch().getFramebufferScale()
            self.picload.setPara([size.width(), size.height(), self.scale[0], self.scale[1], 0, 1, '#00000000'])
            if os.path.exists('/var/lib/dpkg/status'):
                self.picload.startDecode(pixmaps, False)
            else:
                self.picload.startDecode(pixmaps, 0, 0, False)
            ptr = self.picload.getData()
            if ptr is not None:
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
        self["ShowHideActions"] = ActionMap(["InfobarShowHideActions"], {"toggleShow": self.OkPressed, "hide": self.hide}, 0)
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

    def debug(obj, text=""):
        print(text + " %s\n" % obj)


class M3uPlay2(
    InfoBarBase,
    InfoBarMenu,
    InfoBarSeek,
    InfoBarAudioSelection,
    InfoBarSubtitleSupport,
    InfoBarNotifications,
    TvInfoBarShowHide,
    Screen
):
    STATE_IDLE = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    ENABLE_RESUME_SUPPORT = True
    ALLOW_SUSPEND = True
    screen_timeout = 5000

    def __init__(self, session, name, url):
        global streaml
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = 'MoviePlayer'
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
                                     'ColorActions',
                                     'ButtonSetupActions',
                                     'OkCancelActions',
                                     'InfobarShowHideActions',
                                     'InfobarActions',
                                     'InfobarSeekActions'], {'leavePlayer': self.cancel,
                                                             'epg': self.showIMDB,
                                                             'info': self.showIMDB,
                                                             # 'info': self.cicleStreamType,
                                                             'tv': self.cicleStreamType,
                                                             'stop': self.leavePlayer,
                                                             'cancel': self.cancel,
                                                             'exit': self.leavePlayer,
                                                             'down': self.av,
                                                             'back': self.cancel}, -1)
        self.allowPiP = False
        self.service = None
        self.url = url
        self.pcip = 'None'
        self.name = html_conv.html_unescape(name)
        self.state = self.STATE_PLAYING
        self.srefInit = self.session.nav.getCurrentlyPlayingServiceReference()
        if '8088' in str(self.url):
            self.onFirstExecBegin.append(self.slinkPlay)
        else:
            self.onFirstExecBegin.append(self.cicleStreamType)
        self.onClose.append(self.cancel)

    def getAspect(self):
        return AVSwitch().getAspectRatioSetting()

    def getAspectString(self, aspectnum):
        return {0: '4:3 Letterbox',
                1: '4:3 PanScan',
                2: '16:9',
                3: '16:9 always',
                4: '16:10 Letterbox',
                5: '16:10 PanScan',
                6: '16:9 Letterbox'}[aspectnum]

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

    def showIMDB(self):
        text_clear = self.name
        if returnIMDB(text_clear):
            print('show imdb/tmdb')

    def slinkPlay(self, url):
        name = self.name
        ref = "{0}:{1}".format(url.replace(":", "%3a"), name.replace(":", "%3a"))
        print('final reference:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(str(name))
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def openPlay(self, servicetype, url):
        name = self.name
        ref = "{0}:0:1:0:0:0:0:0:0:0:{1}:{2}".format(servicetype, url.replace(":", "%3a"), name.replace(":", "%3a"))
        print('reference:   ', ref)
        if streaml is True:
            url = 'http://127.0.0.1:8088/' + str(url)
            ref = "{0}:0:1:0:0:0:0:0:0:0:{1}:{2}".format(servicetype, url.replace(":", "%3a"), name.replace(":", "%3a"))
            print('streaml reference:   ', ref)
        print('final reference:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(str(name))
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def cicleStreamType(self):
        global streaml
        streaml = False
        from itertools import cycle, islice
        self.servicetype = str(cfg.services.value)
        print('servicetype1: ', self.servicetype)
        url = str(self.url)
        if str(os.path.splitext(self.url)[-1]) == ".m3u8":
            if self.servicetype == "1":
                self.servicetype = "4097"
        currentindex = 0
        streamtypelist = ["4097"]

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
        self.up()

    def doEofInternal(self, playing):
        self.close()

    def __evEOF(self):
        self.end = True

    def showVideoInfo(self):
        if self.shown:
            self.hideInfobar()
        if self.infoCallback is not None:
            self.infoCallback()
        return

    def showAfterSeek(self):
        if isinstance(self, TvInfoBarShowHide):
            self.doShow()

    def cancel(self):
        srefinit = self.srefInit
        if os.path.isfile('/tmp/hls.avi'):
            os.remove('/tmp/hls.avi')
        self.session.nav.stopService()
        self.session.nav.playService(srefinit)
        if not self.new_aspect == self.init_aspect:
            try:
                self.setAspect(self.init_aspect)
            except:
                pass
        self.close()

    def leavePlayer(self):
        self.close()


class AddIpvStream(Screen):
    def __init__(self, session, name, url):
        Screen.__init__(self, session)
        self.session = session
        skin = os.path.join(skin_path, 'AddIpvStream.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setTitle(title_plug + ' ' + name)
        self['title'] = Label(title_plug + ' ' + name)
        self['Maintainer2'] = Label(Maintainer2)
        # self['path'] = Label(_('Folder path %s'% str(Path_Movies)))
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_('Ok'))
        self['key_yellow'] = Button()
        self["key_blue"] = Button()
        self["key_yellow"].hide()
        self["key_blue"].hide()
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'ButtonSetupActions',
                                     'DirectionActions'], {'ok': self.keyOk,
                                                           'cancel': self.keyCancel,
                                                           'green': self.keyOk,
                                                           'red': self.keyCancel}, -2)
        self['statusbar'] = Label()
        self.list = []
        self['list'] = MenuList([])
        self.mutableList = None
        self.servicelist = ServiceList(None)
        self.onLayoutFinish.append(self.createTopMenu)
        self.namechannel = name
        self.urlchannel = url
        return

    def initSelectionList(self):
        self.list = []
        self['list'].setList(self.list)

    def createTopMenu(self):
        self.setTitle(_('Add Stream IPTV'))
        self.initSelectionList()
        self.list = []
        self.list = self.getBouquetList()
        self['list'].setList(self.list)
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
            str = '4097:0:1:0:0:0:0:0:0:0:%s:%s' % (quote(self.url), quote(self.name))
            ref = eServiceReference(str)
            self.addServiceToBouquet(self.list[self['list'].getSelectedIndex()][1], ref)
            self.close()

    def addServiceToBouquet(self, dest, service=None):
        mutableList = self.getMutableList(dest)
        if mutableList is not None:
            if service is None:
                return
            if not mutableList.addService(service):
                mutableList.flushChanges()
        return

    def getMutableList(self, root=eServiceReference()):
        if self.mutableList is not None:
            return self.mutableList
        else:
            serviceHandler = eServiceCenter.getInstance()
            if not root.valid():
                root = self.getRoot()
            list = root and serviceHandler.list(root)
            if list is not None:
                return list.startEdit()
            return
            return

    def getRoot(self):
        return self.servicelist.getRoot()

    def keyCancel(self):
        self.close()


class OpenConfig(Screen, ConfigListScreen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        skin = os.path.join(skin_path, 'OpenConfig.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = _("stvcl Config")
        self.onChangedEntry = []
        self.list = []
        info = '***YOUR SETUP***'
        self.setTitle(title_plug + ' ' + info)
        self['title'] = Label(title_plug + ' SETUP')
        self['Maintainer2'] = Label(Maintainer2)
        self["paypal"] = Label()
        # self['path'] = Label(_('Folder path %s'% str(Path_Movies)))
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_('Save'))
        self["key_blue"] = Button(_('Empty Pic Cache'))
        self['key_yellow'] = Button()
        self['key_yellow'].hide()
        # self["key_blue"].hide()
        self['text'] = Label(info)
        self["description"] = Label()
        self['actions'] = ActionMap(["SetupActions",
                                     "ColorActions",
                                     'ButtonSetupActions',
                                     "VirtualKeyboardActions"], {'cancel': self.extnok,
                                                                 'red': self.extnok,
                                                                 'green': self.cfgok,
                                                                 'blue': self.cachedel,
                                                                 # 'yellow': self.msgupdt1,
                                                                 'showVirtualKeyboard': self.KeyText,
                                                                 'ok': self.Ok_edit}, -2)

        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
        self.createSetup()
        # self.onLayoutFinish.append(self.checkUpdate)
        self.onLayoutFinish.append(self.layoutFinished)
        if self.setInfo not in self['config'].onSelectionChanged:
            self['config'].onSelectionChanged.append(self.setInfo)

    def layoutFinished(self):
        payp = paypal()
        self["paypal"].setText(payp)
        self.setTitle(self.setup_title)

    def cachedel(self):
        fold = tvstrvl  # cfg.cachefold.value + "stvcl"
        cmd = "rm -rf " + tvstrvl + "/*"
        if os.path.exists(fold):
            os.system(cmd)
        self.mbox = self.session.open(MessageBox, _('All cache fold are empty!'), MessageBox.TYPE_INFO, timeout=5)

    def createSetup(self):
        self.editListEntry = None
        self.list = []
        self.list.append(getConfigListEntry(_('IPTV bouquets location '), cfg.bouquettop, _("Configure position of the bouquets of the converted lists")))
        self.list.append(getConfigListEntry(_('Player folder List <.m3u>:'), cfg.pthm3uf, _("Folder path containing the .m3u files")))
        self.list.append(getConfigListEntry(_('Services Player Reference type'), cfg.services, _("Configure Service Player Reference")))
        self.list.append(getConfigListEntry(_('Filter M3U link regex type'), cfg.filterx, _("Set On for line link m3u full")))
        self.list.append(getConfigListEntry(_('Show thumpics?'), cfg.thumb,  _("Show Thumbpics ? Enigma restart required")))
        if cfg.thumb.value is True:
            self.list.append(getConfigListEntry(_('Download thumpics?'), cfg.thumbpic, _("Download thumpics in Player M3U (is very Slow)?")))
        self.list.append(getConfigListEntry(_('Folder Cache for Thumbpics:'), cfg.cachefold, _("Configure position folder for temporary Thumbpics")))
        self.list.append(getConfigListEntry(_('Link in Extensions Menu:'), cfg.strtext, _("Show Plugin in Extensions Menu")))
        self.list.append(getConfigListEntry(_('Link in Main Menu:'), cfg.strtmain, _("Show Plugin in Main Menu")))
        self['config'].list = self.list
        self["config"].l.setList(self.list)
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
        if sel and sel == cfg.pthm3uf:
            self.setting = 'pthm3uf'
            self.openDirectoryBrowser(cfg.pthm3uf.value)
        elif sel and sel == cfg.cachefold:
            self.setting = 'cachefold'
            self.openDirectoryBrowser(cfg.cachefold.value)
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
        except Exception as e:
            print('error: ', e)

    def openDirectoryBrowserCB(self, path):
        if path is not None:
            if self.setting == 'pthm3uf':
                cfg.pthm3uf.setValue(path)
            elif self.setting == 'cachefold':
                path = os.path.join(path, 'stvcl')
                cfg.cachefold.setValue(path)
        return

    def cfgok(self):
        self.save()

    def save(self):
        if not os.path.exists(cfg.pthm3uf.value):
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

    def VirtualKeyBoardCallback(self, callback=None):
        if callback is not None and len(callback):
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


def threadGetPage(url=None, file=None, key=None, success=None, fail=None, *args, **kwargs):
    print('[tivustream][threadGetPage] url, file, key, args, kwargs', url, "   ", file, "   ", key, "   ", args, "   ", kwargs)
    try:
        url = url.rstrip('\r\n')
        url = url.rstrip()
        url = url.replace("%0A", "")
        response = get(url, verify=False)
        response.raise_for_status()
        if file is None:
            success(response.content)
        elif key is not None:
            success(response.content, file, key)
        else:
            success(response.content, file)
    except httperror:
        print('[tivustream][threadGetPage] Http error: ', httperror)
        # fail(error)  # E0602 undefined name 'error'
    except exceptions.RequestException as error:
        print(error)


def getpics(names, pics, tmpfold, picfold):
    # from PIL import Image
    global defpic
    defpic = defpic
    pix = []

    if cfg.thumbpic.value == "False":
        npic = len(pics)
        i = 0
        while i < npic:
            pix.append(defpic)
            i += 1
        return pix

    cmd = "rm " + tmpfold + "/*"
    os.system(cmd)

    npic = len(pics)
    j = 0

    while j < npic:
        name = names[j]
        if name is None or name == '':
            name = "Video"
        url = pics[j]
        ext = str(os.path.splitext(url)[-1])
        picf = os.path.join(picfold, str(name + ext))
        tpicf = os.path.join(tmpfold, str(name + ext))

        if os.path.exists(picf):
            if ('stagione') in str(name.lower()):
                cmd = "rm " + picf
                os.system(cmd)

            cmd = "cp " + picf + " " + tmpfold
            print("In getpics fileExists(picf) cmd =", cmd)
            os.system(cmd)

        if not os.path.exists(picf):
            if plugin_path in url:
                try:
                    cmd = "cp " + url + " " + tpicf
                    print("In getpics not fileExists(picf) cmd =", cmd)
                    os.system(cmd)
                except:
                    pass
            else:
                # now download image
                try:
                    url = url.replace(" ", "%20").replace("ExQ", "=")
                    url = url.replace("AxNxD", "&").replace("%0A", "")
                    poster = Utils.checkRedirect(url)
                    if poster:
                        if "|" in url:
                            n3 = url.find("|", 0)
                            n1 = url.find("Referer", n3)
                            n2 = url.find("=", n1)
                            url = url[:n3]
                            referer = url[n2:]
                            p = Utils.getUrl2(url, referer)
                            with open(tpicf, 'wb') as f1:
                                f1.write(p)
                        else:
                            try:
                                try:
                                    with open(tpicf, 'wb') as f:
                                        f.write(requests.get(url, stream=True, allow_redirects=True).content)
                                    print('=============11111111=================\n')
                                except Exception as e:
                                    print("Error: Exception", e)
                                    print('===========2222222222=================\n')
                                    callInThread(threadGetPage, url=poster, file=tpicf, success=downloadPic, fail=downloadError)

                                    '''
                                    print(e)
                                    open(tpicf, 'wb').write(requests.get(poster, stream=True, allow_redirects=True).content)
                                    '''
                            except Exception as e:
                                print("Error: Exception 2")
                                print(e)

                except:
                    cmd = "cp " + defpic + " " + tpicf
                    os.system(cmd)
                    print('cp defpic tpicf')

        if not os.path.exists(tpicf):
            cmd = "cp " + defpic + " " + tpicf
            os.system(cmd)

        if os.path.exists(tpicf):
            try:
                size = [150, 220]
                if screenwidth.width() == 2560:
                    size = [294, 440]
                elif screenwidth.width() == 1920:
                    size = [220, 330]

                file_name, file_extension = os.path.splitext(tpicf)
                try:
                    im = Image.open(tpicf).convert("RGBA")
                    # shrink if larger
                    try:
                        im.thumbnail(size, Image.Resampling.LANCZOS)
                    except:
                        im.thumbnail(size, Image.ANTIALIAS)
                    imagew, imageh = im.size
                    # enlarge if smaller
                    try:
                        if imagew < size[0]:
                            ratio = size[0] / imagew
                            try:
                                im = im.resize((int(imagew * ratio), int(imageh * ratio)), Image.Resampling.LANCZOS)
                            except:
                                im = im.resize((int(imagew * ratio), int(imageh * ratio)), Image.ANTIALIAS)

                            imagew, imageh = im.size
                    except Exception as e:
                        print(e)
                    # # no work on PY3
                    # # crop and center image
                    # bg = Image.new("RGBA", size, (255, 255, 255, 0))
                    # im_alpha = im.convert("RGBA").split()[-1]
                    # bgwidth, bgheight = bg.size
                    # bg_alpha = bg.convert("RGBA").split()[-1]
                    # temp = Image.new("L", (bgwidth, bgheight), 0)
                    # temp.paste(im_alpha, (int((bgwidth - imagew) / 2), int((bgheight - imageh) / 2)), im_alpha)
                    # bg_alpha = ImageChops.screen(bg_alpha, temp)
                    # bg.paste(im, (int((bgwidth - imagew) / 2), int((bgheight - imageh) / 2)))
                    # im = bg
                    im.save(file_name + ".png", "PNG")
                except Exception as e:
                    print(e)
                    im = Image.open(tpicf)
                    try:
                        im.thumbnail(size, Image.Resampling.LANCZOS)
                    except:
                        im.thumbnail(size, Image.ANTIALIAS)
                    im.save(tpicf)
            except Exception as e:
                print("******* picon resize failed *******")
                print(e)
                tpicf = defpic
        else:
            print("******* make picon failed *******")
            tpicf = defpic

        pix.append(j)
        pix[j] = picf
        j += 1

    cmd1 = "cp " + tmpfold + "/* " + picfold
    os.system(cmd1)

    cmd1 = "rm " + tmpfold + "/* &"
    os.system(cmd1)
    return pix


def downloadPic(output, poster):
    try:
        if output is not None:
            f = open(poster, 'wb')
            f.write(output)
            f.close()
    except Exception as e:
        print('downloadPic error ', e)
    return


def downloadError(output):
    print('output error ', output)
    pass


def savePoster(dwn_poster, url_poster):
    with open(dwn_poster, 'wb') as f:
        f.write(requests.get(url_poster, stream=True, allow_redirects=True).content)
        f.close()


class GridMain(Screen):
    def __init__(self, session, names, urls, pics=[]):
        from Components.Sources.List import List
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        skin = os.path.join(skin_path, 'GridMain.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self['title'] = Label('..:: S.T.V.C.L. ::..')
        self.pos = []

        def add_positions(coords):
            for coord in coords:
                self.pos.append(coord)

        if screenwidth.width == 2560:
            positions = [
                [180, 80], [658, 80], [1134, 80], [1610, 80], [2084, 80],
                [180, 720], [658, 720], [1134, 720], [1610, 720], [2084, 720]
            ]
            add_positions(positions)

        elif screenwidth.width == 1920:
            positions = [
                [122, 42], [478, 42], [834, 42], [1190, 42], [1546, 42],
                [122, 522], [478, 522], [834, 522], [1190, 522], [1546, 522]
            ]
            add_positions(positions)

        else:
            positions = [
                [81, 28], [319, 28], [556, 28], [793, 28], [1031, 28],
                [81, 348], [319, 348], [556, 348], [793, 348], [1031, 348]
            ]
            add_positions(positions)

        tmpfold = tvstrvl + "/tmp"  # os.path.join(str(cfg.cachefold.value), "stvcl/tmp")
        picfold = tvstrvl + " /pic"  # os.path.join(str(cfg.cachefold.value), "stvcl/pic")
        picx = getpics(names, pics, tmpfold, picfold)
        # print("In Gridmain pics = ", pics)
        self.urls = urls
        self.pics = picx
        self.name = "stvcl"
        self.names = names
        self["info"] = Label()
        menu_list = []
        menu_list = names
        for x in menu_list:
            print("x in list =", x)

        self["menu"] = List(menu_list)
        self["frame"] = MovingPixmap()

        self.PIXMAPS_PER_PAGE = 10
        i = 0
        while i < self.PIXMAPS_PER_PAGE:
            self["label" + str(i + 1)] = StaticText()
            self["pixmap" + str(i + 1)] = Pixmap()
            i += 1
        self.npics = len(self.names)
        self.npage = int(float(self.npics // self.PIXMAPS_PER_PAGE)) + 1
        self.index = 0
        self.maxentry = len(menu_list) - 1
        self.ipage = 1

        self["actions"] = ActionMap(["OkCancelActions", "EPGSelectActions", "MenuActions", 'ButtonSetupActions', "DirectionActions", "NumberActions"], {
            "ok": self.okClicked,
            "cancel": self.cancel,
            "left": self.key_left,
            "right": self.key_right,
            "up": self.key_up,
            "down": self.key_down
        })
        self.srefInit = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.openTest)
        # self.onShown.append(self.openTest)

    def paintFrame(self):
        try:
            # If the index exceeds the maximum number of items, it returns to the first item
            if self.index > self.maxentry:
                self.index = self.minentry
            self.idx = self.index
            name = self.names[self.idx]
            self['info'].setText(str(name))
            ifr = self.index - (self.PIXMAPS_PER_PAGE * (self.ipage - 1))
            ipos = self.pos[ifr]
            self["frame"].moveTo(ipos[0], ipos[1], 1)
            self["frame"].startMoving()
        except Exception as e:
            print('Error in paintFrame: ', e)

    def openTest(self):
        if self.ipage < self.npage:
            self.maxentry = (self.PIXMAPS_PER_PAGE * self.ipage) - 1
            self.minentry = (self.ipage - 1) * self.PIXMAPS_PER_PAGE

        elif self.ipage == self.npage:
            self.maxentry = len(self.pics) - 1
            self.minentry = (self.ipage - 1) * self.PIXMAPS_PER_PAGE
            i1 = 0
            while i1 < self.PIXMAPS_PER_PAGE:
                self["label" + str(i1 + 1)].setText(" ")
                self["pixmap" + str(i1 + 1)].instance.setPixmapFromFile(dblank)
                i1 += 1
        self.npics = len(self.pics)
        i = 0
        i1 = 0
        self.picnum = 0
        ln = self.maxentry - (self.minentry - 1)
        while i < ln:
            idx = self.minentry + i
            # self["label" + str(i + 1)].setText(self.names[idx])  # this show label to bottom of png pixmap
            pic = self.pics[idx]
            if not os.path.exists(self.pics[idx]):
                pic = dblank
            self["pixmap" + str(i + 1)].instance.setPixmapFromFile(pic)
            i += 1
        self.index = self.minentry
        self.paintFrame()

    def key_left(self):
        # Decrement the index only if we are not at the first pixmap
        if self.index >= 0:
            self.index -= 1
        else:
            # If we are at the first pixmap, go back to the last pixmap of the last page
            self.ipage = self.npage
            self.index = self.npics - 1
        # Check if we need to change pages
        if self.index < self.minentry:
            self.ipage -= 1
            if self.ipage < 1:  # If we go beyond the first page
                self.ipage = self.npage
                self.index = self.npics - 1  # Back to the last pixmap of the last page
            self.openTest()
        else:
            self.paintFrame()

    def key_right(self):
        # Increment the index only if we are not at the last pixmap
        if self.index < self.npics - 1:
            self.index += 1
        else:
            # If we are at the last pixmap, go back to the first pixmap of the first page
            self.index = 0
            self.ipage = 1
            self.openTest()
        # Check if we need to change pages
        if self.index > self.maxentry:
            self.ipage += 1
            if self.ipage > self.npage:  # If we exceed the number of pages
                self.index = 0
                self.ipage = 1  # Back to first page
            self.openTest()
        else:
            self.paintFrame()

    def key_up(self):
        if self.index >= 5:
            self.index -= 5
        else:
            if self.ipage > 1:
                self.ipage -= 1
                self.index = self.maxentry  # Back to the last line of the previous page
                self.openTest()
            else:
                # If we are on the first page, go back to the last pixmap of the last page
                self.ipage = self.npage
                self.index = self.npics - 1
                self.openTest()
        self.paintFrame()

    def key_down(self):
        if self.index <= self.maxentry - 5:
            self.index += 5
        else:
            if self.ipage < self.npage:
                self.ipage += 1
                self.index = self.minentry  # Back to the top of the next page
                self.openTest()
            else:
                # If we are on the last page, go back to the first pixmap of the first page
                self.index = 0
                self.ipage = 1
                self.openTest()

        self.paintFrame()

    def okClicked(self):
        itype = self.index
        url = self.urls[itype]
        name = self.names[itype]
        self.session.open(M3uPlay2, name, url)
        return

    def cancel(self):
        self.close()

    def exit(self):
        self.close()

    def info(self):
        itype = self.index
        self.inf = self.names[itype]
        # self.inf = ''
        try:
            self.inf = self.names[itype]
        except:
            pass
        if self.inf:
            try:
                self["info"].setText(self.inf)
                # print('infos: ', self.inf)
            except:
                self["info"].setText('')
                # print('except info')
        print("In GridMain infos =", self.inf)
