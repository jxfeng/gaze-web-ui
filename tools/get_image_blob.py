#!/usr/bin/env python

import sys
sys.path.append('../')
import gaze
import time

# Params
username='testuser'
password='testpass'

# Start up Gaze
g = gaze.gaze('http://localhost:8080/video-webapp')
s = g.login(username, password)
sid=s['sessionId']

# Upload image
ts=str(int(time.time() * 1000))
blob=open('vid0.jpg','rb').read()
img = g.upload_image(sid, username, 'camera001', ts, 'image/jpeg', 'vid0.jpg', blob)
print 'Image', img

# Fetch it
blb = g.get_blob(sid, username, 'camera001', ts)
fd=open(ts + '.jpg', 'wb')
fd.write(blb)
fd.close()
print 'Blob length', len(blb)

# Logout
g.logout(s['sessionId'])



