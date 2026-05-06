# -*- coding: utf-8 -*-
import os
import sys
import xbmc
import xbmcgui
import xbmcaddon
import main

__addon__ = xbmcaddon.Addon('plugin.video.weeb.tv')
t = __addon__.getLocalizedString

os.path.join( __addon__.getAddonInfo('path'), 'resources' )

MESSAGE_TITLE = 101
MESSAGE_LINE1 = 102
MESSAGE_LINE2 = 103
MESSAGE_LINE3 = 104
MESSAGE_ACTION_OK = 110
MESSAGE_EXIT = 111

INFO_CANAL_NAME = 11
INFO_PHOTO_DIFFUSE = 12
INFO_BROADCAST = 13
INFO_PLATFORM = 15
INFO_DESCRIPTION = 16
INFO_PHOTO = 17
INFO_PLAY = 18
INFO_CANCEL = 19

SKINS = {
    'confluence': { 'normal': 50, 'list': 512, 'biglist': 51, 'thumbnail': 500 },
    'transparency': { 'normal': 590, 'list': 51, 'biglist': 52, 'thumbnail': 53 }
}

MENU = {
    1: [ t(56001).encode('utf-8'), '1.png', 1, False, False ],
    2: [ t(56002).encode('utf-8'), '2.png', 2, False, False ],
    3: [ t(56003).encode('utf-8'), '3.png', 3, False, False ],
    4: [ t(56004).encode('utf-8'), '4.png', 4, False, False ],
    5: [ t(56005).encode('utf-8'), '5.png', 5, False, False ],
    6: [ t(56006).encode('utf-8'), 'favorites.png', 6, False, False ],
    7: [ t(56007).encode('utf-8'), '7.png', 7, False, False ],
    8: [ t(56100).encode('utf-8'), 'settings.png', 8, False, False ]
}

def setViewMode(mode):
    for skin, type in SKINS.items():
        if skin in xbmc.getSkinDir():
            if mode == '4': #Normal
                xbmc.executebuiltin('Container.SetViewMode(%s)' % type['normal'])
            elif mode == '0': #List
                xbmc.executebuiltin('Container.SetViewMode(%s)' % type['list'])
            elif mode == '1': #Big list
                xbmc.executebuiltin('Container.SetViewMode(%s)' % type['biglist'])
            elif mode == '2': #Thumbnail
                xbmc.executebuiltin('Container.SetViewMode(%s)' % type['thumbnail'])

class MessageDialog(xbmcgui.WindowXMLDialog):
    def __init__(self, strXMLname, strFallbackPath, strDefaultName, forceFallback = True):
        pass
    
    def setTableText(self, tab):
        self.tabText = tab
    
    def getTableText(self):
        return self.tabText
    
    def onInit(self):
        self.getControl(MESSAGE_TITLE).setLabel(str(self.getTableText()['title']))
        self.getControl(MESSAGE_LINE1).setLabel(str(self.getTableText()['text1']))
        self.getControl(MESSAGE_LINE2).setLabel(str(self.getTableText()['text2']))
        self.getControl(MESSAGE_LINE3).setLabel(str(self.getTableText()['text3']))
    
    def onAction(self, action):
        if action == 1010:
            self.close()
    
    def onClick(self, controlID):
        if controlID == MESSAGE_ACTION_OK or controlID == MESSAGE_EXIT:
            self.onAction(1010)
    
    def onFocus(self, controlID):
        pass

class InfoDialog(xbmcgui.WindowXMLDialog):
    def __init__(self, strXMLname, strFallbackPath, strDefaultName, forceFallback = True):
        jsn = main.ShowList()
        self.channelsTab =  jsn.getJsonFromAPI(__addon__.getSetting('api_url')+__addon__.getSetting('api_path_getchannels')+main.CHANNEL_LIST_MODES[1])
    
    def setChannel(self, channel):
        self.channel = channel
    
    def getChannel(self):
        return self.channel
    
    def onInit(self):
        print '#InfoDialog onInit#'
        chanInfo = self.getChannelInfoFromJSON(self.getChannel())
        self.getControl(INFO_CANAL_NAME).setLabel(chanInfo['title'])
        self.getControl(INFO_BROADCAST).setLabel(chanInfo['user'])
        self.getControl(INFO_PHOTO).setImage(chanInfo['image'])
        self.getControl(INFO_PHOTO_DIFFUSE).setImage(chanInfo['image'])
        self.getControl(INFO_PLATFORM).setLabel(__addon__.getAddonInfo('name'))
        self.getControl(INFO_DESCRIPTION).setText(chanInfo['desc'])
    
    def onAction(self, action):
        if action == 1010:
            self.close()
        elif action == 1011:
            p = main.Handler()
            p.setIsPlay('True')
            self.close()
    
    def onClick(self, controlID):
        if controlID == INFO_CANCEL:
            self.onAction(1010)
        elif controlID == INFO_PLAY:
            self.onAction(1011)
    
    def getChannelInfoFromJSON(self, channel):
        dataInfo = { 'title': '', 'image': '', 'user': '', 'tags': '', 'desc': '' }
        try:
            for v,k in self.channelsTab.items():
                print v
                print k
                if channel == k['cid']:
                    cid = k['cid']
                    title = k['channel_title']
                    user = k['name']
                    tags = k['channel_tags'] 
                    desc = k['channel_description']
                    image = k['channel_logo_url']
                    dataInfo = { 'title': title, 'image': image, 'user': user, 'tags': tags, 'desc': desc }
                    break
        except TypeError, typerr:
            print typerr
        return dataInfo

class Windows:
    def __init__(self):
        pass
    
    def Warning(self, title, text1, text2 = '', text3 = ''):
        msg = MessageDialog('DialogWarning.xml', __addon__.getAddonInfo('path'), 'Default')
        tabText = { 'title': title, 'text1': text1, 'text2': text2, 'text3': text3 }
        msg.setTableText(tabText)
        msg.doModal()
        del msg
    
    def Error(self, title, text1, text2 = '', text3 = ''):
        msg = MessageDialog('DialogError.xml', __addon__.getAddonInfo('path'), 'Default')
        tabText = { 'title': title, 'text1': text1, 'text2': text2, 'text3': text3 }
        msg.setTableText(tabText)
        msg.doModal()
        del msg
    
    def Info(self, channel):
        info = InfoDialog('DialogInfo.xml', __addon__.getAddonInfo('path'), 'Default')
        info.setChannel(channel)
        info.doModal()
        del info
