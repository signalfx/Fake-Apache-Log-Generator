import datetime
from tzlocal import get_localzone
import gzip
import numpy
import os
from .common import switch, log_types
import random
import sys
import time


class Generator(object):
    def __init__(self, log_type=None, stop_probability=0.05):
        self.log_type = log_type
        self.stop_probability = stop_probability

    def getLogStatement(otime=datetime.datetime.now(), local=get_localzone(), state={}):
        pass

    def getStartStatement(self, otime=datetime.datetime.now(), local=get_localzone(), state={}):
        return []

    def getStopStatement(self, otime=datetime.datetime.now(), local=get_localzone(), state={}):
        return []

    def _get_file_name(self, file_prefix=None):
        """
        returns the name of the file to write to
        """
        timestr = time.strftime("%Y%m%d-%H%M%S")
        log_name = ''
        if str.lower(self.log_type) in log_types:
            log_name = str.lower(self.log_type)
        return log_name+'_'+timestr+'.log' if not file_prefix else file_prefix+'_'+log_name+'_'+timestr+'.log'

    def _getOutputObj(self, output_type, filename='', output=None, limit=None):
        """
        Set the output type on the generator
        """
        if output is None:
            for case in switch(output_type):
                if case('LOG'):
                    output = open(filename, 'w')
                    break
                if case('GZ'):
                    output = gzip.open(filename+'.gz', 'wb')
                    break
                if case('CONSOLE'):
                    pass
                if case():
                    output = sys.stdout
        elif limit is not None:
            for case in switch(output_type):
                if case('LOG'):
                    if os.path.getsize(filename) > limit:
                        output.seek(0)
                        output.truncate()
                    break
                if case('GZ'):
                    if os.path.getsize(filename) > limit:
                        output.close()
                        os.remove(filename)
                        output = gzip.open(filename, 'wb')
                    break
                if case('CONSOLE'):
                    pass
                if case():
                    output = sys.stdout
        return output

    def generate(self, output_type='CONSOLE', log_lines=-1, file_prefix=None, sleep_time=0, limit=None, max_dither=0):
        """
        generates a log statement
        """
        local = get_localzone()
        otime = datetime.datetime.now()
        filename = self._get_file_name(file_prefix)
        output = self._getOutputObj(output_type=output_type, filename=filename)

        state = {}

        started = False

        while (True):
            otime = datetime.datetime.now()
            stmts = []
            if not started:
                stmts = self.getStartStatement(otime, local)
                started = True
            elif started and numpy.random.choice([True, False], p=[self.stop_probability, 1.0-self.stop_probability]):
                stmts = self.getStopStatement(otime, local)
                started = False

            if len(stmts) == 0:
                stmts = self.getLogStatement(otime, local, state=state)

            # check for truncation and write out
            for stmt in stmts:
                output = self._getOutputObj(output=output, filename=filename, limit=limit,
                                            output_type=output_type)
                for case in switch(output_type):
                    if case('GZ'):
                        output.write(bytes(stmt, 'utf-8'))
                        break
                    if case('CONSOLE') or case('LOG'):
                        pass
                    if case():
                        output.write(stmt)
                output.flush()
                log_lines = log_lines - 1
                if log_lines == 0:
                    break

            if log_lines == 0:
                break

            sleep_amount = sleep_time + random.randint(0, max_dither)

            # calculate remaining time in interval to wait before begining
            t_wait = ((otime+datetime.timedelta(seconds=sleep_amount))-datetime.datetime.now()).total_seconds()

            # wait if there is time to wait, else begin the next loop
            if t_wait > 0:
                time.sleep(t_wait)
        return self
