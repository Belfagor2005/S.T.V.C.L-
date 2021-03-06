#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
****************************************
*		 coded by Lululla			   *
*			thank's Pcd				   *
*			  13/01/2022			   *
*		skin by MMark				   *
****************************************
Info http://t.me/tivustream
'''
from __future__ import print_function
from . import _
import os
import re
import sys
import six
import glob
import socket
from os.path import splitext
from Screens.Screen import Screen
from Components.Label import Label
from Components.config import config
from Components.Button import Button
from enigma import eTimer, eActionMap
from Components.AVSwitch import AVSwitch
from Components.MenuList import MenuList
from Components.Sources.List import List
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from six.moves.urllib.request import urlopen
from six.moves.urllib.request import Request
from Screens.InfoBar import MoviePlayer, InfoBar
from time import time, localtime, strftime, sleep
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Sources.StaticText import StaticText
from six.moves.urllib.error import HTTPError, URLError
from Tools.Directories import SCOPE_PLUGINS, resolveFilename, fileExists
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from enigma import iServiceInformation, iPlayableService, eServiceReference
from Screens.InfoBarGenerics import InfoBarMenu, InfoBarSeek, InfoBarAudioSelection, InfoBarNotifications, \
	InfoBarSubtitleSupport, InfoBarSummarySupport, InfoBarServiceErrorPopupSupport, InfoBarMoviePlayerSummarySupport
try:
	from Plugins.Extensions.stvcl.Utils import *
except:
	from . import Utils
plugin_fold	   = os.path.dirname(sys.modules[__name__].__file__)
try:
	from PIL import Image
except:
	import Image

if isFHD():
	skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/stvcl/res/skins/fhd/")
	defpic = resolveFilename(SCOPE_PLUGINS, "Extensions/stvcl/res/pics/{}".format('defaultL.png'))
	dblank = resolveFilename(SCOPE_PLUGINS, "Extensions/stvcl/res/pics/{}".format('blankL.png'))
else:
	skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/stvcl/res/skins/hd/")
	defpic = resolveFilename(SCOPE_PLUGINS, "Extensions/stvcl/res/pics/{}".format('default.png'))
	dblank = resolveFilename(SCOPE_PLUGINS, "Extensions/stvcl/res/pics/{}".format('blank.png'))
if os.path.exists('/var/lib/dpkg/status'):
	skin_path = skin_path + 'dreamOs/'


def getDesktopSize():
	from enigma import getDesktop
	s = getDesktop(0).size()
	return (s.width(), s.height())

def isFHD():
	desktopSize = getDesktopSize()
	return desktopSize[0] == 1920

pos = []
if isFHD():
	pos.append([35,80])
	pos.append([395,80])
	pos.append([755,80])
	pos.append([1115,80])
	pos.append([1475,80])
	pos.append([35,530])
	pos.append([395,530])
	pos.append([755,530])
	pos.append([1115,530])
	pos.append([1475,530])
else:
	pos.append([20,50])
	pos.append([260,50])
	pos.append([500,50])
	pos.append([740,50])
	pos.append([980,50])
	pos.append([20,350])
	pos.append([260,350])
	pos.append([500,350])
	pos.append([740,350])
	pos.append([980,350])

def getpics(names, pics, tmpfold, picfold):
	global defpic
	defpic = defpic
	print("In getpics tmpfold =", tmpfold)
	print("In getpics picfold =", picfold)
	if isFHD():
		nw = 300
	else:
		nw = 200
	pix = []
	if config.plugins.stvcl.thumbpic.value == False:
		npic = len(pics)
		i = 0
		while i < npic:
			pix.append(defpic)
			i = i+1
		return pix
	cmd = "rm " + tmpfold + "/*"
	os.system(cmd)
	npic = len(pics)
	j = 0
	print("In getpics names =", names)
	print("In getpics pics =", pics)
	while j < npic:
		name = names[j]
		print("In getpics name =", name)
		if name is None:
			name = "Video"
		try:
			name = name.replace("&", "").replace(":", "").replace("(", "-")
			name = name.replace(")", "").replace(" ", "").replace("'", "")
			name = name.replace("/", "-")
			name = decodeHtml(name)
		except:
			pass
		url = pics[j]
		if url is None:
			url = ""
		url = url.replace(" ", "%20")
		url = url.replace("ExQ", "=")
		url = url.replace("AxNxD", "&")
		print("In getpics url =", url)
		ext = str(os.path.splitext(url)[-1])
		picf = picfold + "/" + name + ext
		tpicf = tmpfold + "/" + name + ext
		if fileExists(picf):
			if ('Stagione') in str(name):
				cmd = "rm " + picf
				os.system(cmd)
			cmd = "cp " + picf + " " + tmpfold
			print("In getpics fileExists(picf) cmd =", cmd)
			os.system(cmd)
		if fileExists(tpicf):
			if ('Stagione') in str(name):
				cmd = "rm " + tpicf
				os.system(cmd)
		if not fileExists(picf):
			if plugin_fold in url:
				try:
					cmd = "cp " + url + " " + tpicf
					print("In getpics not fileExists(picf) cmd =", cmd)
					os.system(cmd)
				except:
					pass
			else:
				try:
					if "|" in url:
						n3 = url.find("|", 0)
						n1 = url.find("Referer", n3)
						n2 = url.find("=", n1)
						url1 = url[:n3]
						referer = url[n2:]
						p = getUrl2(url1, referer)
						f1=open(tpicf,"wb")
						f1.write(p)
						f1.close()
					else:
						print("Going in urlopen url =", url)
						fpage = AdultUrl(url)
						f1=open(tpicf,"wb")
						f1.write(fpage)
						f1.close()

				except:
					cmd = "cp " + defpic + " " + tpicf
					os.system(cmd)

		if not fileExists(tpicf):
		# else:
			print("In getpics not fileExists(tpicf) tpicf=", tpicf)
			cmd = "cp " + defpic + " " + tpicf
			print("In getpics not fileExists(tpicf) cmd=", cmd)
			os.system(cmd)
			try:
				#start kiddac code
				size = [200, 200]
				if isFHD():
					size = [300, 300]
				im = Image.open(tpicf).convert('RGBA')
				im.thumbnail(size, Image.ANTIALIAS)
				# crop and center image
				bg = Image.new('RGBA', size, (255, 255, 255, 0))
				imagew, imageh = im.size
				im_alpha = im.convert('RGBA').split()[-1]
				bgwidth, bgheight = bg.size
				bg_alpha = bg.convert('RGBA').split()[-1]
				temp = Image.new('L', (bgwidth, bgheight), 0)
				temp.paste(im_alpha, (int((bgwidth - imagew) / 2), int((bgheight - imageh) / 2)), im_alpha)
				bg_alpha = ImageChops.screen(bg_alpha, temp)
				bg.paste(im, (int((bgwidth - imagew) / 2), int((bgheight - imageh) / 2)))
				im = bg
				im.save(tpicf, 'PNG')

			#end kiddac code
				# im = Image.open(tpicf)#.convert('RGBA')
				# # imode = im.mode
				# # if im.mode == "JPEG":
					# # im.save(tpicf)
					# # # in most case, resulting jpg file is resized small one
				# # if imode.mode in ["RGBA", "P"]:
					# # imode = imode.convert("RGB")
					# # rgb_im.save(tpicf)
				# # if imode != "P":
					# # im = im.convert("P")
				# # if im.mode != "P":
					# # im = im.convert("P")
				# w = im.size[0]
				# d = im.size[1]
				# r = float(d)/float(w)
				# d1 = r*nw
				# if w != nw:
					# x = int(nw)
					# y = int(d1)
					# im = im.resize((x,y), Image.ANTIALIAS)
				# im.save(tpicf, quality=100, optimize=True)
			except Exception as e:
				   print("******* picon resize failed *******")
				   print(str(e))
		else:
			tpicf = defpic
		pix.append(j)
		pix[j] = picf
		j = j+1

	cmd1 = "cp " + tmpfold + "/* " + picfold + " && rm " + tmpfold + "/* &"
	# print("In getpics final cmd1=", cmd1)
	os.system(cmd1)
	os.system('sleep 1')
	return pix


class GridMain(Screen):
	def __init__(self, session, names, urls, pics = []):
		skin = skin_path + '/GridMain.xml'
		f = open(skin, 'r')
		self.skin = f.read()
		f.close()
		Screen.__init__(self, session)
		self['title'] = Label(_('..:: S.T.V.C.L. ::..' ))
		tmpfold = config.plugins.stvcl.cachefold.value + "stvcl/tmp"
		picfold = config.plugins.stvcl.cachefold.value + "stvcl/pic"
		pics = getpics(names, pics, tmpfold, picfold)
		sleep(3)
		list = []

		self.pos = []
		self.pos = pos
		print(" self.pos =", self.pos)
		self.name = "stvcl"
		self.pics = pics
		self.urls = urls
		self.names = names
		self.names1 = names
		list = names
		self["info"] = Label()
		self["menu"] = List(list)
		self["frame"] = MovingPixmap()
		i = 0
		while i<16:
			  self["label" + str(i+1)] = StaticText()
			  self["pixmap" + str(i+1)] = Pixmap()
			  i = i+1
		i = 0
		ip = 0
		self.index = 0
		self.ipage = 1
		self.icount = 0
		ln = len(self.names1)
		self.npage = int(float(ln/10)) + 1
		self["actions"] = ActionMap(["OkCancelActions", "MenuActions", "DirectionActions", "NumberActions"],
				{
				"ok": self.okClicked,
				"cancel": self.cancel,
				"left": self.key_left,
				"right": self.key_right,
				"up": self.key_up,
				"down": self.key_down,
				})

		global SREF
		self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
		SREF = self.initialservice
		self.onLayoutFinish.append(self.openTest)
		# self.onShown.append(self.openTest)

	def cancel(self):
		self.close()

	def exit(self):
		self.close()

	def paintFrame(self):
		print("In paintFrame self.index, self.minentry, self.maxentry =", self.index, self.minentry, self.maxentry)
		# if self.maxentry < self.index or self.index < 0:
		#	  return
		print("In paintFrame self.ipage = ", self.ipage)
		ifr = self.index - (10*(self.ipage-1))
		print("ifr =", ifr)
		ipos = self.pos[ifr]
		print("ipos =", ipos)

		inf = self.index
		if inf != None or inf != -1:
			self["info"].setText(self.names1[inf])
			print('infos: ', inf)
		self["frame"].moveTo( ipos[0], ipos[1], 1)
		self["frame"].startMoving()

	def openTest(self):
		print("self.index, openTest self.ipage, self.npage =", self.index, self.ipage, self.npage)
		if self.ipage < self.npage:
			self.maxentry = (10*self.ipage)-1
			self.minentry = (self.ipage-1)*10
			#self.index 0-11
			print("self.ipage , self.minentry, self.maxentry =", self.ipage, self.minentry, self.maxentry)
		elif self.ipage == self.npage:
			print("self.ipage , len(self.pics) =", self.ipage, len(self.pics))
			self.maxentry = len(self.pics) - 1
			self.minentry = (self.ipage-1)*10
			print("self.ipage , self.minentry, self.maxentry B=", self.ipage, self.minentry, self.maxentry)
			i1 = 0
			blpic = dblank
			while i1 < 12:
				self["label" + str(i1+1)].setText(" ")
				self["pixmap" + str(i1+1)].instance.setPixmapFromFile(blpic)
				i1 = i1+1
		print("len(self.pics) , self.minentry, self.maxentry =", len(self.pics) , self.minentry, self.maxentry)
		self.npics = len(self.pics)
		i = 0
		i1 = 0
		self.picnum = 0
		print("doing pixmap")
		ln = self.maxentry - (self.minentry-1)
		while i < ln:
			idx = self.minentry + i
			print("i, idx =", i, idx)
			print("self.names1[idx] B=", self.names1[idx])
			self["label" + str(i+1)].setText(self.names1[idx])
			print("idx, self.pics[idx]", idx, self.pics[idx])
			pic = self.pics[idx]
			print("pic =", pic)
			if os.path.exists(pic):
				print("pic path exists")
			else:
				print("pic path exists not")
			picd = defpic
			try:
				self["pixmap" + str(i+1)].instance.setPixmapFromFile(pic) #ok
			except:
				self["pixmap" + str(i+1)].instance.setPixmapFromFile(picd)
			i = i+1
		self.index = self.minentry
		print("self.minentry, self.index =", self.minentry, self.index)
		self.paintFrame()

	def key_left(self):
		self.index -= 1
		if self.index < 0:
			self.index = self.maxentry
		self.paintFrame()

	def key_right(self):
		i = self.npics - 1
		if self.index == i:
			self.index = 0
			self.ipage = 1
			self.openTest()
		self.index += 1
		if self.index > self.maxentry:
			self.index = 0
		self.paintFrame()

	def key_up(self):
		print("keyup self.index, self.minentry = ", self.index, self.minentry)
		self.index = self.index - 5
		#	if self.index < 0:
		#		self.index = self.maxentry
		#		self.paintFrame()
		print("keyup self.index, self.minentry 2 = ", self.index, self.minentry)
		print("keyup self.ipage = ", self.ipage)
		if self.index < (self.minentry):
			if self.ipage > 1:
				self.ipage = self.ipage - 1
				self.openTest()
		##	self.paintFrame()
			elif self.ipage == 1:
		#	self.close()
				return
				# self.paintFrame() #edit lululla
			else:
				# return
			   self.paintFrame()
		else:
			# return
		   self.paintFrame()

	def key_down(self):
		print("keydown self.index, self.maxentry = ", self.index, self.maxentry)
		self.index = self.index + 5
		print("keydown self.index, self.maxentry 2= ", self.index, self.maxentry)
		print("keydown self.ipage = ", self.ipage)
		if self.index > (self.maxentry):
			if self.ipage < self.npage:
				self.ipage = self.ipage + 1
				self.openTest()
			elif self.ipage == self.npage:
				self.index = 0
				self.ipage = 1
				self.openTest()
			else:
				print("keydown self.index, self.maxentry 3= ", self.index, self.maxentry)
				self.paintFrame()
		else:
			self.paintFrame()

	def okClicked(self):
		itype = self.index
		url = self.urls[itype]
		name = self.names1[itype]
		self.session.open(M3uPlay2, name, url)
		return

class TvInfoBarShowHide():
	""" InfoBar show/hide control, accepts toggleShow and hide actions, might start
	fancy animations. """
	STATE_HIDDEN = 0
	STATE_HIDING = 1
	STATE_SHOWING = 2
	STATE_SHOWN = 3
	# FLAG_CENTER_DVB_SUBS = 2048
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

	def serviceStarted(self):
		if self.execing:
			if config.usage.show_infobar_on_zap.value:
				self.doShow()

	def __onShow(self):
		self.__state = self.STATE_SHOWN
		self.startHideTimer()

	def __onHide(self):
		self.__state = self.STATE_HIDDEN

	def startHideTimer(self):
		if self.__state == self.STATE_SHOWN and not self.__locked:
			self.hideTimer.stop()
			idx = config.usage.infobar_timeout.index
			if idx:
				self.hideTimer.start(idx * 1500, True)

	def doShow(self):
		self.hideTimer.stop()
		self.show()
		self.startHideTimer()

	def doTimerHide(self):
		self.hideTimer.stop()
		if self.__state == self.STATE_SHOWN:
			self.hide()

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
	screen_timeout = 4000

	def __init__(self, session, name, url):
		global SREF, streaml
		Screen.__init__(self, session)
		self.session = session
		global _session
		_session = session
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
		 'stop': self.leavePlayer,
		 'cancel': self.leavePlayer,
		 'back': self.leavePlayer}, -1)
		self.allowPiP = False
		self.service = None
		service = None
		self.pcip = 'None'
		self.icount = 0
		self.url = url
		self.name = decodeHtml(name)
		self.state = self.STATE_PLAYING
		SREF = self.session.nav.getCurrentlyPlayingServiceReference()
		if '8088' in str(self.url):
			# self.onLayoutFinish.append(self.slinkPlay)
			self.onFirstExecBegin.append(self.slinkPlay)
		else:
			# self.onLayoutFinish.append(self.cicleStreamType)
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
		# debug = True
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
			message = 'stitle:' + str(sTitle) + '\n' + 'sServiceref:' + str(sServiceref) + '\n' + 'sTagCodec:' + str(sTagCodec) + '\n' + 'sTagVideoCodec:' + str(sTagVideoCodec) + '\n' + 'sTagAudioCodec : ' + str(sTagAudioCodec)
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
		ref = str(url)
		ref = ref.replace(':', '%3a').replace(' ','%20')
		print('final reference:	  ', ref)
		sref = eServiceReference(ref)
		sref.setName(name)
		self.session.nav.stopService()
		self.session.nav.playService(sref)

	def openPlay(self, servicetype, url):
		name = self.name
		url = url.replace(':', '%3a').replace(' ','%20')
		ref = str(servicetype) + ':0:1:0:0:0:0:0:0:0:' + str(url)
		if streaml == True:
			ref = str(servicetype) + ':0:1:0:0:0:0:0:0:0:http%3a//127.0.0.1%3a8088/' + str(url)
		print('final reference:	  ', ref)
		sref = eServiceReference(ref)
		sref.setName(name)
		self.session.nav.stopService()
		self.session.nav.playService(sref)

	def cicleStreamType(self):
		global streaml
		streaml = False
		from itertools import cycle, islice
		self.servicetype = str(config.plugins.stvcl.services.value) +':0:1:0:0:0:0:0:0:0:'#	 '4097'
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
		if os.path.exists("/usr/sbin/streamlinksrv"):
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

	def ok(self):
		if self.shown:
			self.hideInfobar()
		else:
			self.showInfobar()

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

