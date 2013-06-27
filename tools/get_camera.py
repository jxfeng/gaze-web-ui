#!/usr/bin/env python

import sys
sys.path.append('../')
import gaze

# Params
username='testuser'
password='testpass'

# Start up Gaze
g = gaze.gaze('http://localhost:8080/video-webapp')
s = g.login(username, password)
sid=s['sessionId']

# Get camera
c = g.get_camera(sid, 'camera001')
print 'Camera', c

# Logout
g.logout(s['sessionId'])



