import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
cred = credentials.Certificate('testingccc-3b63d-firebase-adminsdk-vyn5d-3c9e0df96a.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()

home_ref = db.collection('Home')
docs = home_ref.stream()

for col in db.collections():
    print(f'{col.id}')