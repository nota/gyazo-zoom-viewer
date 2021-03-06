import os, tempfile
from datetime import datetime, timedelta
from flask import Flask, redirect, session, send_from_directory, send_file, url_for
app = Flask(__name__, static_folder='.')
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

from authlib.integrations.flask_client import OAuth
oauth = OAuth(app)
api_base_url = os.environ.get('GYAZO_API_BASE_URL') or 'https://api.gyazo.com/'
gyazo_client = oauth.register(
    'gyazo',
    authorize_url=(api_base_url + 'oauth/authorize'),
    access_token_url=(api_base_url + 'oauth/token'),
    api_base_url=api_base_url,
    client_id=os.environ.get("GYAZO_CLIENT_ID"),
    client_secret=os.environ.get("GYAZO_CLIENT_SECRET")
)

from main import getGyazoImagesData

@app.route('/')
def root():
    if not 'token' in session:
        return redirect('/login')
    return app.send_static_file('index.html')

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return oauth.gyazo.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = oauth.gyazo.authorize_access_token()
    session['token'] = token
    return redirect('/')

@app.route('/me')
def me():
    resp = oauth.gyazo.get('api/users/me', token=session['token'])
    return resp.json()

@app.route('/index_files/<path:path>')
def getIndexFiles(path):
    return send_from_directory('index_files', path)

import worker

@app.route('/index_files/gyazodata.js')
def getGyazoData():
    uid = me()['user']['uid']
    blob = worker.gyazodataGcsBlob(uid)
    if blob.exists():
        with tempfile.NamedTemporaryFile() as temp:
            blob.download_to_filename(temp.name)
            return send_file(temp.name)
    else:
        update()
        return ''

@app.route('/update', methods=['POST'])
def update():
    uid = me()['user']['uid']
    blob = worker.gyazodataGcsBlob(uid, get=True)
    # Avoid update in 10 seconds since last progress
    if (blob and blob.updated.replace(tzinfo=None) + timedelta(seconds=10) > datetime.now()):
        return "Please wait until gyazodata is available.", 429

    blob = worker.gyazodataGcsBlob(uid)
    placeholder = 'var data = [];'
    blob.upload_from_string(placeholder)
    worker.createGyazodata.delay(uid, session['token']['access_token'])
    return redirect('/')
