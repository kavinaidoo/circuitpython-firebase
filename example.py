from firebase_auth import FirebaseAuth
import ufirestore
import wifi

# --------------- Setup Variables

wifi_ssid                   = 'Your WiFi Name'
wifi_password               = 'Your WiFi Password'
firebase_api_key            = 'Get this from Project Settings > General > Web API Key'
firebase_project_id         = 'Get this from Project Settings > General > Project ID'
firebase_auth_user_email    = 'testUser@testDomain.co.za'
firebase_auth_user_password = 'testPassword'

# --------------- Connecting to WiFi

wifi.radio.connect(wifi_ssid, wifi_password)

# --------------- Getting Access Token from Firebase Auth

auth = FirebaseAuth(firebase_api_key)
auth.sign_in(firebase_auth_user_email, firebase_auth_user_password)
sensor_token = auth.session.access_token

# --------------- Write to Firestore

ufirestore.set_project_id(firebase_project_id)
ufirestore.set_access_token(sensor_token)

# A document "testDocument" with fields testString:"hello world!" and testNumber:123456 will be created in collection "testCollection"

doc = ufirestore.FirebaseJson()
doc.set("testString/stringValue", "hello world!")
doc.set("testNumber/doubleValue", 123456)

response = ufirestore.create("testCollection",doc,document_id="testDocument")

print(response)

# --------------- END OF FILE