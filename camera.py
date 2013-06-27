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
NUM_THREADS = 5
QUEUE_SIZE = NUM_THREADS * 5
FRAMES_PER_SEC=5.0
USERNAME='testuser'
PASSWORD='testpass'
CAMERA='camera001'

task_queue = Queue.Queue(QUEUE_SIZE)
queue_lock = threading.Lock()
stats = {'num_gets': 0, 'num_puts': 0}
threads = dict()

def thread_upload_image(tid, gz, delay=0.01):
    done = False
    s=gz.login(USERNAME, PASSWORD)
    sid=s['sessionId']
    while(True):
        tsk = None
        queue_lock.acquire()
        if not task_queue.empty():
            tsk = task_queue.get()
            #print 'TID: %(tid)d: Got task %(tsk)s' % {'tid':tid, 'tsk':tsk}
            stats['num_gets'] = stats['num_gets'] + 1
            queue_lock.release()
            ts=str(int(time.time() * 1000))
            filename=ts + '.jpg'
            subprocess.call(['convert', '-pointsize', '48', '-gravity', 'center', '-size', '640x480', \
                                 'xc:white', '+noise', 'Random', '-annotate', '0x0+0+0',\
                                 ts, filename])
            img=open(filename, 'rb').read()            
            gz.upload_image(sid, USERNAME, CAMERA, ts, 'image/jpeg', filename, img)
            os.remove(filename)
            print 'Uploaded image', ts
            done = True
        else:
            queue_lock.release()
            #print 'TID: %(tid)d: Queue is empty so sleep a bit' % {'tid':tid}
            time.sleep(delay)

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
for img in range(1,1000000):
    queue_lock.acquire()
    if not task_queue.full():
        task_queue.put(img)
        stats['num_puts'] = stats['num_puts'] + 1
    cur_time = time.time()
    stats_freq = 10.0
    if((cur_time - last_print_time) > stats_freq):
        ps = (stats['num_puts'] - last_num_puts)/(cur_time - last_print_time + 0.0)
        gs = (stats['num_gets'] - last_num_gets)/(cur_time - last_print_time + 0.0)
        print 'STATS: PUTS/s = %(ps)10.3f GETS/s = %(gs)10.3f' % {'ps':ps, 'gs':gs}
        last_print_time = cur_time
        last_num_puts = stats['num_puts']
        last_num_gets = stats['num_gets']
    queue_lock.release()
    time.sleep(1.0/FRAMES_PER_SEC)




        

