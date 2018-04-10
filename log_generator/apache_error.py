from common import Faker
import datetime
from tzlocal import get_localzone
from log_generator import BaseGenerator
import numpy


class Generator(BaseGenerator):
    def __init__(self):
        self._faker = Faker()

        # log levels for apache 2.4+
        self._log_level = ["emerg", "alert", "crit", "error", "warn", "notice", "info", "debug", "trace1", "trace2",
                           "trace3", "trace4", "trace5", "trace6", "trace7", "trace8"]
        self._log_level_p = [0.05, 0.05, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.0375, 0.0375, 0.0375, 0.0375, 0.0375, 0.0375,
                             0.0375, 0.0375]
        # apache error messages
        self._apache_error_messages = {
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
            'trace1': [
                'trace level statement'
            ],
            'trace2': [
                'trace level statement'
            ],
            'trace3': [
                'trace level statement'
            ],
            'trace4': [
                'trace level statement'
            ],
            'trace5': [
                'trace level statement'
            ],
            'trace6': [
                'trace level statement'
            ],
            'trace7': [
                'trace level statement'
            ],
            'trace8': [
                'trace level statement'
            ]
        }
        super(Generator, self).__init__("apache_error")

    def getLogStatement(self, otime=datetime.datetime.now(), local=get_localzone()):
        """
        generates an apache error log statement
        """
        ip = self._faker.ipv4()
        dt = otime.strftime('%a %b %d %H:%M:%S %Y')
        level = numpy.random.choice(self._log_level, p=self._log_level_p)
        msg = numpy.random.choice(self._apache_error_messages[level])
        return ['[%s] [%s] [client %s] %s \n' % (dt, level, ip, msg)]
