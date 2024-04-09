import adafruit_requests
import ssl
import socketpool
import wifi

radio = wifi.radio
pool = socketpool.SocketPool(radio)
ssl_context = ssl.create_default_context()
requests = adafruit_requests.Session(pool, ssl_context)

class FirestoreException(Exception):
    def __init__(self, message, code=400):
        super().__init__()
        self.message = message
        self.code = code

    def __str__(self):
        return f"{self.code}: {self.message}"


class FIREBASE_GLOBAL_VAR:
    GLOBAL_URL_HOST = "https://firestore.googleapis.com"
    GLOBAL_URL_ADINFO = {
        "host": "https://firestore.googleapis.com", "port": 443}
    PROJECT_ID = None
    DATABASE_ID = "(default)"
    ACCESS_TOKEN = None
    SLIST = {}


def construct_url(resource_path=None):
    path = "%s/v1/projects/%s/databases/%s/documents" % (
        FIREBASE_GLOBAL_VAR.GLOBAL_URL_HOST, FIREBASE_GLOBAL_VAR.PROJECT_ID, FIREBASE_GLOBAL_VAR.DATABASE_ID)

    if resource_path:
        path += "/"+resource_path

    return path


def to_url_params(params=dict()):
    return "?" + "&".join(
        [(str(k) + "=" + str(v)) for k, v in params.items() if v is not None])


def get_resource_name(url):
    return url[url.find("projects"):]


def send_request(path, method="get", data=None, dump=True):
    headers = {}

    if FIREBASE_GLOBAL_VAR.ACCESS_TOKEN:
        headers["Authorization"] = "Bearer " + FIREBASE_GLOBAL_VAR.ACCESS_TOKEN

    response = requests.request(method, path, headers=headers, json=data)

    if dump == True:
        if response.status_code < 200 or response.status_code > 299:
            print(response.text)
            raise FirestoreException(response.reason, response.status_code)

        json = response.json()
        if json.get("error"):
            error = json["error"]
            code = error["code"]
            message = error["message"]
            raise FirestoreException(message, code)
        return json


class INTERNAL:
    def patch(DOCUMENT_PATH, DOC, update_mask=None):
        PATH = construct_url(DOCUMENT_PATH)
        LOCAL_PARAMS = to_url_params()
        if update_mask:
            for field in update_mask:
                LOCAL_PARAMS += "&updateMask.fieldPaths=" + field
        DATA = DOC.process(get_resource_name(PATH))
        LOCAL_OUTPUT = send_request(PATH+LOCAL_PARAMS, "patch", data=DATA)
        return LOCAL_OUTPUT


    def create(COLLECTION_PATH, DOC, document_id=None):
        PATH = construct_url(COLLECTION_PATH)
        PARAMS = {"documentId": document_id}
        LOCAL_PARAMS = to_url_params(PARAMS)
        DATA = DOC.process(get_resource_name(PATH))
        LOCAL_OUTPUT = send_request(PATH+LOCAL_PARAMS, "post", DATA)
        return LOCAL_OUTPUT

    def get(DOCUMENT_PATH):
        PATH = construct_url(DOCUMENT_PATH)
        LOCAL_OUTPUT = send_request(PATH, "get")
        return LOCAL_OUTPUT


def set_project_id(id):
    FIREBASE_GLOBAL_VAR.PROJECT_ID = id


def set_access_token(token):
    FIREBASE_GLOBAL_VAR.ACCESS_TOKEN = token


def set_database_id(id="(default)"):
    FIREBASE_GLOBAL_VAR.DATABASE_ID = id


def patch(PATH, DOC, update_mask=None):
    return INTERNAL.patch(PATH, DOC, update_mask)
    

def create(PATH, DOC, document_id=None):
    return INTERNAL.create(PATH, DOC, document_id)


def get(PATH):
    return INTERNAL.get(PATH)


class FirebaseJson:
    def __init__(self, data={}):
        self.data = data

    def __getitem__(self, key):
        return FirebaseJson(self.data[key])

    @classmethod
    def to_value_type(cls, value):
        if value == None:
            typ = "nullValue"
        elif isinstance(value, bool):
            typ = "booleanValue"
        elif isinstance(value, int):
            typ = "integerValue"
        elif isinstance(value, float):
            typ = "doubleValue"
        elif value.startswith("/t"):
            typ = "timestampValue"
            value = value[2:]
        elif value.startswith("/r"):
            typ = "referenceValue"
            value = value[2:]
        elif value.startswith("/g"):
            typ = "geoPointValue"
            value = value[2:].split(",")
            value = {
                "latitude": value[0],
                "longitude": value[1]
            }
        elif isinstance(value, str):
            typ = "stringValue"
        elif isinstance(value, bytes):
            typ = "bytesValue"
        elif isinstance(value, list):
            typ = "arrayValue"
            return {typ: {"values": [cls.to_value_type(item) for item in value]}}
        elif isinstance(value, dict):
            typ = "mapValue"
            return {typ: {"fields": {k: cls.to_value_type(v) for k, v in value.items()}}}

        return {typ: str(value)}

    @classmethod
    def from_value_type(cls, value):
        typ = [k for k in value.keys()][0]
        if typ == "nullValue":
            return None
        elif typ == "booleanValue":
            return bool(value[typ])
        elif typ == "integerValue":
            return int(value[typ])
        elif typ == "doubleValue":
            return float(value[typ])
        elif typ == "timestampValue":
            return str(value[typ])
        elif typ == "referenceValue":
            return str(value[typ])
        elif typ == "stringValue":
            return str(value[typ])
        elif typ == "bytesValue":
            return bytes(value[typ])
        elif typ == "arrayValue":
            return [cls.from_value_type(item) for item in value[typ]["values"]]
        elif typ == "mapValue":
            return {k: cls.from_value_type(v) for k, v in value[typ]["fields"].items()}

    def cursor(self, path, cb):
        segments = path.split("/")
        cur = self.data
        for i, s in enumerate(segments):
            if i == len(segments) - 1:
                # If final segment is reached
                return cb(cur, s)
            elif s not in cur or not isinstance(cur[s], dict):
                cur[s] = dict()
            cur = cur[s]

    def set(self, path, value, as_type=False):
        def cb(cur, s):
            if as_type:
                cur[s] = self.to_value_type(value)
            else:
                cur[s] = value

        return self.cursor(path, cb)

    def get(self, path, default=None):
        def cb(cur, s):
            if default != None:
                return cur.get(s, default)

            return cur[s]

        return self.cursor(path, cb)

    def add(self, path, name, value):
        def cb(cur, s):
            cur[s].update({name: value})

        return self.cursor(path, cb)

    def add_item(self, path, value):
        def cb(cur, s):
            if s not in cur:
                cur[s] = []
            cur[s].append(value)

        return self.cursor(path, cb)

    def remove(self, path):
        def cb(cur, s):
            del cur[s]

        return self.cursor(path, cb)

    def exists(self, path):
        def cb(cur, s):
            return s in cur

        return self.cursor(path, cb)

    def process(self, name):
        return {
            "fields": self.data
        }

    @classmethod
    def from_raw(cls, raw):
        fields = raw["fields"]
        doc_data = {
            "name": raw["name"],
            "createTime": raw["createTime"],
            "updateTime": raw["updateTime"]
        }
        doc_data.update(fields={k: cls.from_value_type(v)
                        for k, v in fields.items()})
        return FirebaseJson(doc_data)


class Query(FirebaseJson):
    OPERATIONS = {
        "<": "LESS_THAN",
        "<=": "LESS_THAN_OR_EQUAL",
        ">": "GREATER_THAN",
        ">=": "GREATER_THAN_OR_EQUAL",
        "==": "EQUAL",
        "!=": "NOT_EQUAL",
        "array-contains": "ARRAY_CONTAINS",
        "in": "IN",
        "array-contains-any": "ARRAY_CONTAINS_ANY",
        "not-in": "NOT_IN"
    }

    def __init__(self, *args, **kwargs):
        self.num_filters = 0
        super().__init__(*args, **kwargs)

    def from_(self, collection_id, all_descendants=False):
        self.add_item("from", {
            "collectionId": collection_id,
            "allDescendants": all_descendants
        })
        return self

    def select(self, field):
        self.add_item("select/fields", {
            "fieldPath": field
        })
        return self

    def order_by(self, field, direction="DESCENDING"):
        self.add_item("orderBy", {
            "field": {
                "fieldPath": field
            },
            "direction": direction
        })
        return self

    def limit(self, value):
        self.set("limit", value)
        return self

    def where(self, field, op, value):
        if op not in self.OPERATIONS:
            raise Exception("Invalid query operation: %s" % op)

        if self.num_filters == 1:
            cur_filter = self.get("where/fieldFilter")
            self.remove("where/fieldFilter")
            self.set("where/compositeFilter/op", "AND")
            self.add_item("where/compositeFilter/filters", cur_filter)
            self.add_item("where/compositeFilter/filters", {
                "field": {
                    "fieldPath": field
                },
                "op": self.OPERATIONS[op],
                "value": self.to_value_type(value)
            })
        else:
            self.set("where/fieldFilter/field/fieldPath", field)
            self.set("where/fieldFilter/op", self.OPERATIONS[op])
            self.set("where/fieldFilter/value", self.to_value_type(value))

        self.num_filters += 1
        return self

    def process(self):
        return self.data