class Drone(object):
    """ Stores details on a drone. """

    def __init__(self, name, class_type=1, rescue=False):
        self.id = 0
        self.name = name
        self.class_type = class_type
        self.rescue = rescue
        self.operator = None
        self.map = None
        self.location = None


class DroneAction(object):
    """ A pending action on the DroneStore. """

    def __init__(self, drone, operator, commit_action):
        self.drone = drone
        self.operator = operator
        self.messages = []
        self._commit_action = commit_action
        self._committed = False

    def add_message(self, message):
        """ Adds a message to the action. """
        self.messages.append(message)

    def is_valid(self):
        """ Returns True if the action is valid, False otherwise. """
        return len(self.messages) == 0

    def commit(self):
        """ Commits (performs) this action. """
        if self._committed:
            raise Exception("Action has already been committed")

        self._commit_action(self.drone, self.operator)
        self._committed = True
        return self.operator


class DroneStore(object):
    """ DroneStore stores all the drones for DALSys. """

    def __init__(self, conn=None):
        self._drones = {}
        self._last_id = 0
        self._conn = conn
        if conn != None:
            self.fill_from_db()
            
    def fill_from_db(self):
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM drone")
        result = cursor.fetchall()
        for line in result:
            new_drone = Drone(line[1], int(line[2]), int(line[3]))
            if line[4] != None:
                new_drone.operator = line[4]
            if line[5] != None:
                new_drone.map = line[5]
            self.add(new_drone)

    def add(self, drone):
        """ Adds a new drone to the store. """
        if drone.id in self._drones:
            raise Exception('Drone already exists in store')
        else:
            self._last_id += 1
            drone.id = self._last_id
            self._drones[drone.id] = drone
            self.save(drone)

    def remove(self, drone):
        """ Removes a drone from the store. """
        if not drone.id in self._drones:
            raise Exception('Drone does not exist in store')
        else:
            del self._drones[drone.id]
            cursor = self._conn.cursor()
            sql_str = "DELETE FROM drone WHERE drone_id = %d;" % drone.id
            cursor.execute(sql_str)
            self._conn.commit()

    def get(self, id):
        """ Retrieves a drone from the store by its ID. """
        if not id in self._drones:
            return None
        else:
            return self._drones[id]

    def list_all(self):
        """ Lists all the drones in the system. """
        for key, value in self._drones.iteritems():
            yield value

    def allocate(self, drone, operator):
        """ Starts the allocation of a drone to an operator. """
        action = DroneAction(drone, operator, self._allocate)
        # 1. An operator can only operate one drone.
        if operator.drone is not None:
            action.add_message("Operator can only control one drone")

        # 2. The operator must hold the correct license.
        if operator.drone_license != drone.class_type:
            action.add_message("Operator does not have correct drone license")

        # 3. For a rescue drone, the operator must hold a rescue drone endorsement.
        if drone.rescue and not operator.rescue_endorsement:
            action.add_message("Operator does not have rescue endorsement")

        return action

    def _allocate(self, drone, operator):
        """ Performs the actual allocation of the operator to the drone. """
        if operator.drone is not None:
            # If the operator had a drone previously, we need to clean it so it does not
            # hold an incorrect reference
            operator.drone.operator = None
        operator.drone = drone.id
        drone.operator = operator.id
        self.save(drone)

    def save(self, drone):
        """ Saves the drone to the database. """
        cursor = self._conn.cursor()
        sql_str = "SELECT * FROM drone WHERE drone_id = {};".format(drone.id)
        cursor.execute(sql_str)
        if cursor.fetchone() == None:
            # This will run if the drone is not already in the database (adding a new drone)
            sql_str = "INSERT INTO drone () VALUES(%d, \"%s\", %d, %d, NULL, NULL);"% (drone.id, drone.name, drone.class_type, drone.rescue)
            cursor.execute(sql_str)
            self._conn.commit()
        else:
            # This will run if the drone already exists (update drone)
            if drone.operator == None:
                sql_str = "UPDATE drone SET name = \"%s\", class_type = %d, rescue = %d WHERE drone_id = %d;" % (drone.name, drone.class_type, drone.rescue, drone.id)
            else:
                sql_str = "UPDATE drone SET name = \"%s\", class_type = %d, rescue = %d, operator_id = %d WHERE drone_id = %d;" % (drone.name, drone.class_type, drone.rescue, drone.operator, drone.id)
            cursor.execute(sql_str)
            self._conn.commit()

