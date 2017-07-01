# -*- coding: utf-8 -*-

import socket
from async_utils import async_run


def udp_send(target, content):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(content, target)
    return s


def create_udp_server(port, handler):
    """
    建立一个 UDP server。

    port
        此 server 监听的端口

    handler
        (sock, address, content) => None
        每当有 client 向此 server 发送数据时，便把数据传给它
        此函数会被放到一个新的线程里运行，因此可以任意执行阻塞操作，不用担心阻塞整个 server 的运行
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))

    while True:
        content, address = sock.recvfrom(2048)
        async_run(handler, sock, address, content)
