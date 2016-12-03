#!/usr/bin/env python
#-*-coding:utf-8 -*-
#  Скрипт проверки новых писем
#  на почте gmail
#  и оповещение голосом (espeak)

import subprocess
import shlex
import feedparser
import webbrowser

USERNAME="victor.petin@gmail.com"
PASSWORD="PVA191066"
DIR="/home/petin/PRG/gmail_espeak/"
#DIR="/home/pi/python_prg/gmail_espeak/"


ff=feedparser.parse("https://" + USERNAME + ":" + PASSWORD + "@mail.google.com/gmail/feed/atom");
count_letters = int(ff["feed"]["fullcount"])
if count_letters > 0: 
    print("Есть новые письма")
    command1='espeak -vru -a150 -s80 "Многоуважаемый хозяин, У вас '
    if count_letters>9 and count_letters<20:
       command1+=str(count_letters)
       command1+=' новых  писем"'
    elif count_letters%10==1:
       if(count_letters>10):
          command1+=str(int(count_letters/10)*10)
       command1+=" одно"
       command1+=' новое письмо"'
    elif count_letters%10>4 or count_letters%10==0:
       if(count_letters>10):
          command1+=str(int(count_letters/10)*10)
       command1+=str(count_letters%10)
       command1+=' новых писем"'
    else:
       if(count_letters>10):
          command1+=str(int(count_letters/10)*10)
       command1+=str(count_letters%10)
       command1+=' новых письма"'
    #print ff["entries"][1].title
    fhtml=open(DIR+"links.html","w")
    for i in range(0,len(ff["entries"])):
       str2=str(i+1)+". ";
       str2+="<a href='"+ff["entries"][i].link+"'>";
       str2+=ff["entries"][i].title+"</a><br>";
       print str2
       fhtml.write(str2.encode('windows-1251'))

    fhtml.close()
    command1+=' 2>/dev/null'
    #print command1
    webbrowser.open(DIR+"links.html")
    subprocess.Popen(command1,shell=True).communicate()

else: 
    print("Нет новых писем")



