#!/usr/bin/env python

import sys
sys.path.append('../')
import gaze
import time

# Params
hostname='http://localhost:8080/gaze-web-app'
username='testuser'
password='testpass'
camera='camera001'

# Start up Gaze
g = gaze.gaze(hostname)
s = g.login(username, password)
sid=s['sessionId']

# List images
li = g.list_images(sid, username, camera, limit=50)
print 'Images', len(li), li
li = g.list_images(sid, username, camera, limit=10, reverse=True)
print 'Images', len(li), li
li = g.list_images(sid, username, camera, since=int(time.time()*1000), limit=10, reverse=True)
print 'Images', len(li), li

# Logout
g.logout(s['sessionId'])



