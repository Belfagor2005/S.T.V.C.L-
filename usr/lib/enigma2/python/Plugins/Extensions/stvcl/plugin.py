#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
****************************************
*        coded by Lululla              *
*             skin by MMark            *
*             10/07/2022               *
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

def intCheck():
    import socket
    try:
        socket.setdefaulttimeout(1)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except:
        return False

def mainw(session, **kwargs):
    try:
        if intCheck():
                from . import Update
                Update.upd_done()
                from six.moves import reload_module
                reload_module(Utils)
                reload_module(main)        
                session.open(main.StvclMain)

        else:
            from Screens.MessageBox import MessageBox
            from Tools.Notifications import AddPopup
            AddPopup(_("Sorry but No Internet :("),MessageBox.TYPE_INFO, 10, 'Sorry')  
    except:
        import traceback
        traceback.print_exc() 
        pass

# def mainw(session, **kwargs):
    # try:
        # from six.moves import reload_module
        # reload_module(Utils)
        # reload_module(main)        
        # session.open(main.StvclMain)
    # except:
        # import traceback
        # traceback.print_exc()

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
