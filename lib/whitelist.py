# -*- coding: utf-8 -*-

from os.path import dirname, join, abspath, isfile
import re

from logger import logger


def read_whitelist():
    filepath = abspath(join(dirname(__file__), '../config')) + "/whitelist.txt"

    if isfile(filepath):
        logger.info("read whitelist from " + filepath)
        with open(filepath) as f:
            patterns = [
                pattern.strip()
                for pattern in f.read().split("\n") if len(pattern.strip()) and pattern.strip()[0] != "#"
            ]
            # 经测试，把多个正则表达式合并成一个正则表达式进行匹配，比分别进行匹配在大多数情况下效率更高
            return "|".join(patterns)
    else:
        logger.info("whitelist.txt not exist, skip")
        return None


whitelist_patterns = read_whitelist()


def match_whitelist(dns_body):
    return whitelist_patterns and bool(re.search(whitelist_patterns, dns_body))
