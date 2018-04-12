from faker import Faker
import numpy
import random

faker = Faker()

log_types = ['apache', 'apache_error', 'mysql_general', 'mysql_error', 'mysql_slow']


# users
users = ['root', 'michael', 'elanor', 'chidi', 'tahani', 'jason', 'vicky', 'shawn',
         'mindy', 'ec2-user']
users_p = [0.3, 0.15, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.2]

# tables
tables = ['Good', 'Bad', 'Medium', 'Train']
tables_p = [0.1, 0.2, 0.3, 0.4]


# databases
databases = ['hello', 'world', 'foo', 'bar']
databases_p = [0.4, 0.3, 0.2, 0.1]

# general mysql query statements
mysql_query_statements = [
    '{time} {id:>5} Query	INSERT INTO {table} VALUES ( {int_value} )',
    '{time} {id:>5} Query	SELECT * FROM {table}',
    '{time} {id:>5} Query	DELETE FROM {table} WHERE {table}ID = {int_value}'
]
mysql_query_statements_p = [0.5, 0.3, 0.2]

# operational mysql statements
mysql_op_statements = [
    '{time} {id:>5} Query	SET PASSWORD FOR `{user}`@`{ip}`=<secret>',
    '{time} {id:>5} Query	SET GLOBAL query_cache_size = {int_value}',
    '{time} {id:>5} Query	select @@version_comment limit {int_value}'
]
mysql_op_statements_p = [0.2, 0.4, 0.4]


class ObjMgr(object):
    class Operation():
        CREATE = 0
        UPDATE = 1
        DELETE = 2

    def __init__(self, objs=[], objs_p=[]):
        self._objs = objs
        self._objs_p = objs_p
        self._created_objs = []

    def get(self):
        obj = None
        operation = None
        # create a obj if there aren't any or if we have objs left to create (with some probability)
        if len(self._created_objs) == 0 or (numpy.random.choice([True, False], p=[0.1, 0.9])
                                            and (len(self._created_objs) < len(self._objs))):
            obj = numpy.random.choice(self._objs, p=self._objs_p)
            if obj in self._created_objs:
                # if the obj exists, delete it
                self._created_objs.remove(obj)
                operation = ObjMgr.Operation.DELETE
            else:
                # create the obj because it doesn't exist
                self._created_objs.append(obj)
                operation = ObjMgr.Operation.CREATE
        # perform operational tasks
        else:
            obj = self._created_objs[random.randint(0, len(self._created_objs)-1)]
            operation = ObjMgr.Operation.UPDATE
        return obj, operation


class Session(object):
    def __init__(self, Id, user):
        self.Id = Id
        self.user = user
        self.ip = faker.ipv4()


class SessionMgr(object):
    """
    manages open sessions
    """
    class Operation():
        OPEN = 0
        UPDATE = 1
        CLOSE = 2

    def __init__(self, max_sessions=10000, users=[], users_p=[], new_session_p=0.1, remove_session_p=0.1):
        self._users = users
        self._users_p = users_p
        self.Ids = list(range(0, max_sessions))
        self._new_session_p = new_session_p
        self._remove_session_p = remove_session_p
        self.sessions = []

    def get_session(self):
        session = None
        operation = None
        # create a session if there aren't any active sessions
        # or if we have users to log in (with some probability)
        if len(self.sessions) == 0 or (numpy.random.choice([True, False],
                                                           p=[self._new_session_p, 1-self._new_session_p])
                                       and len(self.Ids) > 0):
            user = numpy.random.choice(self._users, p=self._users_p)
            Id = self.Ids.pop(0)
            session = Session(Id, user)
            operation = SessionMgr.Operation.OPEN
            self.sessions.append(session)
        # randomly decide if we should close a session
        elif numpy.random.choice([True, False], p=[self._remove_session_p, 1-self._remove_session_p]):
            session = self.sessions.pop(0)  # pull out a random session
            operation = SessionMgr.Operation.CLOSE
            self.Ids.append(session.Id*1)
        # use an existing session to make an update
        else:
            session = self.sessions[random.randint(0, len(self.sessions)-1)]
            operation = SessionMgr.Operation.UPDATE

        return session, operation


class switch(object):
    """
    helper class to simiulate switch statement
    """
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args:  # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False
