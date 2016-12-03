#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import subprocess
import time
import sys

while True:
     try:
        a = os.system('julius -quiet -input mic -C /home/pi/julius_model2/julian.jconf 2>/dev/null | ./julius_to_text.py')
        time.sleep(1)
     except KeyboardInterrupt:
		sys.exit(1)


