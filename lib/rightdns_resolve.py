# -*- coding: utf-8 -*-

import socket
from datetime import datetime

from config import config
from whitelist import match_whitelist
from logger import logger
from dns import decode_msg_id, extract_domain
from udp import udp_send
from poll import SocksPoll
from cache import add_cache, get_cache


def rightdns_resolve(req):
    """
    接收 req，返回 resolved resp。
    若超时，返回 None
    """
    id = decode_msg_id(req)
    domain = extract_domain(req)

    # ===== helper functions =====

    def info(msg):
        logger.info("({}:{}) {}".format(id, domain, msg))

    def debug(msg):
        logger.debug("({}:{}) {}".format(id, domain, msg))

    # ===== 检查缓存 =====

    cache = get_cache(domain, req[:2])
    if cache:
        info("resolved from cache")
        return cache

    # ===== execute resolve =====

    poisoned = False    # 是否已判定域名被污染

    normal_resp = None
    safe_resp = None
    response = None     # 输出给客户端的 reponse

    poll = SocksPoll.create()

    safe_req = udp_send(('127.0.0.1', config.google_proxy_port), req)
    poll.register(safe_req)

    # 若待解析的域名与白名单匹配，则无需再获取 fake / normal resp
    if match_whitelist(req):
        logger.debug("{}:{} domain match whitelist".format(id, domain))
        poisoned = True
        fake_req = normal_req = None
    else:
        fake_req = udp_send((config.fake_dns_ip, 53), req)
        poll.register(fake_req)

        normal_req = udp_send((config.normal_dns_ip, config.normal_dns_port), req)
        poll.register(normal_req)

    poll_started = datetime.now()
    while True:
        prepared_socks = poll.poll(0.1)

        spent_seconds = (datetime.now() - poll_started).total_seconds()
        if len(prepared_socks) == 0 and config.resolve_timeout > 0 and spent_seconds > (config.resolve_timeout / 1000.0):
            info("timeout. safe_resp: {}, normal_resp: {}".format(safe_resp is not None, normal_resp is not None))

            # 超时，若当前已经取得 safe_resp（即超时是因为没能取得 normal_resp），则返回 safe_resp；否则结束此次解析
            if safe_resp:
                poisoned = True
            else:
                return

        if fake_req in prepared_socks:
            # 如果在其他检查项完成前，从 fake_req 处收到了响应，则立刻将域名判定为已被污染
            debug("received fake response: {}".format(fake_req.recv(2048)))
            poisoned = True

        if safe_req in prepared_socks:
            safe_resp = safe_req.recv(2048)
            debug("received safe response: {}".format(safe_resp))

            if not poisoned and match_whitelist(safe_resp):
                poisoned = True
                debug("cname from safe response matchs whitelist")

        if normal_req in prepared_socks:
            normal_resp = normal_req.recv(2048)
            debug("received normal response: {}".format(normal_resp))

            if not poisoned and match_whitelist(normal_resp):
                poisoned = True
                debug("cname from normal response matchs whitelist")

        if poisoned:
            if safe_resp:
                response = safe_resp
                break
        elif safe_resp and normal_resp:
            # 当前域名未被标记为污染，说明尚没有收到 fake response。如果此时解析耗时尚未达到 fake_response_delay，则等到达到 fake_response_delay，
            # 如果依然没有收到 fake response，才认定域名没有被污染
            remaining_fake_delay_in_sec = (config.fake_response_delay / 1000.0) - (datetime.now() - poll_started).total_seconds()
            if remaining_fake_delay_in_sec > 0:
                debug('wait for fake response')
                try:
                    fake_req.settimeout(remaining_fake_delay_in_sec)
                    debug("received fake response: {}".format(fake_req.recv(2048)))

                    response = safe_resp
                    break
                except socket.timeout:
                    pass

            response = normal_resp
            break

    info("resolved with {} response".format("safe" if poisoned else "normal"))
    add_cache(domain, response)
    return response
