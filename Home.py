class House(object):
    def __init__(self, mac_address, users=[], cats=[]):
        self.mac_address = mac_address
        self.users = users
        self.cats = cats

        @staticmethod
        def from_dict(source):
            mac_address = source['mac_address']
            users = [Users.from_dict(user_dict) for user_dict in source.get('users', [])]
            cats = [Cat.from_dict(cat_dict) for cat_dict in source.get('cats', [])]
            return House(mac_address, users, cats)

        def to_dict(self):
            return {
                'mac_address': self.mac_address,
                'users': [user.to_dict() for user in self.users],
                'cats': [cat.to_dict() for cat in self.cats],
            }

class Users(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    @staticmethod
    def from_dict(source):
        id = source['id']
        name = source['name']
        return Users(id, name)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class Cat(object):
    def __init__(self, id, name, max_food, daily_food):
        self.id = id
        self.name = name
        self.max_food = max_food
        self.daily_food = daily_food

    @staticmethod
    def from_dict(source):
        id = source['id']
        name = source['name']
        max_food = source['max_food']
        daily_food = source['daily_food']
        return Cat(id, name, max_food, daily_food)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'max_food': self.max_food,
            'daily_food': self.daily_food,
        }

