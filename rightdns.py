#!/usr/bin/python2
# -*- coding: utf-8 -*-
import os
import sys

from config import config
from lib.daemon import Daemon
from lib.logger import logger
from lib.dns import decode_msg_id
from lib.udp import create_udp_server
from lib.google_https_dns import start_google_https_dns_proxy_server
from lib.rightdns_resolve import rightdns_resolve
from lib.async_utils import async_run


class DNSDaemon(Daemon):
    def run(self):
        if config.use_https_dns:
            logger.info("starting Google HTTPS DNS proxy")
            async_run(start_google_https_dns_proxy_server)

        logger.info("listening DNS request on {}".format(config.port))
        create_udp_server(config.port, self.resolve)

    def resolve(self, sock, address, req):
        logger.debug("({}) received request from {}: '{}'".format(decode_msg_id(req), address, req))
        resp = rightdns_resolve(req)
        if resp:
            sock.sendto(resp, address)


if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    daemon = DNSDaemon(base + "/dns.pid")

    action = "start"
    for act_name in ["start", "stop", "restart", "run"]:    # 'run' is the foreground mode
        if act_name in sys.argv:
            action = act_name
            break
    getattr(daemon, action)()
