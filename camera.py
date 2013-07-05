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
import gaze

GAZE_URL='http://gazeapi.elasticbeanstalk.com'
NUM_THREADS = 100
QUEUE_SIZE = NUM_THREADS * 5
FRAMES_PER_SEC=1000.0
USERNAME='testuser'
PASSWORD='testpass'
CAMERA='camera001'

task_queue = Queue.Queue(QUEUE_SIZE)
queue_lock = threading.Lock()
stats = {'num_gets': 0, 'num_puts': 0}
threads = dict()

def thread_upload_image(tid, gz, delay=0.01):
    done = False
    try:
        s=gz.login(USERNAME, PASSWORD)
        sid=s['sessionId']
    except Exception as error:
        print 'Exception', error, s
        sys.exit(-1)
    holding_lock = False
    num_uploaded = 0
    while(True):
        tsk = None
        try:
            holding_lock = True
            queue_lock.acquire()
            if not task_queue.empty():
                tsk = task_queue.get()
                stats['num_gets'] = stats['num_gets'] + 1
                queue_lock.release()
                holding_lock = False
                # Upload image
                ts_img_upload_start=time.time()
                #gz.health_check()
                gz.upload_image(sid, USERNAME, CAMERA, tsk['ts'], 'image/jpeg', tsk['filename'], tsk['data'])
                #gz.get_camera(sid, CAMERA)
                ts_img_upload_end=time.time()            
                # Print stats
                num_uploaded += 1
                if(num_uploaded % 10 == 0):
                    print 'Thread %(tid)d uploaded %(num)d images' % {'tid':tid, 'num':num_uploaded}
                #print 'TIME: upload: %(u)10.3f' % {'u':(ts_img_upload_end-ts_img_upload_start)}
                done = True
            else:
                queue_lock.release()
                holding_lock = False
                #print 'TID: %(tid)d: Queue is empty so sleep a bit' % {'tid':tid}
                time.sleep(delay)
        except Exception as error:
            print 'Exception', error
            time.sleep(0.5)
        finally:
            if(holding_lock):
                queue_lock.release()
                holding_lock = False

# Start up threads
for tid in range(0,NUM_THREADS):
    gz = gaze.gaze(GAZE_URL)
    thd = thread.start_new_thread( thread_upload_image, (tid, gz))
    threads[tid] = thd
    time.sleep(0.01)

# Main thread
last_num_puts = 0
last_num_gets = 0
last_print_time = time.time()

# Create image beforehand
temp_filename='blah.jpg'
subprocess.call(['convert', '-pointsize', '48', '-gravity', 'center', '-size', '640x480', \
                     'xc:white', '+noise', 'Random', '-annotate', '0x0+0+0',\
                     '0000', temp_filename])
imgdata=open(temp_filename, 'rb').read()
os.remove(temp_filename)

for i in range(1,1000000):
    # Create new image
    ts=str(int(time.time() * 1000))
    filename=ts + '.jpg'
    tsk = {'ts':ts, 'filename':filename, 'data':imgdata}
    # Load into queue
    queue_lock.acquire()
    if not task_queue.full():
        task_queue.put(tsk)
        stats['num_puts'] = stats['num_puts'] + 1
    cur_time = time.time()
    stats_freq = 2.0
    if((cur_time - last_print_time) > stats_freq):
        ps = (stats['num_puts'] - last_num_puts)/(cur_time - last_print_time + 0.0)
        gs = (stats['num_gets'] - last_num_gets)/(cur_time - last_print_time + 0.0)
        print 'STATS: TS: %(ts)10.3f PUTS/s = %(ps)10.3f GETS/s = %(gs)10.3f' % {'ts':cur_time, 'ps':ps, 'gs':gs}
        last_print_time = cur_time
        last_num_puts = stats['num_puts']
        last_num_gets = stats['num_gets']
    queue_lock.release()
    # Sleep to set the right rate of upload
    time.sleep(1.0/FRAMES_PER_SEC)




        

