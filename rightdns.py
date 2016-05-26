#!/usr/bin/python2
# -*- coding: utf-8 -*-
import socket
import re
import os
import sys
import select
from datetime import datetime

from daemon import Daemon
from util import _async, udp_send, extract_domain, Logger
import config


base = os.path.dirname(os.path.abspath(__file__))

logger = Logger(config.log_path, not config.debug, config.log_buffer_size)


class DNSDaemon(Daemon):
    def run(self):
        self.whitelist_patterns = self.read_whitelist()

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(('0.0.0.0', config.port))
        logger.info("listening DNS request on {}".format(config.port))

        id = 1
        while True:
            content, address = self.server_socket.recvfrom(2048)
            if config.debug:
                logger.debug("({}) received request from {}: '{}'".format(id, address, content))
            self.resolve(content, address, id)
            id += 1

    def read_whitelist(self):
        path = base + "/whitelist.txt"
        if os.path.isfile(path):
            logger.info("read whitelist from " + path)
            with open(path) as f:
                patterns = [
                    pattern.strip()
                    for pattern in f.read().split("\n") if len(pattern.strip()) and pattern.strip()[0] != "#"
                ]
                # 经测试，把多个正则表达式合并成一个正则表达式进行匹配，比分别进行匹配在大多数情况下效率更高
                return "|".join(patterns)
        else:
            logger.info("whitelist.txt not exist, skip")
            return None

    def match_whitelist(self, domain):
        return bool(re.search(self.whitelist_patterns, domain))

    def cnames_match_whitelist(self, dns_response):
        return any(map(self.match_whitelist, extract_domain(dns_response, multiple=True)))

    @_async
    def resolve(self, request, address, id):
        fake_req = udp_send((config.fake_dns_ip, 53), request)
        safe_req = udp_send((config.safe_dns_ip, config.safe_dns_port), request)
        normal_req = udp_send((config.normal_dns_ip, config.normal_dns_port), request)

        epoll = select.epoll()
        epoll.register(fake_req, select.EPOLLIN)
        epoll.register(safe_req, select.EPOLLIN)
        epoll.register(normal_req, select.EPOLLIN)

        poisoned = False

        domain = extract_domain(request)
        if domain is None:
            logger.error("({}) can't extract domain".format(id))
            poisoned = True
        elif self.whitelist_patterns and self.match_whitelist(domain):
            logger.debug("({}) domain {} match whitelist".format(id, domain))
            poisoned = True

        safe_resp = None
        normal_resp = None
        response = None     # 输出给客户端的 reponse
        poll_started = datetime.now()
        while True:
            fd_list = epoll.poll(0.1)
            spent_seconds = (datetime.now() - poll_started).total_seconds()
            if len(fd_list) == 0 and config.resolve_timeout > 0 and spent_seconds > (config.resolve_timeout / 1000.0):
                logger.info("({}) timeout! domain: {}, safe_resp: {}, normal_resp: {}".format(
                    id, domain, safe_resp is not None, normal_resp is not None))
                return  # 结束此次解析

            if (fake_req.fileno(), select.EPOLLIN) in fd_list:
                # 如果在其他检查项完成前，从 fake_req 处收到了响应，则立刻将域名判定为已被污染
                epoll.unregister(fake_req)
                self.log_fake_response(id, domain, fake_req.recv(2048))
                poisoned = True

            if (safe_req.fileno(), select.EPOLLIN) in fd_list:
                epoll.unregister(safe_req)
                safe_resp = safe_req.recv(2048)
                logger.debug("({}) domain {} received safe response: {}".format(id, domain, safe_resp))

                if(not poisoned and self.cnames_match_whitelist(safe_resp)):
                    poisoned = True
                    logger.debug("({}) domain {}'s cname from safe response matchs whitelist".format(id, domain))

            if (normal_req.fileno(), select.EPOLLIN) in fd_list:
                epoll.unregister(normal_req)
                normal_resp = normal_req.recv(2048)
                logger.debug("({}) domain {} received normal response: {}".format(id, domain, normal_resp),)

                if(not poisoned and self.cnames_match_whitelist(normal_resp)):
                    poisoned = True
                    logger.debug("({}) domain {}'s cname from normal response matchs whitelist".format(id, domain))

            if poisoned:
                if safe_resp:
                    response = safe_resp
                    break
            elif safe_resp and normal_resp:
                # 当前域名未被标记为污染，说明尚没有收到 fake response。如果此时解析耗时尚未达到 fake_response_delay，则等到达到 fake_response_delay，
                # 如果依然没有收到 fake response，才认定域名没有被污染
                remaining_fake_delay_in_sec = (config.fake_response_delay / 1000.0) - (datetime.now() - poll_started).total_seconds()
                if remaining_fake_delay_in_sec > 0:
                    logger.debug('({}) wait for fake response'.format(id))
                    try:
                        fake_req.settimeout(remaining_fake_delay_in_sec)
                        self.log_fake_response(id, domain, fake_req.recv(2048))
                        poisoned = True
                        response = safe_resp
                    except socket.timeout:
                        pass

                response = normal_resp
                break

        logger.info("({}) domain {} marks as {}, resolve result: {}".format(
            id, domain, "poisoned" if poisoned else "normal", response))
        self.server_socket.sendto(response, address)

    def log_fake_response(self, id, domain, response):
        logger.debug("({}) domain {} received fake response: {}".format(id, domain, response))


if __name__ == "__main__":
    daemon = DNSDaemon(base + "/dns.pid")

    action = "start"
    for act_name in ["start", "stop", "restart", "run"]:    # 'run' is the foreground mode
        if act_name in sys.argv:
            action = act_name
            break
    getattr(daemon, action)()
