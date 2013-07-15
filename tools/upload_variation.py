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

# Iterate and change images
li = g.list_images(sid, username, camera)
for i in li:
    ts = i['imageTimestamp']
    blob = g.get_blob(sid, username, camera, ts)
    iv = g.upload_image(sid, username, camera, ts, 'image/jpeg', 'blob.jpg', blob, variation='RT_FEATURE_DETECTED')
    print 'Image', iv

# Logout
g.logout(s['sessionId'])



