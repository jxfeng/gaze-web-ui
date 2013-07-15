#!/usr/bin/python

import os
import sys
import requests
import json
from datetime import datetime, date, time

class gaze:
    """A simple wrapper around REST to provide functions instead of raw HTTP"""
    def __init__(self, root_url=None):
        self.LOGFILE = open('/tmp/gaze.log', 'w')
        if(root_url != None):
            self.ROOT_URL = root_url
            self.LOG('INFO: Using root url of ' + str(self.ROOT_URL))
        else:
            self.ROOT_URL = 'http://gazeapi.elasticbeanstalk.com'
        self.session = None
        self.session_num_requests = 0
    def LOG(self, msg):
        ts = datetime.now()
        self.LOGFILE.write('%(ts)25s %(m)s\n' % {'ts':ts, 'm':msg})
    def __SESSION(self):
        if(self.session == None or self.session_num_requests > 10):
            if(self.session != None):
                self.session.close()
                self.session = None
            self.session = requests.Session()
            self.session_num_requests = 0
        self.session_num_requests += 1
    def GET(self, path, headers, params):
        url = self.ROOT_URL + path
        self.LOG('REQUEST: GET: %(p)s' % {'p':url})
        self.__SESSION()
        res = self.session.get(url, headers=headers, params=params)
        if(res == None or res.status_code != requests.codes.ok):
            self.LOG('REPLY: ERROR: GET: %(p)s TEXT: %(j)s MSG: %(m)s' % {'p':path, 'j':res.text, 'm':res})
            return None
        else:
            self.LOG('REPLY: SUCCESS: GET: %(p)s' % {'p':path})
            json_data = None
            try:
                json_data = res.json()
            except ValueError:
                json_data = None
            #print res.headers
            res.stream = False
            return {'status':res.status_code, 'response':res, 'json': json_data}
    def POST(self, path, headers, params, json_data=None, file_data=None):
        url = self.ROOT_URL + path
        self.LOG('REQUEST: POST: %(p)s' % {'p':url})
        self.__SESSION()
        res = None
        if(json_data != None and file_data == None):
            res = self.session.post(url, headers=headers, params=params, data=json.dumps(json_data))
        elif(json_data == None and file_data != None):
            res = self.session.post(url, headers=headers, params=params, files=file_data)
        else:
            res = self.session.post(url, headers=headers, params=params)
        if(res == None or res.status_code != requests.codes.ok):
            self.LOG('REPLY: ERROR: POST: %(p)s TEXT: %(j)s MSG: %(m)s' % {'p':path, 'j':res.text, 'm':res})
            return None
        else:
            self.LOG('REPLY: SUCCESS: POST: %(p)s' % {'p':path})
            json_data = None
            try:
                json_data = res.json()
            except ValueError:
                json_data = None
            res.stream = False
            return {'status':res.status_code, 'response':res, 'json': json_data}
    def health_check(self):
        headers = {'Accepts': 'application/json'}
        ep = '/healthcheck'
        res = self.GET(ep, headers, None)
        if(res == None or res['status'] != requests.codes.ok):
            self.LOG('HEALTH-CHECK: FAILED: ')
            return None
        assert(res != None and res['status'] == requests.codes.ok)
        stat = res['json']
        return stat
    def create_user(self, username, email, password):
        data = {'userHandle':username, 'emailAddress':email, 'password': password}
        headers = {'Content-type': 'application/json', 'Accepts': 'application/json'}
        res = self.POST('/api/user', headers, None, json_data=data)
        if(res == None or res['status'] != requests.codes.ok):
            self.LOG('CREATE-USER: FAILED: username: %(u)s password: %(p)s' % {'u':username, 'p':password})
            return None
        assert(res != None and res['status'] == requests.codes.ok)
        u = res['json']
        return u
    def login(self, username, password):
        data = {'userId':username, 'password':password}
        headers = {'Content-type': 'application/json', 'Accepts': 'application/json'}
        res = self.POST('/api/authenticate', headers, None, json_data=data)
        if(res == None or res['status'] != requests.codes.ok):
            self.LOG('LOGIN: FAILED: username: %(u)s password: %(p)s' % {'u':username, 'p':password})
            return None
        assert(res != None and res['status'] == requests.codes.ok)
        s = res['json']
        return s
    def logout(self, session_id):
        headers = {'Accepts': 'application/json','x-application-session-id': session_id}
        res = self.POST('/api/logout', headers, None)
        if(res == None or res['status'] != requests.codes.ok):
            self.LOG('LOGOUT: FAILED: session_id: %(s)s' % {'s':session_id})
            return False
        assert(res != None and res['status'] == requests.codes.ok)
        return True
    def create_camera(self, session_id, user_id, camera_id):
        headers = {'Content-type': 'application/json', 'Accepts': 'application/json','x-application-session-id': session_id}
        url = '/api/camera/' + camera_id
        data = {'userId':user_id, 'cameraId':camera_id}
        res = self.POST(url, headers, None, json_data=data)
        if(res == None or res['status'] != requests.codes.ok):
            self.LOG('CREATE-CAMERA: FAILED: session_id: %(s)s camera_id:%(c)s' \
                         % {'s':session_id, 'c':camera_id})
            return False
        assert(res != None and res['status'] == requests.codes.ok)
        s = res['json']
        return s
    def update_camera(self, session_id, user_id, camera_id, name=None, location=None):
        headers = {'Content-type': 'application/json', 'Accepts': 'application/json','x-application-session-id': session_id}
        url = '/api/camera/' + camera_id
        data = {'userId':user_id, 'cameraId':camera_id, 'cameraName':name, 'cameraLocation':location}
        res = self.POST(url, headers, None, json_data=data)
        if(res == None or res['status'] != requests.codes.ok):
            self.LOG('CREATE-CAMERA: FAILED: session_id: %(s)s camera_id:%(c)s' \
                         % {'s':session_id, 'c':camera_id})
            return False
        assert(res != None and res['status'] == requests.codes.ok)
        s = res['json']
        return s
    def list_cameras(self, session_id, user_id, limit=10, start=None, reverse=False):
        if(limit == None or limit < 0 or limit > 100):
            limit = 10
        params={'limit': limit, 'reverse':reverse}
        if(start != None):
            params['start'] = start
        headers = {'Accepts': 'application/json','x-application-session-id': session_id}
        res = self.GET('/api/camera/list', headers, params)
        if(res == None or res['status'] != requests.codes.ok):
            self.LOG('LIST-CAMERAS: FAILED: username: %(u)s limit:%(l)d start:%(s)s' % {'u':user_id, 'l':limit, 's':start})
            return None
        assert(res != None and res['status'] == requests.codes.ok)
        self.LOG('LIST-CAMERAS: SUCCESS: username: %(u)s limit:%(l)d start:%(s)s' % {'u':user_id, 'l':limit, 's':start})
        lc = res['json']
        return lc
    def get_camera(self, session_id, camera_id):
        headers = {'Accepts': 'application/json','x-application-session-id': session_id}
        ep = '/api/camera/' + camera_id 
        res = self.GET(ep, headers, None)
        if(res == None or res['status'] != requests.codes.ok):
            self.LOG('GET-CAMERA: FAILED: session_id: %(s)s' % {'s':session_id})
            return None
        assert(res != None and res['status'] == requests.codes.ok)
        cam = res['json']
        return cam
    def list_shards(self, session_id, user_id, camera_id, limit=10, start=None, reverse=False):
        if(limit == None or limit < 0 or limit > 100):
            limit = 10
        params={'limit': limit, 'reverse':reverse}
        if(start != None):
            params['from'] = start
        headers = {'Accepts': 'application/json','x-application-session-id': session_id}
        ep='/api/camera/%(c)s/list-shards' % {'c':camera_id}
        res = self.GET(ep, headers, params)
        if(res == None or res['status'] != requests.codes.ok):
            self.LOG('LIST-SHARDS: FAILED: username: %(u)s camera: %(c)s limit:%(l)d from:%(s)s' \
                         % {'u':user_id, 'c':camera_id, 'l':limit, 's':start})
            return None
        assert(res != None and res['status'] == requests.codes.ok)
        self.LOG('LIST-SHARDS: SUCCESS: username: %(u)s camera: %(c)s limit:%(l)d start:%(s)s' \
                     % {'u':user_id, 'c':camera_id, 'l':limit, 's':start})
        lc = res['json']
        return lc
    def upload_image(self, session_id, user_id, camera_id, img_id, img_type, img_name, img, variation='ORIGINAL'):
        headers = {'Accepts': 'application/json','x-application-session-id': session_id}
        ep = '/api/image/%(cid)s/%(iid)s' % {'cid':camera_id, 'iid': img_id}
        params={'variation':variation}
        files={'uploaded-image':(img_name, img)}
        res = self.POST(ep, headers, params, file_data=files)
        if(res == None or res['status'] != requests.codes.ok):
            self.LOG('UPLOAD: FAILED: session_id: %(s)s' % {'s':session_id})
            return None
        assert(res != None and res['status'] == requests.codes.ok)
        im = res['json']
        return im
    def commit_image(self, session_id, user_id, camera_id, img_id):
        headers = {'Accepts': 'application/json','x-application-session-id': session_id}
        ep = '/api/camera/%(cid)s/commit/%(iid)s' % {'cid':camera_id, 'iid': img_id}
        res = self.POST(ep, headers, None)
        if(res == None or res['status'] != requests.codes.ok):
            self.LOG('COMMIT: FAILED: session_id: %(s)s' % {'s':session_id})
            return None
        assert(res != None and res['status'] == requests.codes.ok)
        cm = res['json']
        return cm
    def list_images(self, session_id, user_id, camera_id, limit=10, since=None, reverse=False):
        if(limit == None or limit < 0 or limit > 100):
            limit = 10
        params={'limit': limit, 'reverse':reverse}
        if(since != None):
            params['since'] = since
        headers = {'Accepts': 'application/json','x-application-session-id': session_id}
        ep='/api/image/%(c)s/list' % {'c':camera_id}
        res = self.GET(ep, headers, params)
        if(res == None or res['status'] != requests.codes.ok):
            self.LOG('LIST-IMAGES: FAILED: username: %(u)s camera: %(c)s limit:%(l)d since:%(s)s' \
                         % {'u':user_id, 'c':camera_id, 'l':limit, 's':since})
            return None
        assert(res != None and res['status'] == requests.codes.ok)
        self.LOG('LIST-IMAGES: SUCCESS: username: %(u)s camera: %(c)s limit:%(l)d since:%(s)s' \
                     % {'u':user_id, 'c':camera_id, 'l':limit, 's':since})
        li = res['json']
        return li
    def get_image(self, session_id, user_id, camera_id, img_id):
        headers = {'Accepts': 'application/json','x-application-session-id': session_id}
        ep = '/api/image/%(cid)s/%(iid)s' % {'cid':camera_id, 'iid': img_id}
        res = self.GET(ep, headers, None)
        if(res == None or res['status'] != requests.codes.ok):
            self.LOG('GET-IMAGE: FAILED: session_id: %(s)s' % {'s':session_id})
            return None
        assert(res != None and res['status'] == requests.codes.ok)
        im = res['json']
        return im
    def list_variations(self, session_id, user_id, camera_id, img_id):
        headers = {'Accepts': 'application/json','x-application-session-id': session_id}
        ep = '/api/image/%(cid)s/%(iid)s/variations' % {'cid':camera_id, 'iid': img_id}
        res = self.GET(ep, headers, None)
        if(res == None or res['status'] != requests.codes.ok):
            self.LOG('LIST-VARIATIONS: FAILED: session_id: %(s)s' % {'s':session_id})
            return None
        assert(res != None and res['status'] == requests.codes.ok)
        blbs = res['json']
        return blbs
    def get_blob(self, session_id, user_id, camera_id, img_id, variation='ORIGINAL'):
        headers = {'x-application-session-id': session_id}
        ep = '/api/image/%(cid)s/%(iid)s/blob.jpg' % {'cid':camera_id, 'iid': img_id}
        params={'variation':variation}
        res = self.GET(ep, headers, params)
        if(res == None or res['status'] != requests.codes.ok):
            self.LOG('GET-BLOB: FAILED: session_id: %(s)s' % {'s':session_id})
            return None
        assert(res != None and res['status'] == requests.codes.ok)
        content = res['response'].content
        return content
        
