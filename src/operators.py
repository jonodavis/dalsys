from datetime import date

class Operator(object):
    """ Stores details on an operator. """

    def __init__(self):
        self.id = -1
        self.first_name = None
        self.family_name = None
        self.date_of_birth = None
        self.drone_license = None
        self.rescue_endorsement = False
        self.operations = 0
        self.drone = None


class OperatorAction(object):
    """ A pending action on the OperatorStore. """

    def __init__(self, operator, commit_action):
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

        self._commit_action(self.operator)
        self._committed = True


class OperatorStore(object):
    """ Stores the operators. """

    def __init__(self, conn=None):
        self._operators = {}
        self._last_id = 0
        self._conn = conn
        if conn != None:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM operator")
            result = cursor.fetchall()
            for line in result:
                self._last_id += 1
                new_op = Operator()
                new_op.id = int(line[0])
                new_op.first_name = line[1]
                new_op.family_name = line[2]
                new_op.date_of_birth = line[3]
                new_op.drone_license = int(line[4])
                new_op.rescue_endorsement = int(line[5])
                new_op.operations = int(line[6])
                new_op.drone = line[7]
                self._operators[new_op.id] = new_op

    def add(self, operator):
        """ Starts adding a new operator to the store. """
        action = OperatorAction(operator, self._add)
        check_age = True
        if operator.first_name is None:
            action.add_message("First name is required")
        if operator.date_of_birth is None:
            action.add_message("Date of birth is required")
            check_age = False
        if operator.rescue_endorsement and operator.operations < 5:
            action.add_message("5 operations are required to hold a rescue endorsement")
        if operator.drone_license is None:
            action.add_message("Drone license is required")
        else:
            if check_age and operator.drone_license == 2:
                today = date.today()
                age = today.year - operator.date_of_birth.year - \
                    ((today.month, today.day) < (
                        operator.date_of_birth.month, operator.date_of_birth.day))
                if age < 20:
                    action.add_message(
                        "Operator should be at least twenty to hold a class 2 license")
        return action

    def _add(self, operator):
        """ Adds a new operator to the store. """
        if operator.id in self._operators:
            raise Exception('Operator already exists in store')
        else:
            self._last_id += 1
            operator.id = self._last_id
            self._operators[operator.id] = operator
            self.save(operator)

    def remove(self, operator):
        """ Removes a operator from the store. """
        if not operator.id in self._operators:
            raise Exception('Operator does not exist in store')
        else:
            del self._operators[operator.id]

    def get(self, id):
        """ Retrieves a operator from the store by its ID or name. """
        if isinstance(id, basestring):
            for op in self._operators.values():
                if (op.first_name + ' ' + op.family_name) == id:
                    return op
            return None
        else:
            if not id in self._operators:
                return None
            else:
                return self._operators[id]

    def list_all(self):
        """ Lists all the _operators in the system. """
        for key, value in self._operators.iteritems():
            yield value

    def save(self, operator):
        """ Saves the store to the database. """
        cursor = self._conn.cursor()
        sql_str = "SELECT * FROM operator WHERE operator_id = %d;" % operator.id
        cursor.execute(sql_str)
        if cursor.fetchone() == None:
            # This will run if the operator is not already in the database (adding a new operator)
            sql_str = "INSERT INTO operator () VALUES(%d, \"%s\", \"%s\", NULL, 0, 0, 0, NULL);"% (operator.id, operator.first_name, operator.family_name)
            cursor.execute(sql_str)
            self._conn.commit()
        else:
            if operator.drone == None:
                sql_str = "UPDATE operator SET first_name = \"%s\", family_name = \"%s\", drone_license = %d, rescue_endorsement = %d, operations = %d WHERE operator_id = %d;" % (operator.first_name, operator.family_name, operator.drone_license, operator.rescue_endorsement, operator.operations, operator.id)
            else:
                sql_str = "UPDATE operator SET first_name = \"%s\", family_name = \"%s\", drone_license = %d, rescue_endorsement = %d, operations = %d, drone_id = %d WHERE operator_id = %d;" % (operator.first_name, operator.family_name, operator.drone_license, operator.rescue_endorsement, operator.operations, operator.drone, operator.id)
            cursor.execute(sql_str)
            self._conn.commit()
