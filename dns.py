#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
import re
import os
import sys
from threading import Thread

debug = "-d" in sys.argv

port = 9992

normal_dns = ('220.189.127.106', 53)
blocked_dns = ('safe dns server', 5353)

with open(os.path.dirname(os.path.realpath(__file__)) + "/blocked_domains.txt") as f:
    block_domain_patterns = [
        pattern.strip()
        for pattern in f.read().split("\n") if len(pattern.strip()) and pattern.strip()[0] != "#"
    ]


# =========================================

def _async(f):
    """应用了此装饰器的函数，其内容会被异步执行"""
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper


@_async
def handle_request(content, address, server_socket):
    match = re.search(r'(\w|-)+([^\w\-](\w|-)+)+', content)
    if match:
        domain = re.search(r'(\w|-)+([^\w\-](\w|-)+)+', content).group()
        domain = re.sub(r'[^\w\-]', '.', domain)

        blocked = False
        for pattern in block_domain_patterns:
            if re.search(pattern, domain):
                blocked = True
                break
    else:
        print("can't extract domain", content)
        domain = "empty"
        blocked = False

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(content, blocked_dns if blocked else normal_dns)
    server_socket.sendto(s.recv(1024), address)
    print("handled", domain, 'blocked' if blocked else 'normal', address)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('0.0.0.0', port))
print("listening UDP on {}".format(port))

while True:
    content, address = server_socket.recvfrom(1024)
    if debug:
        print("received: ", content, address)
    handle_request(content, address, server_socket)
