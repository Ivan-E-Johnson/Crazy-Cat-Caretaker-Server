import pyrebase
config = {
    'apiKey': "AIzaSyBx6ut501XQhSePVu7Fi8SbhfYMuOAD344",
    'authDomain': "testingccc-3b63d.firebaseapp.com",
    'databaseURL': "https://testingccc-3b63d-default-rtdb.firebaseio.com",
    'projectId': "testingccc-3b63d",
    'storageBucket': "testingccc-3b63d.appspot.com",
    'messagingSenderId': "1031446491621",
    'appId': "1:1031446491621:web:971d8fff08ce27a547bf0c",
    'measurementId': "G-M1PX452PG9"
}


firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

email = "teat@test.com"
password = "123456"

user = auth.create_user_with_email_and_password(email,password) # want ID token
print(user)
# user = auth.sign_in_with_email_and_password(email,password)
# print(user)

info = auth.get_account_info(user["idToken"])
print(info)