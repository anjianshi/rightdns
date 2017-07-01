# -*- coding: utf-8 -*-

import string
import binascii
import sys
import datetime


# logging level
ERROR = "ERROR"
INFO = "INFO"
DEBUG = "DEBUG"

printset = set(string.printable) - set(["\t", "\r", "\n", "\x0b", "\x0c"])


class Logger:
    def __init__(self, log_file_path, ignore_debug=True, buffer_size=0):
        self.logfile = open(log_file_path, "a", buffer_size) if log_file_path is not None else None
        self.ignore_debug = ignore_debug

    def _log(self, msg, level):
        if level == DEBUG and self.ignore_debug:
            return

        # handle chars like \x01
        msg = "".join(c if c in printset else '\\x' + binascii.b2a_hex(c) for c in msg)
        log_content = "[{}][{}] {}\n".format(level, datetime.datetime.now().strftime("%m-%d %H:%M:%S %f"), msg)

        if self.logfile is not None:
            self.logfile.write(log_content)

        if level == ERROR:
            sys.stderr.write(log_content)
        else:
            sys.stdout.write(log_content)

    def info(self, msg):
        self._log(msg, INFO)

    def debug(self, msg):
        self._log(msg, DEBUG)

    def error(self, msg):
        self._log(msg, ERROR)

    def flush(self):
        if self.logfile is not None:
            self.logfile.flush()


# ========================================

from config import config
logger = Logger(config.log_path, not config.debug, config.log_buffer_size)
