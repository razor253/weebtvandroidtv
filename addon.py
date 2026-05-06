# -*- coding: utf-8 -*-
import os
import sys
import xbmcplugin
import xbmcaddon
import xbmcgui

__addon__ = xbmcaddon.Addon('plugin.video.weeb.tv')
t = __addon__.getLocalizedString

HOST = 'XBMC'

sys.path.append(os.path.join(os.path.join( __addon__.getAddonInfo('path'), 'resources' ), 'lib'))

import main
import gui

class Start:
    def __init__(self):
        parser = main.UrlParser()
        params = parser.getParams()
        mode = parser.getIntParam(params, 'mode')
        if mode == None or mode == '':
            for n, v in gui.MENU.items():
                self.addDir(v[0], v[2], v[1], v[3], v[4])
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            gui.setViewMode('4')
        elif mode == 1:
            main.Handler().run(1)
            gui.setViewMode(__addon__.getSetting('channel_list_view'))
        elif mode == 2:
            main.Handler().run(2)
            gui.setViewMode(__addon__.getSetting('channel_list_view'))
        elif mode == 3:
            main.Handler().run(3)
            gui.setViewMode(__addon__.getSetting('channel_list_view'))
        elif mode == 4:
            main.Handler().run(4)
            gui.setViewMode(__addon__.getSetting('channel_list_view'))
        elif mode == 5:
            main.Handler().run(5)
            gui.setViewMode(__addon__.getSetting('channel_list_view'))
        elif mode == 6:
            gui.setViewMode('4')
            msg = gui.Windows()
            msg.Warning(t(57023).encode('utf-8'), t(57024).encode('utf-8'))
        elif mode == 7:
            gui.setViewMode('4')
            r = main.checkVersion()
            msg = gui.Windows()
            if r['status'] == 2:
                msg.Warning(t(57023).encode('utf-8'), t(57049).encode('utf-8'))
            elif r['status'] == 3:
                msg.Warning(t(57023).encode('utf-8'), t(57050).encode('utf-8'), t(57048).encode('utf-8'))
            elif r['status'] == 4:
                msg.Warning(t(57023).encode('utf-8'), t(57051).encode('utf-8'), t(57048).encode('utf-8'))
            elif r['status'] == 5:
                msg.Warning(t(57023).encode('utf-8'), t(57052).encode('utf-8'), t(57048).encode('utf-8'))
            else:
                msg.Warning(t(57023).encode('utf-8'), t(57053).encode('utf-8'), t(57054).encode('utf-8'))
        elif mode == 8:
            gui.setViewMode('4')
            __addon__.openSettings(sys.argv[0])
    
    def addDir(self, name, mode, icon, autoplay, isPlayable = True):
        u = '%s?mode=%d' % (sys.argv[0], mode)
        icon = os.path.join( __addon__.getAddonInfo('path'), 'images/' ) + icon
        if autoplay or icon == '':
            icon = 'DefaultVideo.png'
        li = xbmcgui.ListItem(name, iconImage = icon, thumbnailImage = icon)
        if autoplay and isPlayable:
            li.setProperty('IsPlayable', 'true')
        li.setInfo( type = 'Video', infoLabels = { 'Title': name } )
        xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = li, isFolder = not autoplay)

init = Start()
