判断一个域名是否被污染，若被污染，使用安全渠道（如国外的 DNS）进行解析；若未被污染，使用本地渠道（如 ISP 提供的 DNS）进行解析。
以此解决访问部分国内网站被引到国外线路的问题。

使用此工具的前提条件是本机已经能够获取到正确（但可能不适合本地线路）的 DNS 解析结果。  
获取正确解析结果可能的方法有：
1. 使用支持非 53 端口的国外 DNS（可以自己搭建）
2. 通过 VPN 等手段连接 DNS 服务器
3. 使用一个能够解决 DNS 污染的工具，如 DNSCrypt、Pcap_DNSProxy、Tcp-DNS-proxy

## 名词说明
本地渠道：解析未被污染的域名的渠道，能返回适合本地线路的解析结果
安全渠道：解析被污染的域名的渠道
伪造渠道：一个并没有提供 DNS 服务的国外 IP 地址，用来初步检测一个域名是否被污染

## 判断规则（符合任意一条规则视为被污染）
1. 域名与白名单匹配
2. 向伪造渠道发起请求并获得了解析结果
3. 向安全渠道发起请求，获得的解析结果中的 CNAME 记录与白名单匹配
4. 向本地渠道发起请求，获得的解析结果中的 CNAME 记录与白名单匹配

## 环境要求
本地能够运行 Python 2.7  
若在 OpenWrt 下运行，需安装 python-light 包  

## 使用方法
把 config.default.py 复制一份，更名为 config.py，修改其中的参数值  
执行 `python rightdns.py`，现在此脚本就成了一个运行在指定端口上的 DNS 服务  
接下来只要把本机的 DNS 请求指向它即可  

## 鸣谢
daemon.py 来自 https://github.com/serverdensity/python-daemon

## 相关资料
### socket(TCP) 相关教程
https://docs.python.org/2/howto/sockets.html  
http://openexperience.iteye.com/blog/145701

### udp 相关教程
http://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb493182103fac9270762a000/0013868325264457324691c860044c5916ce11b305cb814000  

### DNS 基本概念
DNS 流程说明： http://blog.csdn.net/crazw/article/details/8986504  
DNS 报文格式： http://blog.csdn.net/tigerjibo/article/details/6827736  

### 关于 DNS 污染
https://www.zhihu.com/question/19751271  
https://program-think.blogspot.com/2014/01/dns.html  
http://gfwrev.blogspot.jp/2009/11/gfwdns.html  
