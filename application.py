#!/usr/bin/env python

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, make_response
from gaze import gaze

# SECTION: CONFIGURATION
GAZE_URL='http://gazeapi.elasticbeanstalk.com'
SECRET_KEY='ewqtimbdsihe'

# SECTION: THE APP
application = Flask(__name__)
app = application
app.config.from_object(__name__)

# SECTION: APP FUNCTIONS
@app.route('/')
def home():
    return render_template('index.html', menu=build_menu('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if(request.method == 'POST'):
        if(request.form['username'] == None or request.form['password'] == None):
            error = 'Invalid username or password!'            
        else:
            username = request.form['username']
            password = request.form['password']
            s = g.gaze_instance.login(username, password)
            if(s == None):
                return render_template('login.html', menu=build_menu('console'), error=error)
            else:
                session['gaze-session'] = s
                print session
                return redirect(url_for('console'))
    return render_template('login.html', menu=build_menu('console'), error=error)

@app.route('/logout', methods=['GET','POST'])
def logout():
    if(session.has_key('gaze-session') == False):
        return redirect(url_for('login'))
    else:
        session_id = session['gaze-session']['sessionId']
        if(request.method == 'POST'):
            del session['gaze-session']
            g.gaze_instance.logout(session_id)
            return redirect(url_for('home'))
    return render_template('logout.html', menu=build_menu('console'))

@app.route('/admin')
def console():
    if(session.has_key('gaze-session') == False or session['gaze-session'] == None):
        return redirect(url_for('login'))
    else:
        session_id = session['gaze-session']['sessionId']
        user_id = session['gaze-session']['userId']
    return render_template('console.html', menu=build_menu('console'), user=user_id)

@app.route('/about')
def about():
    session_id = session['gaze-session']['sessionId']
    user_id = session['gaze-session']['userId']
    return render_template('console.html', menu=build_menu('about'), user=user_id)

@app.route('/list-camera')
def list_cameras():
    start = request.args.get('start', None)
    limit = request.args.get('limit',10)
    session_id = session['gaze-session']['sessionId']
    user_id = session['gaze-session']['userId']
    if(start == 'None'):
        start = None
    cl = g.gaze_instance.list_cameras(session_id, user_id, start=start)
    prev = None
    if(start != None):
        prev = start
    next = None
    if(len(cl) > 0):
        next = cl[-1]['cameraId']
    return render_template('list-cameras.html', menu=build_menu('console'), cameras=cl, prev=prev, next=next)

@app.route('/view-image/<camera_id>')
def view_camera(camera_id):
    if(session.has_key('gaze-session') == False or session['gaze-session'] == None):
        return redirect(url_for('login'))
    else:
        session_id = session['gaze-session']['sessionId']
        user_id = session['gaze-session']['userId']
        cam = g.gaze_instance.get_camera(session_id, camera_id)
        print 'Camera', cam
        img_url = url_for('view_image', camera_id=camera_id, ts=cam['lastImageTimestamp'])
        return render_template('view-image.html', menu=build_menu('console'), camera=cam, img_url=img_url)

@app.route('/view-image/<camera_id>/<ts>.jpg')
def view_image(camera_id, ts):
    if(session.has_key('gaze-session') == False or session['gaze-session'] == None):
        return redirect(url_for('login'))
    else:
        session_id = session['gaze-session']['sessionId']
        user_id = session['gaze-session']['userId']
        blb = g.gaze_instance.get_blob(session_id, user_id, camera_id, ts)
        if(blb == None or len(blb) == 0):
            abort(404)
        response = make_response(blb)
        response.headers['Content-Type'] = 'image/jpeg'
        return response
        
    

# SECTION: DECORATORS
@app.before_request
def before_request():
    gaze_instance = getattr(g, 'gaze', None)
    if(gaze_instance == None):
        gaze_instance = gaze(GAZE_URL)
        g.gaze_instance = gaze_instance

@app.teardown_request
def teardown_request(exception):
    g.blah = False

def build_menu(active=None):
    menu = dict()
    menu['home'] = {'name':'Home', 'url': url_for('home'), 'active': False}
    menu['console'] = {'name':'Console', 'url': url_for('console'), 'active': False}
    menu['about'] = {'name':'About', 'url': url_for('about'), 'active': False}
    menu['contact'] = {'name':'Contact', 'url': url_for('about'), 'active': False}
    if(active != None and menu.has_key(active)):
        menu[active]['active'] = True
    print menu
    return menu

# SECTION: MAIN
if(__name__ == "__main__"):
    app.run(debug=True, host='0.0.0.0')

