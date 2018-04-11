from .log_generator import Generator
import importlib
from .common import log_types

__all__ = ['Generator']

for t in log_types:
    importlib.import_module('log_generator.{0}'.format(t))
    __all__.append(t)
