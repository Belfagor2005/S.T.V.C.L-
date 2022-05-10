#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
****************************************
*        coded by Lululla              *
*             skin by MMark            *
*             10/05/2022               *
*   Thank's                            *
*      stvcl, Levi45, KiddaC           *
****************************************
'''
from __future__ import absolute_import
from Plugins.Plugin import PluginDescriptor
from Tools.Directories import SCOPE_PLUGINS, resolveFilename
from Components.config import config
from . import main
from . import Utils
import os

currversion = '1.2'
title_plug = 'Smart Tv Channels List'
name_plug = '..:: Smart Tv Channels List  V.%s ::.. ' % currversion
plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('stvcl'))

try:
    if Utils.checkInternet():
        try:
            from . import Update 
            Update.upd_done()
        except:
            pass
    else:
        Utils.web_info("No Internet")
except:
    import traceback
    traceback.print_exc()

def mainw(session, **kwargs):
    try:
        from six.moves import reload_module
        reload_module(Utils)
        reload_module(main)        
        session.open(main.StvclMain)
    except:
        import traceback
        traceback.print_exc()

def cfgmain(menuid):
    if menuid == 'mainmenu':
        return [(title_plug,
         mainw,
         name_plug,
         44)]
    else:
        return []

def Plugins(**kwargs):
    piclogox = 'logo.png'
    if not os.path.exists('/var/lib/dpkg/status'):
        piclogox = plugin_path + '/res/skins/hd/logo.png'
    extDescriptor = PluginDescriptor(name=title_plug, description=_(name_plug), where=PluginDescriptor.WHERE_EXTENSIONSMENU, icon=piclogox, fnc=mainw)
    mainDescriptor = PluginDescriptor(name=title_plug, description=_(name_plug), where=PluginDescriptor.WHERE_MENU, icon=piclogox, fnc=cfgmain)
    result = [PluginDescriptor(name=title_plug, description=_(name_plug), where=[PluginDescriptor.WHERE_PLUGINMENU], icon=piclogox, fnc=mainw)]
    if config.plugins.stvcl.strtext.value:
        result.append(extDescriptor)
    if config.plugins.stvcl.strtmain.value:
        result.append(mainDescriptor)
    return result
