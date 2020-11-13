
from google.cloud import storage
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "dash-test-edd3fb68a133.json"

client = storage.Client(project='dash-test')
bucket = client.get_bucket('ds4a_storage')
blob = bucket.blob('descargable.csv')
blob.upload_from_filename('siniestros_con_hipotesis.csv')