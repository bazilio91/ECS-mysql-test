import datetime
import unittest

import esper
import mysql.connector as mariadb
from mysql.connector import MySQLConnection

from components import Position, Movement, Persistent, LocationHistory, PlayerData, Container, Item
from processors import MovementProcessor, PersistentProcessor, LocationHistoryProcessor, InventoryProcessor


class MyTestCase(unittest.TestCase):
    db: MySQLConnection
    world: esper.World

    def setUp(self):
        self.db = init_db()

        self.world = esper.World()

        self.world.add_processor(MovementProcessor())
        self.world.add_processor(LocationHistoryProcessor())
        self.world.add_processor(InventoryProcessor())
        self.world.add_processor(PersistentProcessor(self.db))

    def tearDown(self):
        self.db.close()
        self.db = None

    def test_something(self):
        world = self.world
        player = world.create_entity()

        world.add_component(player, PlayerData(name="Jon Doe", changed=True))
        world.add_component(player, Position())
        world.add_component(player, Movement())
        world.add_component(player, LocationHistory())
        world.add_component(player, Persistent())

        world.component_for_entity(player, Movement).x = 3
        world.component_for_entity(player, Movement).location_id = 10

        world.process()

        self.assertEqual(3, world.component_for_entity(player, Position).x)
        cursor = self.db.cursor()

        # check player saved
        cursor.execute("SELECT * FROM PlayerData")
        data = cursor.fetchone()
        self.assertEqual(player, data[0])

        # check current position
        cursor.execute("SELECT * FROM Position")
        data = cursor.fetchone()
        self.assertEqual(player, data[0])
        self.assertEqual(3.0, data[1])  # x
        self.assertEqual(0.0, data[2])  # y
        self.assertEqual(10, data[3])  # location_id

        # check for location history for player 1 to visit location 10
        cursor.execute("SELECT * FROM LocationHistory")
        data = cursor.fetchone()
        self.assertEqual(player, data[0])
        self.assertEqual(10, data[1])
        self.assertIsNotNone(data[2])

        # change location and check for history
        world.component_for_entity(player, Movement).location_id = 11
        world.process()
        cursor.execute("SELECT * FROM LocationHistory WHERE location_id = 11")
        data = cursor.fetchone()
        self.assertEqual(player, data[0])
        self.assertEqual(11, data[1])
        self.assertIsNotNone(data[2])

    def test_inventory(self):
        world = self.world
        player = world.create_entity()

        world.add_component(player, PlayerData(name="Jon Doe", changed=True))
        world.add_component(player, Persistent())

        # create container and assign to player
        container = world.create_entity()
        world.add_component(container, Persistent())
        world.add_component(container, Container(owner=player, changed=True))

        # create item and assign to container and player
        item = world.create_entity()
        world.add_component(item, Persistent())
        world.add_component(item, Item(container=container, owner=player, changed=True))

        world.process()

        cursor = self.db.cursor()

        cursor.execute("SELECT * FROM Container")
        data = cursor.fetchone()
        self.assertEqual(container, data[0])
        self.assertEqual(player, data[1])

        cursor.execute("SELECT * FROM Item")
        data = cursor.fetchone()
        self.assertEqual(item, data[0])
        self.assertEqual(container, data[1])
        self.assertEqual(player, data[2])
        self.assertEqual(0, data[3])  # use_count

        # use and drop item on the ground
        item_comp = world.component_for_entity(item, Item)
        item_comp.use_count += 1
        item_comp.container = None
        item_comp.changed = True
        world.process()

        cursor.execute("SELECT * FROM Item")
        data = cursor.fetchone()
        self.assertEqual(item, data[0])
        self.assertEqual(None, data[1], "no container")
        self.assertEqual(None, data[2], "no owner")
        self.assertEqual(1, data[3])  # use_count

        # pickup
        item_comp.container = container
        world.process()

        cursor.execute("SELECT * FROM Item")
        data = cursor.fetchone()
        self.assertEqual(item, data[0])
        self.assertEqual(container, data[1], "new container")
        self.assertEqual(player, data[2], "new owner")
        self.assertEqual(1, data[3])  # use_count

    def test_player_data(self):
        world = self.world
        player = world.create_entity()

        player_comp = PlayerData(name="John Doe", changed=True)
        world.add_component(player, player_comp)
        world.add_component(player, Persistent())

        world.process()

        cursor = self.db.cursor()

        # check created
        cursor.execute("SELECT * FROM PlayerData")
        data = cursor.fetchone()
        self.assertEqual(player, data[0])
        self.assertEqual("John Doe", data[1])

        # check password change & hashing
        player_comp.set_password("qwerty")
        self.assertTrue(player_comp.verify_password("qwerty"))
        world.process()
        cursor.execute("SELECT * FROM PlayerData")
        data = cursor.fetchone()
        self.assertEqual(player_comp.password_hash, data[5])
        self.assertEqual(player_comp.salt, data[6])

        # check kill counter
        player_comp.kills += 1
        player_comp.changed = True
        world.process()

        cursor.execute("SELECT * FROM PlayerData")
        data = cursor.fetchone()
        self.assertEqual(player_comp.kills, data[7])

        dt = datetime.datetime.now()
        player_comp.last_login = dt
        player_comp.changed = True

        world.process()
        cursor.execute("SELECT * FROM PlayerData")
        data = cursor.fetchone()
        self.assertEqual(dt.hour, data[4].hour)


if __name__ == '__main__':
    unittest.main()


def init_db() -> MySQLConnection:
    conn = mariadb.connect(user='root', password='root', database='test')
    cursor = conn.cursor()


    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    for table_name in tables:
        cursor.execute("DROP TABLE %s" % table_name)
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    conn.commit()

    fd = open('../schema.sql', 'r')
    sqlFile = fd.read()
    fd.close()

    # all SQL commands (split on ';')
    sqlCommands = sqlFile.split(';')

    # Execute every command from the input file
    for command in sqlCommands:
        cursor.execute(command)

    return conn
