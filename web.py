import os
from flask import Flask, redirect, session, send_from_directory, url_for
app = Flask(__name__, static_folder='.')
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

from authlib.integrations.flask_client import OAuth
oauth = OAuth(app)
gyazo_client = oauth.register(
    'gyazo',
    authorize_url='https://api.gyazo.com/oauth/authorize',
    access_token_url='https://api.gyazo.com/oauth/token',
    api_base_url='https://api.gyazo.com/',
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

@app.route('/index_files/gyazodata.js')
def getGyazoData():
    return getGyazoImagesData(
        fetch=True,
        access_token=session['token']['access_token'],
        write_to_file=False,
        page_limit=10)
