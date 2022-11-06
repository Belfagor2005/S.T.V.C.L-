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

currversion = '1.3'
title_plug = 'Smart Tv Channels List'
desc_plugin = '..:: Smart Tv Channels List  V.%s ::.. ' % currversion
plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('stvcl'))
_firstStartstcl = True


class AutoStartTimertcl:

    def __init__(self, session):
        self.session = session
        global _firstStartstcl
        print("*** running AutoStartTimertcl ***")
        if _firstStartstcl:
            self.runUpdate()

    def runUpdate(self):
        print("*** running update ***")
        try:
            from . import Update
            Update.upd_done()
            _firstStartstcl = False
        except Exception as e:
            print('error Fxy', str(e))


def autostart(reason, session=None, **kwargs):
    print("*** running autostart ***")
    global autoStartTimertcl
    global _firstStartstcl
    if reason == 0:
        if session is not None:
            _firstStartstcl = True
            autoStartTimertcl = AutoStartTimertcl(session)
    return


def mainw(session, **kwargs):
    try:
        # if Utils.zCheckInternet(1):
            # try:
                # from . import Update
                # Update.upd_done()
            # except Exception as e:
                # print(str(e))
            from six.moves import reload_module
            reload_module(Utils)
            reload_module(main)
            session.open(main.StvclMain)

        # else:
            # from Screens.MessageBox import MessageBox
            # from Tools.Notifications import AddPopup
            # AddPopup(_("Sorry but No Internet :("), MessageBox.TYPE_INFO, 10, 'Sorry')
    except:
        import traceback
        traceback.print_exc()
        pass


def cfgmain(menuid):
    if menuid == 'mainmenu':
        return [(title_plug,
                 mainw,
                 desc_plugin,
                 44)]
    else:
        return []


def Plugins(**kwargs):
    piclogox = 'logo.png'
    if not os.path.exists('/var/lib/dpkg/status'):
        piclogox = plugin_path + '/res/skins/hd/logo.png'
    extDescriptor = PluginDescriptor(name=title_plug, description=_(desc_plugin), where=PluginDescriptor.WHERE_EXTENSIONSMENU, icon=piclogox, fnc=mainw)
    mainDescriptor = PluginDescriptor(name=title_plug, description=_(desc_plugin), where=PluginDescriptor.WHERE_MENU, icon=piclogox, fnc=cfgmain)
    # result = [PluginDescriptor(name=title_plug, description=_(desc_plugin), where=[PluginDescriptor.WHERE_PLUGINMENU], icon=piclogox, fnc=mainw)]
    result = [PluginDescriptor(name=title_plug, description=desc_plugin, where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=autostart),
              PluginDescriptor(name=title_plug, description=desc_plugin, where=PluginDescriptor.WHERE_PLUGINMENU, icon=piclogox, fnc=mainw)]

    if config.plugins.stvcl.strtext.value:
        result.append(extDescriptor)
    if config.plugins.stvcl.strtmain.value:
        result.append(mainDescriptor)
    return result
