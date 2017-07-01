# -*- coding: utf-8 -*-

"""
dns 工具函数

DNS 格式参见 README 里列出的相关资料
"""

from bits import str2bits, bits2int


def decode_msg_id(req):
    """把 message id 解析成十进制整数"""
    raw = req[0:2]
    return bits2int(str2bits(raw))


def extract_domain(req):
    """
    从 DNS 请求中提取出待解析的域名
    """

    # header 部分占了 12 bytes，抛掉这部分后面就开始是 question 部分
    req_rest = req[12:]

    domain = ''

    while True:
        [sign_char, req_rest] = [req_rest[0], req_rest[1:]]

        part_char_len = ord(sign_char)
        if part_char_len == 0:
            break

        [part, req_rest] = [req_rest[:part_char_len], req_rest[part_char_len:]]
        if domain != '':
            domain += '.'
        domain += part

    return domain


def domain_to_dns_name(domain):
    """把 domain 用 DNS 里的元信息表示法表示。用于 DNS Answer（因为没搞明白怎么用指针法来表示）"""

    # 若域名以 '.' 结尾，把末尾多余的 '.' 去掉
    if domain[-1:] == '.':
        domain = domain[:-1]

    parts = domain.split(".")

    name = ''
    for part in parts:
        name += chr(len(part))
        name += part
    name += chr(0)

    return name
