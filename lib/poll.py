# -*- coding: utf-8 -*-

import select


class SocksPoll(object):
    """兼容 macOS 和 Linux 的 poll 对象"""

    @staticmethod
    def create():
        if hasattr(select, "epoll"):
            return SocksEpoll()
        else:
            return SocksKqueue()

    def __init__(self):
        self.socks = {}    # fileno: sock

    def register(self, sock):
        self.socks[sock.fileno()] = sock

    def poll(self, *args, **kwargs):
        """返回已准备就绪的 socks 列表"""
        fileno_list = self.execute_poll(*args, **kwargs)
        return [
            self.socks[fileno] for fileno in fileno_list
        ]

    def execute_poll(self, timeout):
        """返回已准备就绪的 fileno 列表"""
        raise Exception("not implemeted")


class SocksKqueue(SocksPoll):
    def __init__(self):
        super(SocksKqueue, self).__init__()

        self.kq = select.kqueue()
        self.events = []

    def register(self, sock):
        super(SocksKqueue, self).register(sock)
        self.events.append(select.kevent(sock.fileno()))

    def execute_poll(self, timeout=None):
        event_list = self.kq.control(self.events, len(self.events), timeout)
        return [e.ident for e in event_list]


class SocksEpoll(SocksPoll):
    def __init__(self):
        super(SocksEpoll, self).__init__()
        self.epoll = select.epoll()

    def register(self, sock):
        super(SocksEpoll, self).register(sock)
        self.epoll.register(sock, select.EPOLLIN)

    def execute_poll(self, timeout=-1):
        event_list = self.epoll.poll(timeout)
        return [e[0] for e in event_list]
