"""Global logging helper"""
import logging


LOG_LEVEL = logging.DEBUG


logging.basicConfig(level=LOG_LEVEL)

log = logging.getLogger('upshot')
