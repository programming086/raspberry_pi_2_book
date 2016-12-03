#!/usr/bin/env python
# -*- coding: utf-8 -*-



import os
import subprocess
import sys

var1=0

while var1==0:
       startstring = 'sentence1: <s> '
       endstring = ' </s>'
       line = sys.stdin.readline()
       if not line:
           pass
       else:   
           end = len(line)-6
           if line[0:9] == 'sentence1':
             word = line[15:end]
             print word
   
   
