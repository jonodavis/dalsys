class Map(object):
    """ Stores details on a map. """

    def __init__(self, name, filepath):
        self.name = name
        self.filepath = filepath

class MapStore(object):
    """ MapStore stores all the maps for DALSys. """

    def __init__(self, conn=None):
        self._maps = {}
        self._conn = conn
        if conn != None:
            self.fill_from_db()

    def fill_from_db(self):
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM map")
        result = cursor.fetchall()
        for line in result:
            new_map = Map(line[1], line[2])
            self.add(new_map)

    def add(self, map):
        """ Adds a new map to the store. """
        if map.name in self._maps:
            raise Exception('Map already exists in store')
        else:
            self._maps[map.name] = map

    def remove(self, map):
        """ Removes a map from the store. """
        if not map.name in self._maps:
            raise Exception('Map does not exist in store')
        else:
            del self._maps[map.name]

    def get(self, name):
        """ Retrieves a map from the store by its name. """
        if not name in self._maps:
            return None
        else:
            return self._maps[name]

    def list_all(self):
        """ Lists all the maps in the store. """
        for key, value in self._maps.iteritems():
            yield value

    def save(self):
        """ Saves the store to the database. """
        pass    # TODO: we don't have a database yet
