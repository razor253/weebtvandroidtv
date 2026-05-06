# -*- coding: utf-8 -*-
import os
import sys
import xbmc
import xbmcplugin
import xbmcaddon
import xbmcgui
import urllib
import urllib2
import httplib
try:
    import simplejson as json
except ImportError:
    import json
import gui

__addon__ = xbmcaddon.Addon('plugin.video.weeb.tv')
t = __addon__.getLocalizedString

HOST = sys.modules[ '__main__' ].HOST

os.path.join( __addon__.getAddonInfo('path'), 'resources' )

CHANNEL_LIST_MODES = {
    1 : '&option=online-alphabetical',
    2 : '&option=online-now-viewed',
    3 : '&option=online-most-viewed',
    4 : '&option=offline-ranking',
    5 : '&option=all-ranking'
}

def checkVersion():
    status = None
    try:
        headers = { 'User-Agent' : HOST }
        post = { 'v': __addon__.getAddonInfo('version') }
        data = urllib.urlencode(post)
        request = urllib2.Request(__addon__.getSetting('api_url')+__addon__.getSetting('api_path_checkversion'), data, headers)
        response = urllib2.urlopen(request)
        responseRead = response.read()
        parser = UrlParser()
        params = parser.getParams(responseRead)
        status = parser.getIntParam(params, 'status')
        print 'Version status: %s' % (status)
    except:
        print 'Error when checking if the plugin version is up to date!'
    return { 'status': status }

class ShowList:
    def __init__(self):
        pass
    
    def decode(self, string):
        json_ustr = json.dumps(string, ensure_ascii=False)
        return json_ustr.encode('utf-8')
    
    def JsonToSortedTab(self, json):
        strTab = []
        outTab = []
        for v,k in json.iteritems():
            strTab.append(int(v))
            strTab.append(k)
            outTab.append(strTab)
            strTab = []
        outTab.sort(key=lambda x: x[0])
        return outTab
    
    def getJsonFromAPI(self, url):
        result_json = { '0': 'Null' }
        try:
            headers = { 'User-Agent': HOST, 'ContentType': 'application/x-www-form-urlencoded' }
            if __addon__.getSetting('username') != '' and __addon__.getSetting('userpassword') != '':
                post = { 'platform': HOST, 'v': __addon__.getAddonInfo('version'), 'username': __addon__.getSetting('username'), 'userpassword': __addon__.getSetting('userpassword') }
            else:
                post = { 'platform': HOST, 'v': __addon__.getAddonInfo('version') }
            data = urllib.urlencode(post)
            reqUrl = urllib2.Request(url, data, headers)
            raw_json = urllib2.urlopen(reqUrl)
            content_json = raw_json.read()
            result_json = json.loads(content_json)
        except httplib.BadStatusLine, statuserr:
            result_json = { '0': 'Error' }
            print statuserr
            msg = gui.Windows()
            msg.Error(t(57001).encode('utf-8'), t(57002).encode('utf-8'), t(57003).encode('utf-8'))
        except urllib2.URLError, urlerr:
            result_json = { '0': 'Error' }
            print urlerr
            msg = gui.Windows()
            msg.Error(t(57001).encode('utf-8'), t(57002).encode('utf-8'), t(57003).encode('utf-8'))
        except NameError, namerr:
            result_json = { '0': 'Error' }
            print namerr
            msg = gui.Windows()
            msg.Error(t(57009).encode('utf-8'), t(57010).encode('utf-8'))
        except ValueError, valerr:
            result_json = { '0': 'Error' }
            print valerr
            msg = gui.Windows()
            msg.Error(t(57001).encode('utf-8'), t(57011).encode('utf-8'), t(57012).encode('utf-8'), t(57013).encode('utf-8'))
        return result_json
    
    def loadChannels(self, listmode):
        parser = UrlParser()
        params = parser.getParams()
        mode = parser.getIntParam(params, 'mode')
        channelsArray = self.JsonToSortedTab(self.getJsonFromAPI(__addon__.getSetting('api_url')+__addon__.getSetting('api_path_getchannels')+CHANNEL_LIST_MODES[listmode]))
        if len(channelsArray) > 0:
            try:
                if channelsArray[0][1] == 'Null' or channelsArray[0][1] == 'Error':
                    msg = gui.Windows()
                    msg.Warning(t(57001).encode('utf-8'), t(57004).encode('utf-8'))
                else:
                    for i in range(len(channelsArray)):
                        k = channelsArray[i][1]
                        name = self.decode(k['channel_name']).replace("\"", '')
                        title = self.decode(k['channel_title']).replace("\"", '')
                        desc = self.decode(k['channel_description']).replace("\"", '')
                        tags = self.decode(k['channel_tags']).replace("\"", '')
                        image = k['channel_logo_url']
                        online = k['channel_online']
                        bitrate = k['multibitrate']
                        user = self.decode(k['user_name']).replace("\"", '')
                        self.addChannelToXBMC(listmode, str(mode), online, name, title, image, desc, tags, user)
                    gui.setViewMode(__addon__.getSetting('channel_list_view'))
                    xbmcplugin.endOfDirectory(int(sys.argv[1]))
                    if listmode == 1:
                        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_TITLE)
            except KeyError, keyerr:
                print keyerr
                msg = gui.Windows()
                msg.Error(t(57001).encode('utf-8'), t(57025).encode('utf-8'))
        else:
            msg = gui.Windows()
            msg.Error(t(57001).encode('utf-8'), t(57004).encode('utf-8'))
    
    def addChannelToXBMC(self, listmode, mode, online, name, title, img, desc, tags, user):
        if title is None or title == '' or title == 'null':
            title = name
            label = name
        else:
            label = title
        if desc == None or desc == '' or desc == 'null':
            desc = t(57016).encode('utf-8')
        if tags == None or tags == '' or tags == 'null':
            tags = t(57017).encode('utf-8')
        
        if __addon__.getSetting('channel_list_type') == '0':
            if int(online) == 0:
                status = '[COLOR red]' + t(57030).encode('utf-8') + '[/COLOR]'
            elif int(online) == 2:
                status = '[COLOR green]' + t(57029).encode('utf-8') + '[/COLOR]'
            else:
                status = '[COLOR green]' + t(57033).encode('utf-8') + '[/COLOR]'
            if listmode > 3:
                label = '[B]%s[/B]   [COLOR gray][I]%s [B]%s[/B]  %s [B]%s[/B][/I][/COLOR]    [B]%s[/B]' % (title, t(57031).encode('utf-8'), name, t(57032).encode('utf-8'), user, status)
            else:
                label = '[B]%s[/B]   [COLOR gray][I]%s [B]%s[/B]  %s [B]%s[/B][/I][/COLOR]' % (title, t(57031).encode('utf-8'), name, t(57032).encode('utf-8'), user)
        elif __addon__.getSetting('channel_list_type') == '1':
            if int(online) == 0:
                status = t(57030).encode('utf-8')
            elif int(online) == 2:
                status = t(57029).encode('utf-8')
            else:
                status = t(57033).encode('utf-8')
            if listmode > 3:
                label = '%s %s %s %s %s    %s ' % (title, t(57031).encode('utf-8'), name, t(57032).encode('utf-8'), user, status)
            else:
                label = '%s %s %s %s %s' % (title, t(57031).encode('utf-8'), name, t(57032).encode('utf-8'), user)
        elif __addon__.getSetting('channel_list_type') == '2':
            if int(online) == 0:
                status = t(57030).encode('utf-8')
            elif int(online) == 2:
                status = t(57029).encode('utf-8')
            else:
                status = t(57033).encode('utf-8')
            if listmode > 3:
                label = '%s [%s]' % (title, status)
            else:
                label = '%s' % (title)
         
        li = xbmcgui.ListItem(label, iconImage = 'DefaultFolder.png', thumbnailImage = img)
        li.setProperty('IsPlayable', 'false')
        li.setInfo(type = 'Video', infoLabels={ 'Title': title, 'Plot': desc, 'Studio': __addon__.getAddonInfo('name'), 'Tagline': tags, 'Status': status, 'Aired': user })
        u = '%s?mode=%d&online=%d&channel=%s&title=%s' % (sys.argv[0], int(mode), int(online), name, urllib.quote_plus(title))
        xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = li, isFolder = False)

class UrlParser:
    def __init__(self):
        pass
    
    def getParam(self, params, name):
        try:
            result = params[name]
            result = urllib.unquote_plus(result)
            return result
        except:
            return None
    
    def getIntParam (self, params, name):
        try:
            param = self.getParam(params, name)
            return int(param)
        except:
            return None
    
    def getBoolParam (self, params, name):
        try:
            param = self.getParam(params,name)
            return 'True' == param
        except:
            return None
    
    def getParams(self, paramstring = sys.argv[2]):
        param=[]
        if len(paramstring) >= 2:
            params = paramstring
            cleanedparams = params.replace('?', '')
            if (params[len(params)-1] == '/'):
                params = params[0:len(params)-2]
            pairsofparams = cleanedparams.split('&')
            param = {}
            for i in range(len(pairsofparams)):
                splitparams = {}
                splitparams = pairsofparams[i].split('=')
                if (len(splitparams)) == 2:
                    param[splitparams[0]] = splitparams[1]
        return param

class VideoPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self, *args, **kwargs)
        self.isPlayerActive = True
        self.isPremium = True
        self.tryreconnect_count = 0
        print '#(Starting control VideoPlayer events)#'
    
    def onPlayBackPaused(self):
        print '#onPlayBackPaused#'
        #self.isPlayerActive = False
    
    def onPlayBackResumed(self):
        print '#onPlayBackResumed#'
    
    def onPlayBackStarted(self):
        print '#onPlayBackStarted#'
        self.isPlayerActive = True
        self.tryreconnect_count = 0
        try:
            print '#Im playing :: ' + self.getPlayingFile()
        except:
            print '#I failed get what Im playing#'
    
    def onPlayBackEnded(self):
        print '#onPlayBackEnded#'
        if self.isPremium is False:
            msg = gui.Windows()
            msg.Warning(t(57018).encode('utf-8'), t(57019).encode('utf-8'), t(57020).encode('utf-8'))
        else:
            if __addon__.getSetting('video_autoreconnect') == 'true' and self.isPlayerActive is True:
                self.tryReconnect()
            else:
                msg = gui.Windows()
                msg.Warning(t(57018).encode('utf-8'), t(57027).encode('utf-8'))
        self.isPlayerActive = False
    
    def onPlayBackStopped(self):
        print '#onPlayBackStopped#'
        self.isPlayerActive = False
        if self.tryreconnect_count > 0 and __addon__.getSetting('video_autoreconnect') == 'true':
            self.tryReconnect()
    
    def setPlayer(self, channel):
        status = None
        rtmp = None
        imgLink = None
        title = ''
        premium = 0
        try:
            if __addon__.getSetting('username') != '' and __addon__.getSetting('userpassword') != '':
                post = { 'platform': HOST, 'v': __addon__.getAddonInfo('version'), 'channel': channel, 'username': __addon__.getSetting('username'), 'userpassword': __addon__.getSetting('userpassword') }
            else:
                post = { 'platform': HOST, 'v': __addon__.getAddonInfo('version'), 'channel': channel }
            data = urllib.urlencode(post)
            headers = { 'User-Agent' : HOST }
            request = urllib2.Request(__addon__.getSetting('api_url')+__addon__.getSetting('api_path_setplayer'), data, headers)
            response = urllib2.urlopen(request)
            responseRead = response.read()
            parser = UrlParser()
            params = parser.getParams(responseRead)
            
            status = parser.getParam(params, '0')
            premium = parser.getIntParam(params, '5')
            imgLink = parser.getParam(params, '8')
            rtmpLink = parser.getParam(params, '10')
            playPath = parser.getParam(params, '11')
            bitrate = parser.getIntParam(params, '20')
            token = parser.getParam(params, '73')
            title = parser.getParam(params, '6')
            if title == '':
                 title = parser.getParam(params, '7')
            if __addon__.getSetting('video_quality') == '2' and bitrate == 1:
                playPath = playPath + 'HI'
            elif __addon__.getSetting('video_quality') == '0' and bitrate == 2:
                playPath = playPath + 'LOW'
            
            rtmp = str(rtmpLink) + '/' + str(playPath) + ' live=true pageUrl=token swfUrl=' + str(token)
        except urllib2.URLError, urlerr:
            status = 'urllib2.URLError'
            print urlerr
        print 'Output rtmp link: %s' % (rtmp)
        return { 'status': status, 'rtmp': rtmp, 'imgLink': imgLink, 'title': title, 'premium': premium }
    
    def playChannelVideo(self, channel, silent=False):
        r = False
        self.channel = channel
        videoLink = self.setPlayer(channel)
        if videoLink['status'] == 'urllib2.URLError' and silent is not True:
            msg = gui.Windows()
            msg.Error(t(57014).encode('utf-8'), t(57015).encode('utf-8'), t(57003).encode('utf-8'))
        elif videoLink['status'] == '1':
            if videoLink['rtmp'].startswith('rtmp'):
                li = xbmcgui.ListItem(videoLink['title'], iconImage = videoLink['imgLink'], thumbnailImage = videoLink['imgLink'])
                li.setInfo(type='Video', infoLabels={ 'Title': videoLink['title'] })
                try:
                    if silent is not True:
                        self.isPremium = bool(videoLink['premium'])
                        if self.isPremium is False:
                            msg = gui.Windows()
                            msg.Warning(t(57034).encode('utf-8'), t(57036).encode('utf-8'), t(57037).encode('utf-8'), t(57038).encode('utf-8'))
                    self.play(videoLink['rtmp'], li)
                    r = True
                    while self.isPlayerActive:
                        xbmc.sleep(250)
                except:
                    if silent is not True:
                        msg = gui.Windows()
                        msg.Error(t(57018).encode('utf-8'), t(57021).encode('utf-8'))
                    r = False
            elif silent is not True:
                msg = gui.Windows()
                msg.Error(t(57018).encode('utf-8'), t(57022).encode('utf-8'))
        elif videoLink['status'] == '-1' and silent is not True:
            msg = gui.Windows()
            msg.Warning(t(57018).encode('utf-8'), t(57043).encode('utf-8'))
        elif videoLink['status'] == '-2' and silent is not True:
            msg = gui.Windows()
            msg.Warning(t(57018).encode('utf-8'), t(57044).encode('utf-8')) 
        elif videoLink['status'] == '-3' and silent is not True:
            msg = gui.Windows()
            msg.Warning(t(57018).encode('utf-8'), t(57045).encode('utf-8'))
        elif videoLink['status'] == '-4' and silent is not True:
            msg = gui.Windows()
            msg.Warning(t(57018).encode('utf-8'), t(57046).encode('utf-8'), t(57047).encode('utf-8'))
        elif silent is not True:
            msg = gui.Windows()
            msg.Warning(t(57018).encode('utf-8'), t(57042).encode('utf-8'))
        return r
    
    def tryReconnect(self):
        xbmc.sleep(500)
        if self.tryreconnect_count > 0:
            xbmc.sleep(int(__addon__.getSetting('video_autoreconnect_sleep')))
        print 'Debug: tryreconnect_count: ' + str(self.tryreconnect_count)
        if self.tryreconnect_count < 4:
            self.tryreconnect_count = self.tryreconnect_count+1
            if self.playChannelVideo(self.channel, True) is False:
                print '#playChannelVideo returned False, trying to reconnect again!'
                self.tryReconnect()
        else:
            msg = gui.Windows()
            msg.Warning(t(57018).encode('utf-8'), t(57027).encode('utf-8'))

class Handler:
    def __init__(self):
        pass
    
    def run(self, mode):
        parser = UrlParser()
        params = parser.getParams()
        mode = parser.getIntParam(params, 'mode')
        channel = parser.getParam(params, 'channel')
        online = parser.getIntParam(params, 'online')
        if mode > 0 and mode < 6 and online == None:
            ShowList().loadChannels(mode)
        elif mode > 0 and mode < 6 and online == 2 and channel != '' or channel is None:
            try:
                VideoPlayer().playChannelVideo(channel)
            except:
                VideoPlayer().playChannelVideo(channel)
        elif mode > 0 and mode < 6 and online == 0 and channel != '' or channel is None:
            msg = gui.Windows()
            msg.Warning(t(57005).encode('utf-8'), t(57006).encode('utf-8'), t(57007).encode('utf-8'))
