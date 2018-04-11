from .common import Faker
import datetime
from tzlocal import get_localzone
from . import log_generator
import numpy
import random


class _Session_obj(object):
    def __init__(self, Id, user):
        self.id = Id
        self.user = user
        self.ip = Faker().ipv4()


class Generator(log_generator.Generator):
    def __init__(self):
        self._time_fmt = '%Y-%m-%dT%H:%M:%S.%fZ'
        self._faker = Faker()
        # start up statements
        self._start = [
            "/usr/sbin/mysqld, Version: 5.7.21-0ubuntu0.16.04.1-log ((Ubuntu)). started with:",
            "Tcp port: 3306  Unix socket: /var/run/mysqld/mysqld.sock",
            "Time                 Id Command    Argument"
        ]

        # users
        self._users = ['root', 'michael', 'elanor', 'chidi', 'tahani', 'jason', 'vicky', 'shawn',
                       'mindy', 'ec2-user']
        self._users_p = [0.3, 0.15, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.2]

        # tables
        self._tables = ['Good', 'Bad', 'Medium', 'Train']
        self._tables_p = [0.1, 0.2, 0.3, 0.4]

        # general query statements
        self._statements = [
            '{time} {id:>5} Query	INSERT INTO {table} VALUES ( {int_value} )',
            '{time} {id:>5} Query	SELECT * FROM {table}',
            '{time} {id:>5} Query	DELETE FROM {table} WHERE {table}ID = {int_value}'
        ]
        self._statements_p = [0.5, 0.3, 0.2]

        # operational statements
        self._op_statements = [
            '{time} {id:>5} Query	SET PASSWORD FOR `{user}`@`{ip}`=<secret>',
            '{time} {id:>5} Query	SET GLOBAL query_cache_size = {int_value}',
            '{time} {id:>5} Query	select @@version_comment limit {int_value}'
        ]
        self._op_statements_p = [0.2, 0.4, 0.4]
        super(Generator, self).__init__("mysql", 0.001)

    def getStartStatement(self, otime=datetime.datetime.now(), local=get_localzone(), state={}):
        outgoing = []
        for stmt in self._start:
            outgoing.append('{0}\n'.format(stmt))
        return outgoing

    def _getTime(self, otime=None, local=get_localzone()):
        if otime is None:
            otime = datetime.datetime.now()
        dt = otime.strftime(self._time_fmt)
        tz = datetime.datetime.now(local).strftime('%z')
        return dt, tz

    def getLogStatement(self, otime=datetime.datetime.now(), local=get_localzone(), state={}):
        statement = ''
        sessions = state.get('active_sessions', [])
        tables = state.get('created_tables', [])
        available_session_ids = state.get('available_session_ids', list(range(0, 10000)))
        # create a session if there aren't any active sessions
        # or if we have users to log in (with some probability)
        if len(sessions) == 0 or (numpy.random.choice([True, False], p=[0.1, 0.9])
                                  and len(available_session_ids) > 0):
            user = numpy.random.choice(self._users, p=self._users_p)
            ident = available_session_ids.pop(0)
            session = _Session_obj(ident, user)
            sessions.append(session)
            statement = '{time} {id:>5} Connect	{user}@{ip} on lamptest using Socket'.format(
                         time=self._getTime(otime, local)[0], id=ident, user=user, ip=session.ip)
        # randomly decide if we should close a session
        elif numpy.random.choice([True, False], p=[0.1, 0.9]):
            session = sessions.pop(0)  # pull out a random session
            available_session_ids.append(session.id*1)
            statement = '{time} {id:>5} Quit	'.format(time=self._getTime(otime, local)[0], id=session.id)
        # use an existing session to make an update
        else:
            session = sessions[random.randint(0, len(sessions)-1)]
            # perform table operation
            # create a table if there aren't any or if we have tables left to create (with some probability)
            if len(tables) == 0 or (numpy.random.choice([True, False], p=[0.1, 0.9])
                                    and (len(tables) < len(self._tables))):
                table = numpy.random.choice(self._tables, p=self._tables_p)
                if table in tables:  # if the table exists, drop it
                    tables.remove(table)
                    statement = '{time} {id:>5} Query	DROP TABLE {table}'.format(
                                 time=self._getTime(otime, local)[0], id=session.id, table=table
                                 )  # return a table drop statement
                else:
                    tables.append(table)
                    statement = '{time} {id:>5} Query	CREATE TABLE {table} ( {table}ID int)'.format(
                                 time=self._getTime(otime, local)[0], id=session.id, table=table
                                 )  # return a table create statement
            # perform operational tasks
            elif numpy.random.choice([True, False], p=[0.2, 0.8]):
                table = tables[random.randint(0, len(tables)-1)]
                statement = numpy.random.choice(self._op_statements, p=self._op_statements_p)
                statement = statement.format(time=self._getTime(otime, local)[0], table=table, id=session.id,
                                             user=session.user, ip=session.ip, int_value=random.randint(0, 100000))
            # perform a general table task
            else:
                table = tables[random.randint(0, len(tables)-1)]
                statement = numpy.random.choice(self._statements, p=self._statements_p)
                statement = statement.format(time=self._getTime(otime, local)[0], table=table, id=session.id,
                                             user=session.user, ip=session.ip, int_value=random.randint(0, 100000))

        state['active_sessions'] = sessions
        state['created_tables'] = tables
        state['available_session_ids'] = available_session_ids
        return ['{0}\n'.format(statement)]
