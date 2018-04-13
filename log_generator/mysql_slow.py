from . import common
import datetime
from tzlocal import get_localzone
from . import log_generator
import numpy
import random
import calendar


class Generator(log_generator.Generator):
    def __init__(self, users=common.users, users_p=common.users_p,
                 tables=common.tables, tables_p=common.tables_p,
                 query_statements=common.mysql_query_statements,
                 query_statements_p=common.mysql_query_statements_p,
                 op_statements=common.mysql_op_statements,
                 op_statements_p=common.mysql_op_statements_p,
                 databases=common.databases,
                 databases_p=common.databases_p):
        self._databases = databases
        self._databases_p = databases_p
        self._op_statements = op_statements
        self._op_statements_p = op_statements_p
        self._query_statements = query_statements
        self._query_statements_p = query_statements_p
        self._tables = tables
        self._tables_p = tables_p
        self._users = users
        self._users_p = users_p

        self._time_fmt = '%Y-%m-%dT%H:%M:%S.%fZ'
        self._faker = common.faker
        # start up statements
        self._start = [
            '/usr/sbin/mysqld, Version: 5.7.21-0ubuntu0.16.04.1-log ((Ubuntu)). started with:',
            'Tcp port: 3306  Unix socket: /var/run/mysqld/mysqld.sock',
            'Time                 Id Command    Argument'
        ]

        self._preamble = (
            '# Time: {time}\n'
            '# User@Host: {user}[{db}] @ {ip} []  Id: {id:>5}\n'
            '# Query_time: {q_time:>1.6f} Lock_time: {l_time:>1.6f} Rows_sent: {rows_sent:>2}  Rows_examined: '
            '{rows_exam:>2}\n'
            'use {db};\n'
            'SET timestamp={ts};')
        super(Generator, self).__init__("mysql_slow", 0.001)

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
        statements = []
        sessions = state.get('session_mgr', common.SessionMgr(10000, self._users, self._users_p))
        tables = state.get('table_mgr', common.ObjMgr(self._tables, self._tables_p))
        databases = state.get('db_mgr', common.ObjMgr(self._databases, self._databases_p))
        database, _ = databases.get()
        session, _ = sessions.get_session()
        statements.append(self._preamble.format(time=self._getTime(otime, local)[0], user=session.user, db=database,
                                                ip=session.ip, id=session.Id, rows_sent=random.randint(0, 99),
                                                rows_exam=random.randint(0, 99), q_time=random.uniform(0.0, 9.9999),
                                                l_time=random.uniform(0.0, 9.9999),
                                                ts=calendar.timegm(otime.utctimetuple())))
        for i in range(0, random.randint(0, 3)):
            table, operation = tables.get()
            # create the table
            if operation == common.ObjMgr.Operation.CREATE:
                statements.append('{time} {id:>5} Query	CREATE TABLE {table} ( {table}ID int)'.format(
                                time=self._getTime(otime, local)[0], id=session.Id, table=table))
            # delete the table
            elif operation == common.ObjMgr.Operation.DELETE:
                statements.append('{time} {id:>5} Query	DROP TABLE {table}'.format(
                                time=self._getTime(otime, local)[0], id=session.Id, table=table))
            # operate within the table
            else:
                # perform an operation task
                if numpy.random.choice([True, False], p=[0.2, 0.8]):
                    statement = numpy.random.choice(self._op_statements, p=self._op_statements_p)
                    statements.append(statement.format(time=self._getTime(otime, local)[0], table=table,
                                                       id=session.Id, user=session.user, ip=session.ip,
                                                       int_value=random.randint(0, 100000)))
                # perform a general table task
                else:
                    statement = numpy.random.choice(self._query_statements, p=self._query_statements_p)
                    statements.append(statement.format(time=self._getTime(otime, local)[0], table=table,
                                                       id=session.Id, user=session.user, ip=session.ip,
                                                       int_value=random.randint(0, 100000)))

        state['session_mgr'] = sessions
        state['table_mgr'] = tables
        state['db_mgr'] = databases
        for index, statement in enumerate(statements):
            statements[index] = '{0}\n'.format(statement)
        return statements
