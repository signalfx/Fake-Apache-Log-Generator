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
_log_level_p = [0.5, 0.5, 0.5, 0.2, 0.5, 0.5, 0.2, 0.5, 0.0375, 0.0375, 0.0375, 0.0375, 0.0375, 0.0375, 0.0375, 0.0375]

_resources = ["/list", "/wp-content", "/wp-admin", "/explore", "/search/tag/list", "/app/main/posts",
              "/posts/posts/explore", "/apps/cart.jsp?appID="]

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
    return '%s - - [%s %s] "%s %s HTTP/1.0" %s %s "%s" "%s"\n' % (ip, dt, tz, vrb, uri, resp, byt, referer, useragent)


def get_apache_error_log_statement(log_level=_log_level, log_level_p=_log_level_p, otime=datetime.datetime.now(), 
                                   local=get_localzone()):
    """
    generates an apache error log statement
    """
    ip = _faker.ipv4()
    dt = otime.strftime('%a %b %d %H:%M:%S %Y')
    level = numpy.random.choice(log_level, p=log_level_p)
    msg = numpy.random.choice(_apache_error_messages[level])
    return '[%s] [%s] [client %s] %s \n' % (dt, level, ip, msg)


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

        stmt = ""
        if str.upper(log_type) == "APACHE_ERROR":
            stmt = get_apache_error_log_statement(otime=otime, local=local)
        elif str.upper(log_type) == 'APACHE':
            stmt = get_apache_log_statement(otime, local)

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
    parser.add_argument("--num", "-n", dest='num_lines', help="Number of lines to generate (0 for infinite)", type=int,
                        default=_log_lines)
    parser.add_argument("--prefix", "-p", dest='file_prefix', help="Prefix the output file name", type=str,
                        default=_file_prefix)
    parser.add_argument("--sleep", "-s", dest='sleep_time', help="Sleep this long between lines (in seconds)",
                        default=_sleep_time, type=float)
    parser.add_argument("--type", "-t", dest='log_type', help="Specify the type of log you wish to generate",
                        choices=['apache', 'apache_error'], default=_log_type, type=str)
    args = parser.parse_args()
    generate(args.num_lines, args.file_prefix, args.output_type, args.log_type, sleep_time=args.sleep_time)
