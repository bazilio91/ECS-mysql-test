import esper
from mysql.connector import MySQLConnection

from components import Position, Movement, Persistent, LocationHistory, Item, Container


class MovementProcessor(esper.Processor):
    def __init__(self):
        pass

    def process(self):
        # This will iterate over every Entity that has BOTH of these components:
        for ent, (pos, mov) in self.world.get_components(Position, Movement):
            if pos != mov:
                pos.x = mov.x
                pos.y = mov.y
                pos.location_id = mov.location_id
                pos.changed = True  # mark for save


class LocationHistoryProcessor(esper.Processor):
    def __init__(self):
        pass

    def process(self):
        # This will iterate over every Entity that has BOTH of these components:
        for ent, (pos, history) in self.world.get_components(Position, LocationHistory):
            history.location_id = pos.location_id
            history.changed = True  # time is a SQL statement, so force to update


class InventoryProcessor(esper.Processor):
    def __init__(self):
        pass

    def process(self):
        # This will iterate over every Entity that has BOTH of these components:
        for ent, (item,) in self.world.get_components(Item):
            if not item.container:
                if not item.owner:
                    continue
                item.owner = None
                item.changed = True
                continue

            container_comp = self.world.component_for_entity(item.container, Container)

            if container_comp.owner != item.owner:
                item.owner = container_comp.owner
                item.changed = True


class PersistentProcessor(esper.Processor):
    db: MySQLConnection

    def __init__(self, db):
        self.db = db

    def process(self):
        # This will iterate over every Entity that has BOTH of these components:
        for ent, (_,) in self.world.get_components(Persistent):
            ent_components = self.world.components_for_entity(ent)
            for comp in ent_components:
                # issubclass(type(comp), Persistent) and print(comp, not issubclass(type(comp), Persistent), type(comp) == Persistent, not comp.changed)
                if not issubclass(type(comp), Persistent) or type(comp) == Persistent or not comp.changed:
                    continue

                data_dict = dict(comp.__dict__)
                data_dict.pop('changed')

                keys = ['id']
                values = [ent]
                for k, v in data_dict.items():
                    keys.append(k)
                    values.append(v)

                query_placeholders = ', '.join(['%s'] * len(keys))
                query_columns = ', '.join(keys)
                # very flimsy, but fast :)
                insert_query = '''REPLACE INTO %s (%s) VALUES (%s) ''' % (comp.__class__.__name__, query_columns, query_placeholders)
                # print(insert_query)
                self.db.cursor().execute(insert_query, values)

                comp.changed = False

            self.db.commit()
