# -*- coding: utf-8 -*-

import httplib
import ssl
import json

from config import config
from dns import domain_to_dns_name, extract_domain
from bits import bits2str, int2str, int2bits
from udp import create_udp_server


def start_google_https_dns_proxy_server():
    def handler(sock, address, req):
        msg_id = req[:2]
        domain = extract_domain(req)

        google_resp = request_google_https_dns(domain)
        dns_resp = format_google_response(msg_id, google_resp)

        sock.sendto(dns_resp, address)

    create_udp_server(config.google_proxy_port, handler)


def format_google_response(msg_id, google_resp):
    """
    把 Google 返回的 JSON 格式的数据转换成 DNS 消息格式

    DNS 格式参见 README 里列出的相关资料
    """
    gr = google_resp

    # ===== header =====
    QR = '1'
    OPCODE = '0000'
    AA = '0'
    TC = '1' if gr["TC"] else '0'
    RD = '1'
    RA = '1'
    res1 = '0'
    res2 = '0'
    res3 = '0'
    RCODE = int2bits(gr["Status"], 4)
    header_part2 = bits2str(''.join([QR, OPCODE, AA, TC, RD, RA, res1, res2, res3, RCODE]))

    QDCOUNT = int2str(1)
    ANCOUNT = int2str(len(gr.get("Answer", [])))
    NSCOUNT = int2str(len(gr.get("Authority", [])))     # 已知解析 .in-addr.arpa 类域名时会出现这部分内容
    ARCOUNT = int2str(len(gr.get("Additional", [])))

    header = msg_id + header_part2 + QDCOUNT + ANCOUNT + NSCOUNT + ARCOUNT

    # ===== question =====
    QNAME = domain_to_dns_name(gr["Question"][0]["name"].encode())
    QTYPE = int2str(1)
    QCLASS = int2str(1)

    question = QNAME + QTYPE + QCLASS

    # ===== response =====
    resp = ''

    for resp_type in ["Answer", "Authority", "Additional"]:
        if resp_type not in gr:
            continue

        for i in gr[resp_type]:
            NAME = domain_to_dns_name(i["name"].encode())
            TYPE = int2str(i["type"])
            CLASS = int2str(1)
            TTL = int2str(i["TTL"], 32)

            if i["type"] == 1:     # A 记录
                RDLENGTH = int2str(4)
                RDATA = ''
                for ip_part in i["data"].split("."):
                    RDATA += chr(int(ip_part))
            elif i["type"] == 5:    # CNAME 记录（例如 www.adobe.com 的解析结果里就有）
                RDATA = domain_to_dns_name(i["data"].encode())
                RDLENGTH = int2str(len(RDATA))
            elif i["type"] == 6:    # SOA 记录（例如 .in-addr.arpa 类域名的解析结果里就有）
                primary_ns, admin_mb, \
                    serial_number, refresh_interval, \
                    retry_interval, expiratio_limit, ttl = i["data"].encode().split(" ")

                RDATA = domain_to_dns_name(primary_ns) + domain_to_dns_name(admin_mb) \
                    + int2str(int(serial_number), 32) + int2str(int(refresh_interval), 32) \
                    + int2str(int(retry_interval), 32) + int2str(int(expiratio_limit), 32) \
                    + int2str(int(ttl), 32)
                RDLENGTH = int2str(len(RDATA))
            else:
                raise Exception('unknown answer type: {}'.format(i["type"]))

            resp += (NAME + TYPE + CLASS + TTL + RDLENGTH + RDATA)

    return header + question + resp


def request_google_https_dns(domain):
    """
    执行请求，返回 JSON 数据。

    响应内容的格式：
    https://developers.google.com/speed/public-dns/docs/dns-over-https
    """

    # 因为无法确保当前环境下能够成功解析出 DNS-Over-HTTPS 服务的 IP，因此使用预先准备好的 IP 地址
    # 这样做的缺点是必须关闭 HTTPS 证书检查。方法来自：https://stackoverflow.com/a/32189376/2815178
    conn = httplib.HTTPSConnection(config.dns_google_com_ip, context=ssl._create_unverified_context())
    conn.request('GET', '/resolve?name=' + domain, None, {"Host": "dns.google.com"})
    raw_resp = conn.getresponse().read()
    resp = json.loads(raw_resp)
    return resp
