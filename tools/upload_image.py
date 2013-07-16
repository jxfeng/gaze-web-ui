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

# Upload image
ts=0
for t in range(1,10):
    ts=str(int(time.time() * 1000))
    #ts=t*1000000000
    blob=open('vid0.jpg','rb').read()
    img = g.upload_image(sid, username, camera, ts, 'image/jpeg', 'vid0.jpg', blob)
    print 'Image', img


# Commit it
cm = g.commit_image(sid, username, camera, ts)
print 'Camera', cm

# Logout
g.logout(s['sessionId'])



