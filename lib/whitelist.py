# -*- coding: utf-8 -*-

from os.path import dirname, join, abspath, isfile
import re

from logger import logger


def read_whitelist():
    patterns = []
    base = abspath(join(dirname(__file__), '../config'))

    for filename in ['whitelist.default.txt', 'whitelist.txt']:
        filepath = base + '/' + filename
        if isfile(filepath):
            logger.info("read whitelist from " + filepath)
            with open(filepath) as f:
                patterns.extend(
                    pattern.strip()
                    for pattern in f.read().split("\n") if len(pattern.strip()) and pattern.strip()[0] != "#"
                )
        else:
            logger.info(filename + " not exist, skip")

    # 经测试，把多个正则表达式合并成一个正则表达式进行匹配，比分别进行匹配在大多数情况下效率更高
    return "|".join(patterns)


whitelist_patterns = read_whitelist()


def match_whitelist(dns_body):
    return whitelist_patterns and bool(re.search(whitelist_patterns, dns_body))
