#!/usr/bin/env python

import os
import sys
import thread
import threading
import Queue
import datetime
import time
import logging
import subprocess
import cv2
from cv2 import cv
import numpy as np
import random
import gaze

# Global parameters
GAZE_URL='http://localhost:8080/gaze-web-app' #'http://gazeapi.elasticbeanstalk.com'
NUM_THREADS = 25
QUEUE_SIZE = NUM_THREADS * 5
RAMP_FRAMES=25
STATS_PRINT_TIME=1.0
MAX_IMAGES=10000

# Parse command line arguments
if(len(sys.argv) < 7):
    sys.stderr.write('USAGE: %(p)s <username> <password> <camera-id> <generator> <single-file> <rate> [other]\n' % {'p':sys.argv[0]})
    sys.stderr.write('<generator>: random, webcam, file\n')
    sys.stderr.write('file: <filename>\n')
    sys.exit(-1)

USERNAME=sys.argv[1]
PASSWORD=sys.argv[2]
CAMERA=sys.argv[3]
GENERATOR=sys.argv[4]
SINGLE_FILE=sys.argv[5]
FRAMES_PER_SEC=float(sys.argv[6])
OTHER=None
if(len(sys.argv) > 7):
    OTHER=sys.argv[7:]
if(SINGLE_FILE == 'True' or SINGLE_FILE == 'true' or SINGLE_FILE == 'TRUE'):
    SINGLE_FILE=True
else:
    SINGLE_FILE=False

# Image generator (uses OpenCV)
def get_image(generator, single_image, stats, stats_lock, state, other_params):
    ts_img_create_start=time.time()
    if(generator == 'file'):
        state['filename'] = other_params[0]
        retval = get_file_image(single_image, state)
    elif(generator == 'webcam'):
        retval = get_webcam_image(single_image, state)
    elif(generator == 'random'):
        retval = get_random_image(single_image, state)
    else:
        sys.stderr.write('Not a valid image generator!\n')
        retval = None
    ts_img_create_end=time.time()
    # Update stats
    stats_lock.acquire()
    stats['total_img_time'] = stats['total_img_time'] + (ts_img_create_end-ts_img_create_start)
    stats['num_imgs'] = stats['num_imgs'] + 1
    stats_lock.release()
    return retval

def write_image_to_file(filename, data, opencv=False):
    try:
        if(opencv == False):
            fd = open(filename, 'wb')
            fd.write(data)
            fd.close()
        else:
            cv2.imwrite(filename, data)
    except IOError:
        sys.stderr.write('Could not open filename %(f)s\n' % {'f':filename})
        return None

def get_file_image(single_image, state):
    if(state == None):
        state = dict()
    if(single_image and state.has_key('img')):
        return (state, state['img'])
    else:
        try:
            if(state.has_key('filename')):
                img = open(state['filename'], 'rb').read()
                state['img'] = img
                write_image_to_file('blah.jpg', img)
                return (state, img)
            else:
                sys.stderr.write('No filename defined\n')
                return None
        except IOError as error:
            sys.stderr.write('Could not open file %(f)s\n' % {'f':state['filename']})
            return None

def get_random_image(single_image, state):
    if(state == None):
        state=dict()
    if(single_image and state_has_key('img')):
        return (state, state['img'])
    else:
        iw, ih = 640, 480
        img = np.zeros((ih,iw,3), np.uint8)        
        img[:,:] = (255,255,255)
        # Put random circles
        for ci in xrange(1,25):
            clr = (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255))
            cp = (random.randrange(0,iw), random.randrange(0,ih))
            cw = random.randrange(0,100)
            cv2.circle(img, cp, cw, clr, -1)
        # Put timestamp
        blp = (0,ih-1)
        ts = 'TIME: ' + str(time.time())
        cv2.putText(img, ts, blp, cv.CV_FONT_HERSHEY_TRIPLEX, 1, (0,0,0))
        (retval, img) = cv2.imencode('.jpg',img)
        write_image_to_file('/tmp/temp.jpg', img)
        img = open('/tmp/temp.jpg', 'rb').read()
        state['img'] = img
        return (state, state['img'])

def get_webcam_image(single_image, state):
    if(state == None):
        state = dict()
    if(single_image and state.has_key('img')):
        return (state, state['img'])
    else:
        # Get camera
        camera = None
        if(state.has_key('camera')):
            camera = state['camera']
        else:
            camera = cv2.VideoCapture(0)
            state['camera']=camera
        # Initialize the camera by taking some starter images
        if(state.has_key('first') == False):
            for i in xrange(10):
              retval, im = camera.read()
            state['first'] = True
        # Take a shot
        retval, img = camera.read()
        (retval, img)=cv2.imencode('.jpg', img)
        write_image_to_file('/tmp/temp.jpg', img)
        img = open('/tmp/temp.jpg', 'rb').read()
        state['img'] = img
        return (state, state['img'])

# Image upload functions
def thread_upload_image(tid, gz, task_queue, done_db, queue_lock, stats, stats_lock, delay=0.01):
    done = False
    try:
        s=gz.login(USERNAME, PASSWORD)
        sid=s['sessionId']
        x=1
    except Exception as error:
        print 'Could not login into system', error, s
        return None
    holding_lock = False
    while(True):
        tsk = None
        try:
            holding_lock = True
            queue_lock.acquire()
            if not task_queue.empty():
                tsk = task_queue.get()
                queue_lock.release()
                holding_lock = False
                # Upload image
                ts_img_upload_start=time.time()
                #time.sleep(random.random()/10.0)
                #gz.health_check()
                gz.upload_image(sid, USERNAME, CAMERA, tsk['ts'], 'image/jpeg', tsk['filename'], tsk['data'])
                #gz.get_camera(sid, CAMERA)
                ts_img_upload_end=time.time()            
                # Record completion
                queue_lock.acquire()
                done_db[tsk['id']] = tsk['ts']
                queue_lock.release()
                # Update stats
                stats_lock.acquire()
                stats['num_dequeues'] = stats['num_dequeues'] + 1
                stats['num_uploads'] = stats['num_uploads'] + 1
                stats['total_upload_time'] = stats['total_upload_time'] + (ts_img_upload_end-ts_img_upload_start)
                stats_lock.release()
                done = True
            else:
                queue_lock.release()
                holding_lock = False
                #time.sleep(delay)
        except Exception as error:
            print 'Got Exception', error
            time.sleep(0.5)
        finally:
            if(holding_lock):
                queue_lock.release()
                holding_lock = False

# Main
def main(username=USERNAME, password=PASSWORD, camera=CAMERA, \
             generator=GENERATOR, single_file=SINGLE_FILE, frames_per_sec=FRAMES_PER_SEC, \
             other_params=OTHER):
    # 0. Initialize variables
    state=dict()
    stats={'num_enqueues':0, 'num_dequeues':0, 'num_uploads':0, 'num_imgs': 0, 'total_img_time':0, 'total_upload_time':0}
    threads=dict()
    task_queue = Queue.Queue(QUEUE_SIZE)
    done_db = dict()
    queue_lock = threading.Lock()
    stats_lock = threading.Lock()
    last_stats=None
    last_stats_print_time=time.time()
    num_images=0
    main_gz=gaze.gaze(GAZE_URL)
    # 1. Create threads
    for tid in range(0, NUM_THREADS):
        gz = gaze.gaze(GAZE_URL)
        thd = thread.start_new_thread(thread_upload_image, (tid, gz, task_queue, done_db, queue_lock, stats, stats_lock))
        threads[tid] = thd
    # 2. Create and load images in a loop
    while(num_images < MAX_IMAGES):
        num_images += 1
        ts_loop_start=time.time()
        # 2.1 Generate image
        ts_img_create_start = time.time()
        (state, img) = get_image(generator, single_file, stats, stats_lock, state, other_params)
        if(state == None or img == None):
            sys.stderr.write('Could not get image!\n')
            return None
        ts=str(int(time.time() * 1000))
        filename=ts + '.jpg'
        tsk = {'ts':ts, 'id':num_images, 'filename':filename, 'data':img}
        ts_img_create_stop = time.time()
        # 2.2 Put into queue
        did_put=False
        queue_lock.acquire()
        if not task_queue.full():
            task_queue.put(tsk)
            did_put = True
        queue_lock.release()
        # 2.3 Send commit 
        queue_lock.acquire()
        keys = done_db.keys()
        keys.sort()
        mk=None
        contig=[]
        for k in keys:
            if(mk == None or (mk + 1 == k)):
                contig.append(k)
                mk = k
            else:
                break
        contig.sort()
        if(len(contig) > 0):
            print 'Contiguous', contig
            print 'Send commit', done_db[contig[-1]]
            for k in contig:
                del done_db[k]
        queue_lock.release()
        # 2.4 Update/print stats        
        stats_lock.acquire()
        cur_time=time.time()
        last_time=last_stats_print_time
        if(did_put):
            stats['num_enqueues'] = stats['num_enqueues'] + 1
        diff_stats=None
        if(last_stats != None and (cur_time-last_time) >= STATS_PRINT_TIME):
            diff_stats=dict()
            for key in stats.keys():
                diff_stats[key] = stats[key] - last_stats[key]
            last_stats_print_time = cur_time
            last_stats = dict()
            for key in stats.keys():
                last_stats[key] = stats[key]
        if(last_stats == None):
            last_stats = dict()
            for key in stats.keys():
                last_stats[key] = stats[key]
        stats_lock.release()
        if(diff_stats != None):
            diff_time=cur_time - last_time
            buf = '%(t)10.3f ENQUEUES=%(e)10d DEQUEUES=%(d)10d IMGS=%(i)10d UPLOADS=%(u)10d IMG_TIME=%(it)10.3f UPLOAD_TIME=%(ut)10.3f' \
                % {'t':diff_time, 'e':diff_stats['num_enqueues'], 'd':diff_stats['num_dequeues'], \
                       'i':diff_stats['num_imgs'], 'u':diff_stats['num_uploads'],\
                       'it':diff_stats['total_img_time'],\
                       'ut':diff_stats['total_upload_time']}
            print buf
        ts_loop_end = time.time()
        # 2.4 Wait for a bit to catchup with preferred frame rate
        rate_time = 1.0/frames_per_sec
        rate_diff=(rate_time-(ts_loop_end-ts_loop_start))
        if(rate_diff > 0):
            time.sleep(rate_diff)

# Run main
main()





        

