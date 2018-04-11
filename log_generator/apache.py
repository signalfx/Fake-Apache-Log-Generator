from .common import Faker
import datetime
from tzlocal import get_localzone
from . import log_generator
import numpy
import random


class Generator(log_generator.Generator):
    def __init__(self):
        self._faker = Faker()
        self._verb = ["GET", "POST", "DELETE", "PUT"]
        self._verb_p = [0.6, 0.1, 0.1, 0.2]
        self._response = ["200", "404", "500", "301"]
        self._response_p = [0.9, 0.04, 0.02, 0.04]
        self._resources = ["/list", "/wp-content", "/wp-admin", "/explore", "/search/tag/list", "/app/main/posts",
                           "/posts/posts/explore", "/apps/cart.jsp?appID="]
        self._ualist = [self._faker.firefox, self._faker.chrome, self._faker.safari, self._faker.internet_explorer,
                        self._faker.opera]
        self._ualist_p = [0.5, 0.3, 0.1, 0.05, 0.05]
        super(Generator, self).__init__("apache")

    def getLogStatement(self, otime=datetime.datetime.now(), local=get_localzone(), state={}):
        """
        generates an apache log_statement
        """
        ip = self._faker.ipv4()
        dt = otime.strftime('%d/%b/%Y:%H:%M:%S')
        tz = datetime.datetime.now(local).strftime('%z')
        vrb = numpy.random.choice(self._verb, p=self._verb_p)

        uri = random.choice(self._resources)
        if uri.find("apps") > 0:
            uri += str(random.randint(1000, 10000))

        resp = numpy.random.choice(self._response, p=self._response_p)
        byt = int(random.gauss(5000, 50))
        referer = self._faker.uri()
        useragent = numpy.random.choice(self._ualist, p=self._ualist_p)()
        return ['%s - - [%s %s] "%s %s HTTP/1.0" %s %s "%s" "%s"\n' %
                (ip, dt, tz, vrb, uri, resp, byt, referer, useragent)]
