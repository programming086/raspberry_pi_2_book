# -*- coding: utf-8 -*-
# Licence: GPL v.3 http://www.gnu.org/licenses/gpl.html

# Импортируем нужный модуль
import xbmcgui
import urllib,urllib2,json,re
import hashlib
import uuid
import time
from datetime import datetime

# Коды клавиатурных действий
ACTION_PREVIOUS_MENU = 10 # По умолчанию - ESC
ACTION_NAV_BACK = 92 # По умолчанию - Backspace

#  API 
api_key = '68S.rlMeTgQdw'

# 
app_id = str(uuid.getnode())
md5_app_id = hashlib.md5(app_id).hexdigest()

# список устройств поблизости
# данные датчиков устройства


# Главный класс-контейнер
class MyAddon(xbmcgui.Window):
    
    def __init__(self):
        # список устройств поблизости
        self.getDevices()
        #
        self.label0 = xbmcgui.ControlLabel(100, 50, 800, 50, u'Пример написания плагина для книги\n В.Петин Микрокомпьютеры Raspberry Pi. Практическое руководство')
        self.addControl(self.label0)
        self.label1 = xbmcgui.ControlLabel(80, 110, 400, 50, u'Список ближайших датчиков:')
        self.addControl(self.label1)
        self.label2 = xbmcgui.ControlLabel(600, 110, 300, 50, u'Показания:')
        self.addControl(self.label2)
        self.label3 = xbmcgui.ControlLabel(600, 150, 300, 50, u'Датчик:')
        self.addControl(self.label3)

    def getDevices(self):
        self.id_devices=[]
        data1 = {'cmd': 'sensorNear','uuid': md5_app_id,'api_key': api_key,'radius': 50,'lat': 44.05,         'lng': 42.80,'lang': 'ru'}
        request = urllib2.Request('http://narodmon.ru/client.php', json.dumps(data1))
        response = urllib2.urlopen(request)
        result = json.loads(response.read())
        i=0
        self.list = xbmcgui.ControlList(100, 150, 400, 500)
        self.addControl(self.list)
        for dev in result['devices']:
          el_address=dev['location'].split(", ")
          coords="( "+str(dev['lat'])+" , "+str(dev['lng'])+" )"
          title=el_address[0]+" - "+dev['name']+coords
          i=i+1
          listitem=xbmcgui.ListItem(title,str(i))
          self.list.addItem(listitem)
          #self.list.addItem(title)
          self.id_devices.append(dev['id'])
          #addDevice(title, dev['id'], 10)
        self.setFocus(self.list)
        self.label4 = xbmcgui.ControlLabel(600, 200, 500, 500, u'Данные:')
        self.addControl(self.label4)

    def getSensors(self,id_dev):
        data2 = {'cmd': 'sensorDev','uuid': md5_app_id,'api_key': api_key,'id': 1591,'lang': 'ru'}
        data2['id']=self.id_devices[id_dev-1]
        request = urllib2.Request('http://narodmon.ru/client.php', json.dumps(data2))
        response = urllib2.urlopen(request)
        #  JSON
        value1=""
        result = json.loads(response.read())
        #self.list2 = xbmcgui.ControlList(600, 200, 400, 500)
        #self.addControl(self.list2)
        for sens in result['sensors']:
          if sens['type']==1:
             value1=value1+"\nТемпература "+str(sens['value'])+" C"
          elif sens['type']==2:
             value1=value1+"\nВлажность "+str(sens['value'])+" %"
          elif sens['type']==3:
             value1=value1+"\nДавление "+str(sens['value'])+" мм.рт.ст"
          else:
             value1=value1+"\n??????? "+sens['value']
          #self.list2.addItem(value1)
        self.label4.setLabel(value1)

    def onAction(self, action):
        # Если нажали ESC или Backspace...
        if action == ACTION_NAV_BACK or action == ACTION_PREVIOUS_MENU:
            # ...закрываем плагин.
            self.close()

    def onControl(self, control):
      if control == self.list:
        item = self.list.getSelectedItem()
        self.label3.setLabel(item.getLabel())
        self.getSensors(int(item.getLabel2()))
        #self.message('You selected : ' + item.getLabel2())  
    def message(self, message):
      dialog = xbmcgui.Dialog()
      dialog.ok(" My message title", message)

if __name__ == '__main__':
    # Создаем экземпляр класса-контейнера.
    addon = MyAddon()
    # Выводим контейнер на экран.
    addon.doModal()
    # По завершении удаляем экземпляр.
    del addon
