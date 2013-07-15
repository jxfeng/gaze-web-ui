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

# List shards
ls = g.list_shards(sid, username, camera, limit=100)
print 'Shards', ls
ls = g.list_shards(sid, username, camera, start=24999999999)
print 'Shards', ls

# Logout
g.logout(s['sessionId'])



