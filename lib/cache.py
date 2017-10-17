# -*- coding: utf-8 -*-

from config import config


cache = {}


def add_cache(domain, resolve_result):
    if config.max_cache_len == 0:
        return

    if len(cache) == config.max_cache_len:
        for key in cache:
            del cache[key]
            break

    content = resolve_result[2:]    # 截去 msg_id 的部分
    cache[domain] = content


def get_cache(domain, msg_id):
    # 若没有对应的记录，会返回 None
    content = cache.get(domain)
    if content:
        content = msg_id + content
    return content
