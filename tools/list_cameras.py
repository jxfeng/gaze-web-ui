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

# List cameras
done=False
start=None
cameras=[]
ids=dict()
while(True):
    lc = g.list_cameras(sid, username, start)
    if(lc == None or len(lc) == 0):
        break
    for c in lc:
        if(ids.has_key(c['cameraId'])):
            done=True
            break
        else:
            ids[c['cameraId']] = True
            cameras.append(c)
    if(done):
        break
    start=lc[-1]['cameraId']
    print 'Found', len(cameras), 'cameras'
print 'Cameras', cameras

# Logout
g.logout(s['sessionId'])



