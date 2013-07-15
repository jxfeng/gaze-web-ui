#!/usr/bin/env python

import sys
sys.path.append('../')
import gaze

# Params
hostname='http://localhost:8080/gaze-web-app'
username='testuser'
password='testpass'

# Start up Gaze
g = gaze.gaze(hostname)
h = g.health_check()
print 'Health', h
u = g.create_user(username, username + '@gmail.com', password)
print 'User', u
s = g.login(username, password)
print 'Session', s
#g.logout(s['sessionId'])



