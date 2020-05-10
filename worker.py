import os, base64
from celery import Celery
redis_url = os.environ.get('REDIS_URL')
app = Celery('tasks', broker=redis_url, backend=redis_url)

open('/tmp/gcp-key.json', 'w').write(
    base64.b64decode(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_BASE64')).decode('utf-8'))
from google.cloud import storage
from main import getGyazoImagesData

def gyazodataGcsBlob(uid, get=False):
    storage_client = storage.Client()
    bucket = storage_client.bucket('gyazo-zoom-viewer')
    if get:
        return bucket.get_blob("%s.json" % uid)
    return bucket.blob("%s.json" % uid)

@app.task(acks_late=True)
def createGyazodata(uid, access_token):
    blob = gyazodataGcsBlob(uid)
    def progressCallback(page):
        # Update timestamp in progress
        placeholder = 'var data = [];'
        blob.upload_from_string(placeholder)

    gyazodata = getGyazoImagesData(
        fetch=True,
        access_token=access_token,
        write_to_file=False,
        progress_callback=progressCallback)
    blob.upload_from_string(gyazodata)

@app.task
def add(x, y):
    return x + y

