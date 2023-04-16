import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from Home import *

cat1 = Cat(id="Test_ID", name="KITTY", max_food=1, daily_food=.4)
cat2 = Cat(id="Test_ID2", name="KITTY2", max_food=1, daily_food=.4)
user1 = Users(id = "test_usr", name = "test_usr")
user2 = Users(id = "test_usr", name = "test_usr2")
userList = [user1,user2]
catList = [cat1,cat2]

newHome = House(mac_address="12345",users=userList , cats=catList)
cred = credentials.Certificate('testingccc-3b63d-firebase-adminsdk-vyn5d-3c9e0df96a.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()


home_ref = db.collection('Home')
home_ref
docs = home_ref.stream()
home_ref.add(newHome.to_dict())
db.collection("Home").document("SHOWUP").set(newHome.to_dict())




for col in db.collections():
    print(f'{col.id}')


