#!/usr/bin/python
import time
import datetime
import numpy
import random
import gzip
import sys
from faker import Faker
from tzlocal import get_localzone

# TODO: allow writing different patterns (Common Log, Apache Error log etc) log rotation

# default argument values
_log_lines = 1
_file_prefix = None
_output_type = 'CONSOLE'
_log_type = 'apache'
_sleep_time = 0.0

# static content and their corresponding probabilities
_response = ["200", "404", "500", "301"]
_response_p = [0.9, 0.04, 0.02, 0.04]

_verb = ["GET", "POST", "DELETE", "PUT"]
_verb_p = [0.6, 0.1, 0.1, 0.2]

_faker = Faker()
_ualist = [_faker.firefox, _faker.chrome, _faker.safari, _faker.internet_explorer, _faker.opera]
_ualist_p = [0.5, 0.3, 0.1, 0.05, 0.05]

# log levels for apache 2.4+
_log_level = ["emerg", "alert", "crit", "error", "warn", "notice", "info", "debug", "trace1", "trace2", "trace3",
              "trace4", "trace5", "trace6", "trace7", "trace8"]
_log_level_p = [0.05, 0.05, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.0375, 0.0375, 0.0375, 0.0375, 0.0375, 0.0375, 0.0375,
                0.0375]

_resources = ["/list", "/wp-content", "/wp-admin", "/explore", "/search/tag/list", "/app/main/posts",
              "/posts/posts/explore", "/apps/cart.jsp?appID="]

# mysql error log messages 
_mysql_error_log_startup = [
    "mysqld_safe Logging to '/var/log/mysql/error.log'.",
    "mysqld_safe Starting mysqld daemon with databases from /var/lib/mysql",
    "0 [Warning] TIMESTAMP with implicit DEFAULT value is deprecated. Please use --explicit_defaults_for_timestamp server option (see documentation for more details).",
    "0 [Note] /usr/sbin/mysqld (mysqld 5.7.21-0ubuntu0.16.04.1-log) starting as process 600 ...",
    "0 [Note] InnoDB: PUNCH HOLE support available",
    "0 [Note] InnoDB: Mutexes and rw_locks use GCC atomic builtins",
    "0 [Note] InnoDB: Uses event mutexes",
    "0 [Note] InnoDB: GCC builtin __atomic_thread_fence() is used for memory barrier",
    "0 [Note] InnoDB: Compressed tables use zlib 1.2.8",
    "0 [Note] InnoDB: Using Linux native AIO",
    "0 [Note] InnoDB: Number of pools: 1",
    "0 [Note] InnoDB: Using CPU crc32 instructions",
    "0 [Note] InnoDB: Initializing buffer pool, total size = 128M, instances = 1, chunk size = 128M",
    "0 [Note] InnoDB: Completed initialization of buffer pool",
    "0 [Note] InnoDB: If the mysqld execution user is authorized, page cleaner thread priority can be changed. See the man page of setpriority().",
    "0 [Note] InnoDB: Highest supported file format is Barracuda.",
    "0 [Note] InnoDB: Creating shared tablespace for temporary tables",
    "0 [Note] InnoDB: Setting file './ibtmp1' size to 12 MB. Physically writing the file full; Please wait ...",
    "0 [Note] InnoDB: File './ibtmp1' size is now 12 MB.",
    "0 [Note] InnoDB: 96 redo rollback segment(s) found. 96 redo rollback segment(s) are active.",
    "0 [Note] InnoDB: 32 non-redo rollback segment(s) are active.",
    "0 [Note] InnoDB: 5.7.21 started; log sequence number 2551607",
    "0 [Note] InnoDB: Loading buffer pool(s) from /var/lib/mysql/ib_buffer_pool",
    "0 [Note] Plugin 'FEDERATED' is disabled.",
    "0 [Note] InnoDB: Buffer pool(s) load completed at 180327 13:50:19",
    "0 [Warning] Failed to set up SSL because of the following SSL library error: SSL context is not usable without certificate and private key",
    "0 [Note] Server hostname (bind-address): '127.0.0.1'; port: 3306",
    "0 [Note]   - '127.0.0.1' resolves to '127.0.0.1';",
    "0 [Note] Server socket created on IP: '127.0.0.1'.",
    "0 [Note] Event Scheduler: Loaded 0 events",
    "0 [Note] /usr/sbin/mysqld: ready for connections.",
    "Version: '5.7.21-0ubuntu0.16.04.1-log'  socket: '/var/run/mysqld/mysqld.sock'  port: 3306  (Ubuntu)"
]

_mysql_error_log_shutdown = [
    "0 [Note] Giving 0 client threads a chance to die gracefully",
    "0 [Note] Shutting down slave threads",
    "0 [Note] Forcefully disconnecting 0 remaining clients",
    "0 [Note] Event Scheduler: Purging the queue. 0 events",
    "0 [Note] Binlog end",
    "0 [Note] Shutting down plugin 'ngram'",
    "0 [Note] Shutting down plugin 'partition'",
    "0 [Note] Shutting down plugin 'BLACKHOLE'",
    "0 [Note] Shutting down plugin 'ARCHIVE'",
    "0 [Note] Shutting down plugin 'MyISAM'",
    "0 [Note] Shutting down plugin 'PERFORMANCE_SCHEMA'",
    "0 [Note] Shutting down plugin 'MEMORY'",
    "0 [Note] Shutting down plugin 'MRG_MYISAM'",
    "0 [Note] Shutting down plugin 'CSV'",
    "0 [Note] Shutting down plugin 'INNODB_SYS_VIRTUAL'",
    "0 [Note] Shutting down plugin 'INNODB_SYS_DATAFILES'",
    "0 [Note] Shutting down plugin 'INNODB_SYS_TABLESPACES'",
    "0 [Note] Shutting down plugin 'INNODB_SYS_FOREIGN_COLS'",
    "0 [Note] Shutting down plugin 'INNODB_SYS_FOREIGN'",
    "0 [Note] Shutting down plugin 'INNODB_SYS_FIELDS'",
    "0 [Note] Shutting down plugin 'INNODB_SYS_COLUMNS'",
    "0 [Note] Shutting down plugin 'INNODB_SYS_INDEXES'",
    "0 [Note] Shutting down plugin 'INNODB_SYS_TABLESTATS'",
    "0 [Note] Shutting down plugin 'INNODB_SYS_TABLES'",
    "0 [Note] Shutting down plugin 'INNODB_FT_INDEX_TABLE'",
    "0 [Note] Shutting down plugin 'INNODB_FT_INDEX_CACHE'",
    "0 [Note] Shutting down plugin 'INNODB_FT_CONFIG'",
    "0 [Note] Shutting down plugin 'INNODB_FT_BEING_DELETED'",
    "0 [Note] Shutting down plugin 'INNODB_FT_DELETED'",
    "0 [Note] Shutting down plugin 'INNODB_FT_DEFAULT_STOPWORD'",
    "0 [Note] Shutting down plugin 'INNODB_METRICS'",
    "0 [Note] Shutting down plugin 'INNODB_TEMP_TABLE_INFO'",
    "0 [Note] Shutting down plugin 'INNODB_BUFFER_POOL_STATS'",
    "0 [Note] Shutting down plugin 'INNODB_BUFFER_PAGE_LRU'",
    "0 [Note] Shutting down plugin 'INNODB_BUFFER_PAGE'",
    "0 [Note] Shutting down plugin 'INNODB_CMP_PER_INDEX_RESET'",
    "0 [Note] Shutting down plugin 'INNODB_CMP_PER_INDEX'",
    "0 [Note] Shutting down plugin 'INNODB_CMPMEM_RESET'",
    "0 [Note] Shutting down plugin 'INNODB_CMPMEM'",
    "0 [Note] Shutting down plugin 'INNODB_CMP_RESET'",
    "0 [Note] Shutting down plugin 'INNODB_CMP'",
    "0 [Note] Shutting down plugin 'INNODB_LOCK_WAITS'",
    "0 [Note] Shutting down plugin 'INNODB_LOCKS'",
    "0 [Note] Shutting down plugin 'INNODB_TRX'",
    "0 [Note] Shutting down plugin 'InnoDB'",
    "0 [Note] InnoDB: FTS optimize thread exiting.",
    "0 [Note] InnoDB: Starting shutdown...",
    "0 [Note] InnoDB: Dumping buffer pool(s) to /var/lib/mysql/ib_buffer_pool",
    "0 [Note] InnoDB: Buffer pool(s) dump completed at 180327 13:50:20",
    "0 [Note] InnoDB: Shutdown completed; log sequence number 2562116",
    "0 [Note] InnoDB: Removed temporary tablespace data file: \"ibtmp1\"",
    "0 [Note] Shutting down plugin 'sha256_password'",
    "0 [Note] Shutting down plugin 'mysql_native_password'",
    "0 [Note] Shutting down plugin 'binlog'",
    "0 [Note] /usr/sbin/mysqld: Shutdown complete",
    "",
    "mysqld_safe mysqld from pid file /var/run/mysqld/mysqld.pid ended"
]

# apache error messages
_apache_error_messages = {
    'emerg': [
        'emergency level statement'
    ],
    'alert': [
        'alert level statement'
    ],
    'crit': [
        'critical level statement'
    ],
    'error': [
        'File does not exist: /home/httpd/wiki/view/Main/MobileHome',
        'File does not exist: /usr/local/apache/htdocs/foo/bar.dll',
        'Directory index forbidden by rule: /home/prod/',
        'Client sent malformed Host header',
        'user foo: authentication failure for "/~foo/resource": Password Mismatch'
    ],
    'warn': [
        'warning level statement'
    ],
    'notice': [
        'Accept mutex: sysvsem (Default: sysvsem)',
        'Apache/1.3.29 (Unix) configured -- resuming normal operations',
        'caught SIGTERM, shutting down'
    ],
    'info': [
        'Server built: Feb 27 2004 13:56:37',
        '(104)Connection reset by peer: client stopped connection before send body completed',
    ],
    'debug': [
        'debug level statement'
    ],
}


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


def get_apache_log_statement(otime=datetime.datetime.now(), local=get_localzone()):
    """
    generates an apache log_statement
    """
    ip = _faker.ipv4()
    dt = otime.strftime('%d/%b/%Y:%H:%M:%S')
    tz = datetime.datetime.now(local).strftime('%z')
    vrb = numpy.random.choice(_verb, p=_verb_p)

    uri = random.choice(_resources)
    if uri.find("apps") > 0:
        uri += str(random.randint(1000, 10000))

    resp = numpy.random.choice(_response, p=_response_p)
    byt = int(random.gauss(5000, 50))
    referer = _faker.uri()
    useragent = numpy.random.choice(_ualist, p=_ualist_p)()
    return ['%s - - [%s %s] "%s %s HTTP/1.0" %s %s "%s" "%s"\n' %
            (ip, dt, tz, vrb, uri, resp, byt, referer, useragent)]


def get_apache_error_log_statement(log_level=_log_level, log_level_p=_log_level_p, otime=datetime.datetime.now(), 
                                   local=get_localzone()):
    """
    generates an apache error log statement
    """
    ip = _faker.ipv4()
    dt = otime.strftime('%a %b %d %H:%M:%S %Y')
    level = numpy.random.choice(log_level, p=log_level_p)
    msg = numpy.random.choice(_apache_error_messages[level])
    return ['[%s] [%s] [client %s] %s \n' % (dt, level, ip, msg)]


def _get_mysql_error_log_startup_or_shutdown(otime=datetime.datetime.now()):
    """
    returns either a start up or shutdown statement for the mysql error log
    """
    # 2018-03-27T13:50:20.397608Z
    time_fmt = '%Y-%m-%dT%H:%M:%S.%fZ'
    dt = otime.strftime(time_fmt)
    outgoing = []
    incoming = _mysql_error_log_startup
    global __mysql_error_started
    if '__mysql_error_started' in globals() and __mysql_error_started:
        incoming = _mysql_error_log_shutdown
        __mysql_error_started = False
    else:
        __mysql_error_started = True

    for stmt in incoming:
        if stmt == '':
            outgoing.append('\n')
        else:
            outgoing.append('{0} {1}\n'.format(dt, stmt))
            otime = datetime.datetime.now()
            dt = otime.strftime(time_fmt)
    return outgoing


def get_mysql_error_log_statement(log_level=_log_level, log_level_p=_log_level_p, otime=datetime.datetime.now(),
                                  local=get_localzone()):
    """
    generate mysql log statements
    """
    # 2018-03-27T13:50:20.397608Z
    time_fmt = '%Y-%m-%dT%H:%M:%S.%fZ'
    dt = otime.strftime(time_fmt)
    level = numpy.random.choice(log_level, p=log_level_p)
    outgoing = []

    global __mysql_error_started
    if '__mysql_error_started' not in globals() or numpy.random.choice([True, False], p=[0.05, 0.95]) or \
       not __mysql_error_started:
        outgoing = _get_mysql_error_log_startup_or_shutdown(otime=otime)

    if not outgoing:
        outgoing = ['%s 0 [%s] seemingly random log message \n' % (dt, level)]

    return outgoing


def _get_file_name(log_type=_log_type, file_prefix=_file_prefix):
    """
    returns the name of the file to write to
    """
    timestr = time.strftime("%Y%m%d-%H%M%S")
    if str.upper(log_type) == 'APACHE':
        log_name = 'access_log'
    elif str.upper(log_type) == 'APACHE_ERROR':
        log_name = 'error_log'
    return log_name+'_'+timestr+'.log' if not file_prefix else file_prefix+'_'+log_name+'_'+timestr+'.log'


def generate(log_lines=_log_lines, file_prefix=_file_prefix, output_type=_output_type, log_type=_log_type,
             sleep_time=_sleep_time, resources=_resources,
             ua_list=_ualist, ua_list_p=_ualist_p,
             verb=_verb, verb_p=_verb_p,
             log_level=_log_level, log_level_p=_log_level_p):
    """
    generates a log statement
    """
    local = get_localzone()
    otime = datetime.datetime.now()

    for case in switch(output_type):
        if case('LOG'):
            f = open(_get_file_name(log_type, file_prefix), 'w')
            break
        if case('GZ'):
            f = gzip.open(_get_file_name(log_type, file_prefix)+'.gz', 'w')
            break
        if case('CONSOLE'):
            pass
        if case():
            f = sys.stdout

    flag = True
    while (flag):
        otime = datetime.datetime.now()

        stmts = [""]
        if str.upper(log_type) == 'APACHE_ERROR':
            stmts = get_apache_error_log_statement(otime=otime, local=local)
        elif str.upper(log_type) == 'APACHE':
            stmts = get_apache_log_statement(otime, local)
        elif str.upper(log_type) == 'MYSQL_ERROR':
            stmts = get_mysql_error_log_statement(otime=otime, local=local)
        else:
            return

        for stmt in stmts:
            f.write(stmt)
            f.flush()

        log_lines = log_lines - 1
        flag = False if log_lines == 0 else True
        # calculate remaining time in interval to wait before begining
        t_wait = ((otime+datetime.timedelta(seconds=sleep_time))-datetime.datetime.now()).total_seconds()
        # wait if there is time to wait, else begin the next loop
        if t_wait > 0:
            time.sleep(t_wait)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(__file__, description="Fake Apache Log Generator")
    parser.add_argument("--output", "-o", dest='output_type', help="Write to a Log file, a gzip file or to STDOUT",
                        choices=['LOG', 'GZ', 'CONSOLE'], default=_output_type)
    parser.add_argument("--num", "-n", dest='num_lines', help="Number of statements to generate (0 for infinite)",
                        type=int, default=_log_lines)
    parser.add_argument("--prefix", "-p", dest='file_prefix', help="Prefix the output file name", type=str,
                        default=_file_prefix)
    parser.add_argument("--sleep", "-s", dest='sleep_time', help="Sleep this long between lines (in seconds)",
                        default=_sleep_time, type=float)
    parser.add_argument("--type", "-t", dest='log_type', help="Specify the type of log you wish to generate",
                        choices=['apache', 'apache_error', 'mysql_error'], default=_log_type, type=str)
    args = parser.parse_args()
    generate(args.num_lines, args.file_prefix, args.output_type, args.log_type, sleep_time=args.sleep_time)
