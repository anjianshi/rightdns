返回正确的 DNS 解析结果，且不影响普通域名的解析（例如对于国内的网站不会解析到国外的线路）

## 环境要求
Python 2.7
若在 openwrt 下运行，需安装 python-light 包

## 使用方法
在 blocked_domains.txt 中列出希望使用国外 DNS 来解析的域名的正则表达式，
每行一个表达式，空行和以 "#" 开头的行会被忽略

然后执行 start.sh 即可

## 相关资料

socket(TCP) 相关教程：
https://docs.python.org/2/howto/sockets.html
http://openexperience.iteye.com/blog/145701

udp 相关教程：
http://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb493182103fac9270762a000/0013868325264457324691c860044c5916ce11b305cb814000

DNS 流程说明： http://blog.csdn.net/crazw/article/details/8986504
DNS 报文格式： http://blog.csdn.net/tigerjibo/article/details/6827736
