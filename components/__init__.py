import datetime
import hashlib, uuid


class Persistent(object):
    changed = False

    def __init__(self, changed=False):
        self.changed = changed


class PlayerData(Persistent):
    def __init__(self, name, clan=None, last_login=None, password_hash=None, salt=None, kills=0, changed=False):
        self.name = name
        self.clan = clan
        self.last_login = last_login
        self.password_hash = password_hash
        self.kills = kills
        self.salt = salt

        super(PlayerData, self).__init__(changed=changed)

    def set_password(self, password):
        self.salt = uuid.uuid4().hex
        self.password_hash = hashlib.sha512(str(password + self.salt).encode('utf-8')).hexdigest()
        self.changed = True

    def verify_password(self, password):
        # todo: eliminate time attack on ==
        return hashlib.sha512(str(password + self.salt).encode('utf-8')).hexdigest() == self.password_hash


class Coordinates:
    def __init__(self, x=0.0, y=0.0, location_id=0):
        self.x = x
        self.y = y
        self.location_id = location_id

    def __eq__(self, other):
        """Override the default Equals behavior"""
        return self.x == other.x and self.y == other.y and self.location_id == other.location_id

    def __ne__(self, other):
        """Override the default Unequal behavior"""
        return self.x != other.x or self.y != other.y or self.location_id != other.location_id


class Position(Coordinates, Persistent):
    def __init__(self, x=0.0, y=0.0, location_id=0):
        super(Position, self).__init__(x=x, y=y, location_id=location_id)


class Movement(Coordinates):
    def __init__(self, x=0.0, y=0.0, location_id=0):
        super(Movement, self).__init__(x=x, y=y, location_id=location_id)


class LocationHistory(Persistent):
    date: "NOW()"

    def __init__(self, location_id=0):
        self.location_id = location_id


class Container(Persistent):
    def __init__(self, owner=0, changed=False):
        super(Container, self).__init__(changed=changed)
        self.owner = owner


class Item(Persistent):
    def __init__(self, container=0, owner=0, use_count=0, changed=False):
        super(Item, self).__init__(changed=changed)
        self.container = container
        self.use_count = use_count
        self.owner = owner
        self.changed = changed
