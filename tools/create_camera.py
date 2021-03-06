#!/usr/bin/env python

import sys
sys.path.append('../')
import gaze

# Params
hostname='http://localhost:8080/gaze-web-app'
username='testuser'
password='testpass'
n=25

# Start up Gaze
g = gaze.gaze(hostname)
s = g.login(username, password)
sid=s['sessionId']

# Create camera
for i in range(1,n):
    c = g.create_camera(sid, username, 'camera%(id)03d' % {'id':i})
    print 'Camera', c

# Update them
for i in range(1,n):
    c = g.update_camera(sid, username, 'camera%(id)03d' % {'id':i}, name='Camera-%(id)03d' % {'id':i})
    print 'Camera', c

# Logout
g.logout(s['sessionId'])



