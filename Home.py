from firebase_admin import firestore, credentials, initialize_app

cred = credentials.Certificate(
    "secret/testingccc-3b63d-firebase-adminsdk-vyn5d-39fa47faad.json"
)

app = initialize_app(cred)
db = firestore.client()

home_ref = db.collection("Home")

class DatabaseObject():
    ref = db
    attrs = []
    pk = None

    def __str__(self):
        return f"{self.__class__.__name__[:-1]}:\n\t" + \
               "\n\t".join([f"{key}:\n {' '.join([str(v) for v in value])}" if type(value) == list else f"{key}: {value}" for key, value in self.__dict__.items()]) + "\n"

    def primary_key(self):
        return self.__dict__[self.__class__.pk]

    def create(self):
        self.__class__.ref.document(self.primary_key()).set(self.to_dict())

    def _transform_attrs(self, name, attr_class, attr_list_of_dicts):
        new_attrs = []
        for attr in attr_list_of_dicts:
            new_attrs.append(attr_class.from_dict(attr))
        self.__dict__[name] = new_attrs

    def _transform_attr(self, name, attr_class, attr_dict):
        self.__dict__[name] = attr_class.from_dict(attr_dict)

    @classmethod
    def get(cls, primary_key):
        data = cls.ref.document(primary_key).get()
        return None if data is None else cls.from_dict(data.to_dict())

    @staticmethod
    def _from_dict(cls, source):
        if source is None:
            return None
        args = []
        for arg in cls.attrs:
            args.append(source[arg])
        return cls(*args)

    @classmethod
    def from_dict(cls, source):
        return None if source is None else cls._from_dict(cls, source)

    def to_dict(self):
        dict = {}
        for key, val in self.__dict__.items():
            if type(val) == list:
                val = [i.to_dict() for i in val]
                dict[key] = val
            elif issubclass(type(val), DatabaseObject):
                dict[key] = val.to_dict()
            else:
                dict[key] = val
        return dict


class Users(DatabaseObject):
    ref = db.collection("Users")
    pk = "email"
    attrs = ["email", "mac_address"]

    def __init__(self, email, mac_address):
        self.email = email
        self.mac_address = mac_address


class House(DatabaseObject):
    ref = db.collection("Home")
    pk = "mac_address"
    attrs = ["mac_address", "cats", "events"]

    def __init__(self, mac_address, cats, events):
        self.mac_address = mac_address
        self.cats = cats
        self.events = events

    @classmethod
    def from_dict(cls, source):
        new_class = super()._from_dict(cls, source)
        if new_class is None:
            return None
        new_class._transform_attrs("cats", Cats, new_class.cats)
        new_class._transform_attr("events", HomeEvents, new_class.events)
        return new_class

    def add_cat(self, cat):
        self.cats.append(cat)


class Cats(DatabaseObject):
    ref = None # Cats should be added to a house not to the db directly
    pk = None # Cats should be added to a house not to the db directly
    attrs = ["name", "max_food", "daily_food"]

    def __init__(self, name, max_food, daily_food):
        self.name = name
        self.max_food = max_food
        self.daily_food = daily_food


class HomeEvents(DatabaseObject):
    ref = None  # Events should be added to a house not to the db directly
    pk = None  # Events should be added to a house not to the db directly
    attrs = ["laser_state", "dispense", "video"]

    def __init__(self, laser_state, dispense, video):
        self.laser_state = laser_state
        self.dispense = dispense
        self.video = video


