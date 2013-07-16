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

# Get all stats
stats = g.get_stats(sid, username)
print 'Total images', stats['totalImages']
print 'Total bytes used by origin', stats['bytesUsedByVariation']['ORIGINAL']

# Print cameras
for cs in stats['cameraStats']:
    print 'Camera', cs['cameraId'], cs['totalImages']
    for ss in cs['shardStats']:
        print 'Shard', ss['shardId'], ss['totalImages'], ss['numImagesByVariation']

# Logout
g.logout(s['sessionId'])



