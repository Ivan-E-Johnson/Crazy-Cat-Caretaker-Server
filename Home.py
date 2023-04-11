class House(object):
    def __init__(self, mac_address, users=[]):
        self.mac_address = mac_address
        self.users = users

    @staticmethod
    def from_dict(source):
        # ...
        pass

    def to_dict(self):
        # ...
        pass

class Users(object):
    def __init__(self, id, name, cats=[]):
        self.id = id
        self.name = name
        self.cats = cats

    @staticmethod
    def from_dict(source):
        # ...
        pass

    def to_dict(self):
        # ...
        pass

class Cat(object):
    def __init__(self,id, name ,max_food,daily_food):
        self.id = id
        self.name = name
        self.max_food = max_food
        self.daily_food = daily_food

    @staticmethod
    def from_dict(source):
        # ...
        pass

    def to_dict(self):
        # ...
        pass
