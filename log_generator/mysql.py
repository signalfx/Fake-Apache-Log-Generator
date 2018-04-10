from common import Faker
import datetime
from tzlocal import get_localzone
from .log_generator import BaseGenerator
import numpy
import random


class _Session_obj(object):
    def __init__(self, Id, Name):
        self.Id
        self.Name
        self.Ip = Faker.ipv4()


class Generator(BaseGenerator):
    def __init__(self):
        self._time_fmt = '%Y-%m-%dT%H:%M:%S.%fZ'
        self._faker = Faker()
        self._users = ['root', 'batman', 'wonderwoman', 'aquaman', 'greenlantern', 'cyborg', 'flash', 'greenarrow',
                       'hawkgirl', 'ec2-user']
        self._users_p = [0.3, 0.15, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.2]
        self._tables = ['JusticeLeage', 'Ocean', 'InvisibleJet', 'BatCave']
        self._tables_p = [0.1, 0.2, 0.3, 0.4]
        self._start = [
            "/usr/sbin/mysqld, Version: 5.7.21-0ubuntu0.16.04.1-log ((Ubuntu)). started with:",
            "Tcp port: 3306  Unix socket: /var/run/mysqld/mysqld.sock",
            "Time                 Id Command    Argument"
        ]
        # self._transactions = [
        #     '{time}	    {id} Connect	{user}@{ip} on lamptest using Socket',
        #     '{time}	    {id} Query	select @@version_comment limit 1',
        #     '{time}	    {id} Query	CREATE TABLE {table} ( {table}ID int)',
        #     '{time}	    {id} Query	INSERT INTO {table} VALUES ( 1 )'
        #     '{time}	    {id} Query	INSERT INTO {table} VALUES ( 2 )'
        #     '{time}	    {id} Quit	'
        # ]
        super(Generator, self).__init__("apache")

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

    def _getTransaction(self, state={}):
        ip = self._faker.ipv4()
        user = numpy.random.choice(self._users, p=self._users_p)
        table = numpy.random.choice(self._tables, p=self._tables_p)
        state['Id'] = state['Id'] + 1 if 'Id' in state else 1
        Id = state['Id']
        lines = ['{time}	    {id} Connect	{user}@{ip} on lamptest using Socket']
        lines.append('{time}	    {id} Query	CREATE TABLE {table} ( {table}ID int)')
        lines.append('{time}	    {id} Query	INSERT INTO {table} VALUES ( 1 )')
        lines.append('{time}	    {id} Query	INSERT INTO {table} VALUES ( 2 )')
        lines.append('{time}	    {id} Quit	')
        for i, l in enumerate(lines):
            lines[i] = '{0}\n'.format(l.format(ip=ip, user=user, table=table, time=self._getTime()[0], id=Id))
        return lines

    def getLogStatement(self, otime=datetime.datetime.now(), local=get_localzone(), state={}):
        sessions = state.get('active_sessions', [])
        tables = state.get('created_tables', {})
        # create a session if there aren't any active sessions or if we have users to log in with some probability
        if len(sessions) == 0 or (numpy.random.choice([True, False], p=[0.1, 0.9])
                                  and len(sessions) < len(self._users)):
            user = numpy.random.choice(self._users, p=self._users_p)
            state['Id'] = state['Id'] + 1 if 'Id' in state else 1
            ident = state['Id']
            session = _Session_obj(ident, user)
            sessions.push(session)
            return ['{time}	    {id} Connect	{user}@{ip} on lamptest using Socket\n'.format(
                        time=otime, id=ident, user=user, ip=session.Ip)]
        # randomly decide if we should close a session
        elif numpy.random.choice([True, False], p=[0.1, 0.9]):
            sessions.pop(random.randint(0, len(sessions)-1))  # pull out a random session
            return ['{time}	    {id} Quit	\n'.format(time=otime, id=ident)]
        # use an existing session to make an update
        else:
            session = sessions[random.randint(0, len(sessions)-1)]
            # create a table if there aren't any or if we have tables left to create with some probability
            if len(tables) == 0 or (numpy.random.choice([True, False], p=[0.1, 0.9])
                                    and (len(tables) < len(self._tables))):
                table = numpy.random.choice(self._tables, p=self._tables_p)
                tables[table] = None
            # randomly decide if we should drop a table
            elif numpy.random.choice([True, False], p=[0.1, 0.9]):  # randomly decide to delete a table
                pass
            else:  # perform an operation on the table SET, CREATE, INSERT, DELETE
                pass

        state['active_sessions'] = sessions
        state['created_tables'] = tables
        return self._getTransaction()
        # """
        # generates an apache log_statement
        # """
        # ip = self._faker.ipv4()
        # time_fmt = '%Y-%m-%dT%H:%M:%S.%fZ'  # 2018-03-27T13:50:20.397608Z
        # dt = otime.strftime(time_fmt)
        # tz = datetime.datetime.now(local).strftime('%z')
        # vrb = numpy.random.choice(self._verb, p=self._verb_p)

        # uri = random.choice(self._resources)
        # if uri.find("apps") > 0:
        #     uri += str(random.randint(1000, 10000))

        # resp = numpy.random.choice(self._response, p=self._response_p)
        # byt = int(random.gauss(5000, 50))
        # referer = self._faker.uri()
        # useragent = numpy.random.choice(self._ualist, p=self._ualist_p)()
        # return ['%s - - [%s %s] "%s %s HTTP/1.0" %s %s "%s" "%s"\n' %
        #         (ip, dt, tz, vrb, uri, resp, byt, referer, useragent)]
