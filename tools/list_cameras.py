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
s = g.login(username, password)
sid=s['sessionId']

# List cameras
done=False
start=None
cameras=[]
ids=dict()
while(True):
    print 'Start', start
    lc = g.list_cameras(sid, username, start=start)
    print 'List', lc
    if(lc == None or len(lc) == 0):
        break
    for c in lc:
        if(ids.has_key(c['cameraId'])):
            done=False
            print 'Found repeat', c['cameraId']
            break
        else:
            ids[c['cameraId']] = True
            cameras.append(c)
    if(done):
        break
    start=lc[-1]['cameraId']
    #print 'Found', len(cameras), 'cameras'
print 'Cameras', cameras

# Reverse iterator
lc=g.list_cameras(sid, username, start=None, limit=5)
#print 'Forward', lc
print 'Last',lc[-1]['cameraId']
lc=g.list_cameras(sid, username, start=lc[-1]['cameraId'], reverse=True, limit=2)
print 'Reverse', lc

# Logout
g.logout(s['sessionId'])



