# -*- coding: utf-8 -*-

"""
二进制相关工具函数

= 相关概念说明

str
    字符串

char
    字符串里的一个字符（不考虑中文）

byte
    字节。字符串里每个字符的大小是 1 byte

bit
    位。数据的最小单位。
    1 byte = 8 bit

二进制字符串
    把 bits 数据（即二进制值）以字符串的形式表示出来。
    例如 3 的二进制值是 11，对应的二进制字符串值就是 '11'。


因为 1 byte = 8 bit，所以 1 byte 的数据（即一个 char）改为以二进制字符串的形式表示时，会表示成 8 位长度的字符串。（因为二进制字符串的每一位代表 1 bit 的值）
在把一长串二进制字符串转换为 str 时，也是每 8 位截取一次，转换成一个 char。

在进行二进制处理时，不要把 char 想象成一个字符，而应想象成它是一个包裹了 1 byte（8 bit）数据的容器。
而 str 则是一个更大的容器，里面有一个个小封包（char），每一个小封包代表一长串二进制字符串里其中 8 位的值。

ord(char)   => char to value
chr(number) => value to char
"""


def int2bits(i, len=8):
    """把十进制整数转换成指定长度的二进制字符串"""
    raw = bin(i)        # 10 => '0b1010'
    clean = raw[2:]     # '0b1010' => '1010'
    return clean.zfill(len)  # '1010' => '00001010'


def bits2int(bits):
    """
    把二进制字符串转换成十进制整数
    '01100001' => 97
    '0110000101100001' => 24929
    """
    return int(bits, 2)


def char2bits(char):
    """
    把一个 char 里的数值解码成二进制字符串

    例如一个字符是 'a'，它的 ascii 码是 97，对应的二进制值是 1100001 ，
    此函数就会返回 '01100001'
    """
    value = ord(char)              # 取得 char 里存储的数值
    return int2bits(value)


def str2bits(str):
    """
    把封装成了字符串的数据值解码成二进制字符串
    'aa' => '01100001' + '01100001' => '0110000101100001'
    """
    bits = ''
    for char in str:
        bits += char2bits(char)
    return bits


def split_bits(bits):
    """
    把二进制字符串划分成 8 位一组（因为每 8 位对应于 1 byte，可以容纳到一个 char 里）
    0110000101100001 => ['01100001', '01100001']
    """
    parts = []

    start = 0
    while start + 8 <= len(bits):
        part = bits[start:start + 8]
        parts.append(part)
        start += 8

    return parts


def bits2str(bits):
    """
    把二进制字符串封装成普通字符串
    0110000101100001 => '01100001' '01100001' => 'aa'
    """
    str = ''

    for char_bits in split_bits(bits):
        ascii_code = bits2int(char_bits)        # 97
        char = chr(ascii_code)                  # 'a'
        str += char

    return str


def int2str(i, bits=16):
    """
    把一个整数转换成指定位数长度的二进制字符串，然后封装为普通字符串

    [bits=16]
    125 => 1111101   => 00000000 01111101 => chr(0) + chr(125)
    257 => 100000001 => 00000001 00000001 => chr(1) + chr(1)

    [bits=32]
    257 => 100000001 => 00000000 00000000 00000001 00000001 => chr(0) + chr(0) + chr(1) + chr(1)
    """
    return bits2str(int2bits(i, bits))
