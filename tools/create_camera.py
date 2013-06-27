#!/usr/bin/env python

import sys
sys.path.append('../')
import gaze

# Params
username='testuser'
password='testpass'

# Start up Gaze
g = gaze.gaze()
s = g.login(username, password)
sid=s['sessionId']

# Create camera
for i in range(1,5):
    c = g.create_camera(sid, username, 'camera%(id)03d' % {'id':i})
    print 'Camera', c

# Logout
g.logout(s['sessionId'])



