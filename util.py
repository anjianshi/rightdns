# -*- coding: utf-8 -*-

from threading import Thread
import socket
import re
import string
import binascii
import sys


def _async(f):
    """应用了此装饰器的函数，其内容会被异步执行"""
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper


def udp_send(target, content):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(content, target)
    return s


def extract_domain(dns_packets, multiple=False):
    domain_pattern = r'(?:\w|-)+(?:[^\w\-](?:\w|-)+)+'

    def sub(content):
        return re.sub(r'[^\w\-]', '.', content)

    if multiple:
        return map(sub, re.findall(domain_pattern, dns_packets))
    else:
        match = re.search(domain_pattern, dns_packets)
        return sub(match.group()) if match else None


# logging level
ERROR = "ERROR"
INFO = "INFO"
DEBUG = "DEBUG"

printset = set(string.printable) - set(["\t", "\r", "\n", "\x0b", "\x0c"])


class Logger:
    def __init__(self, log_file_path, ignore_debug=True):
        self.logfile = open(log_file_path, "a")
        self.ignore_debug = ignore_debug

    def _log(self, msg, level):
        if level == DEBUG and self.ignore_debug:
            return

        # handle chars like \x01
        msg = "".join(c if c in printset else '\\x' + binascii.b2a_hex(c) for c in msg)
        log_content = "[{}] {}\n".format(level, msg)

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
