#!/usr/bin/env python

import sys
sys.path.append('../')
import gaze

# Params
username='testuser'
password='testpass'

# Start up Gaze
g = gaze.gaze()
u = g.create_user(username, username + '@gmail.com', password)
print 'User', u
s = g.login(username, password)
print 'Session', s
g.logout(s['sessionId'])



