#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
import re
import os
import sys
from threading import Thread

import config

# 运行时加 -d 参数能获得更详细的输出信息
debug = "-d" in sys.argv

with open(os.path.dirname(os.path.realpath(__file__)) + "/whitelist.txt") as f:
    whitelist_patterns = [
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
    domain = extract_domain(content)

    in_whitelist = False
    if domain is not None:
        for pattern in whitelist_patterns:
            if re.search(pattern, domain):
                in_whitelist = True
                break

    if in_whitelist:
        poisoned = True
    else:
        fake_req = udp_send((config.fake_dns_ip, 53), content)
        try:
            fake_req.settimeout(config.poisoning_response_delay / 1000.0)
            fake_resp = fake_req.recv(1024)
            if debug:
                print("got poisoned result", content, fake_resp)
            poisoned = True
        except socket.timeout:
            poisoned = False

    req = udp_send(
        (config.safe_dns_ip, config.safe_dns_port) if poisoned else (config.normal_dns_ip, config.normal_dns_port),
        content
    )
    resp = req.recv(2048)
    server_socket.sendto(resp, address)
    print('handled ' + ('poisoned' if poisoned else 'normal') + ' domain', resp)


def extract_domain(req_content):
    match = re.search(r'(\w|-)+([^\w\-](\w|-)+)+', content)
    if match:
        domain = re.search(r'(\w|-)+([^\w\-](\w|-)+)+', content).group()
        domain = re.sub(r'[^\w\-]', '.', domain)
        return domain
    else:
        print("error: can't extract domain", content)
        return None


def udp_send(target, content):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(content, target)
    return s


# ===========================================

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('0.0.0.0', config.port))
print("listening DNS request on {}".format(config.port))

while True:
    content, address = server_socket.recvfrom(2048)
    if debug:
        print("received: ", content, address)
    handle_request(content, address, server_socket)
