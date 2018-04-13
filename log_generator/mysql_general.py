from . import common
import datetime
from tzlocal import get_localzone
from . import log_generator
import numpy
import random


class Generator(log_generator.Generator):
    def __init__(self, users=common.users, users_p=common.users_p,
                 tables=common.tables, tables_p=common.tables_p,
                 query_statements=common.mysql_query_statements,
                 query_statements_p=common.mysql_query_statements_p,
                 op_statements=common.mysql_op_statements,
                 op_statements_p=common.mysql_op_statements_p):
        self._users = users
        self._users_p = users_p
        self._tables = tables
        self._tables_p = tables_p
        self._query_statements = query_statements
        self._query_statements_p = query_statements_p
        self._op_statements = op_statements
        self._op_statements_p = op_statements_p

        self._time_fmt = '%Y-%m-%dT%H:%M:%S.%fZ'

        # start up statements
        self._start = [
            "/usr/sbin/mysqld, Version: 5.7.21-0ubuntu0.16.04.1-log ((Ubuntu)). started with:",
            "Tcp port: 3306  Unix socket: /var/run/mysqld/mysqld.sock",
            "Time                 Id Command    Argument"
        ]
        super(Generator, self).__init__("mysql_general", 0.001)

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
        sessions = state.get('session_mgr', common.SessionMgr(10000, self._users, self._users_p))
        tables = state.get('table_mgr', common.ObjMgr(self._tables, self._tables_p))
        session, operation = sessions.get_session()
        # create the session
        if operation == common.SessionMgr.Operation.OPEN:
            statement = '{time} {id:>5} Connect	{user}@{ip} on lamptest using Socket'.format(
                         time=self._getTime(otime, local)[0], id=session.Id, user=session.user, ip=session.ip)
        # close the session
        elif operation == common.SessionMgr.Operation.CLOSE:
            statement = '{time} {id:>5} Quit	'.format(time=self._getTime(otime, local)[0], id=session.Id)
        # operate within the session
        else:
            table, operation = tables.get()
            # create the table
            if operation == common.ObjMgr.Operation.CREATE:
                statement = '{time} {id:>5} Query	CREATE TABLE {table} ( {table}ID int)'.format(
                            time=self._getTime(otime, local)[0], id=session.Id, table=table
                            )  # return a table create statement
            # delete the table
            elif operation == common.ObjMgr.Operation.DELETE:
                statement = '{time} {id:>5} Query	DROP TABLE {table}'.format(
                            time=self._getTime(otime, local)[0], id=session.Id, table=table
                            )  # return a table drop statement
            # operate within the table
            else:
                # perform an operation task
                if numpy.random.choice([True, False], p=[0.2, 0.8]):
                    statement = numpy.random.choice(self._op_statements, p=self._op_statements_p)
                    statement = statement.format(time=self._getTime(otime, local)[0], table=table, id=session.Id,
                                                 user=session.user, ip=session.ip, int_value=random.randint(0, 100000))
                # perform a general table task
                else:
                    statement = numpy.random.choice(self._query_statements, p=self._query_statements_p)
                    statement = statement.format(time=self._getTime(otime, local)[0], table=table, id=session.Id,
                                                 user=session.user, ip=session.ip, int_value=random.randint(0, 100000))

        state['session_mgr'] = sessions
        state['table_mgr'] = tables
        return ['{0}\n'.format(statement)]
