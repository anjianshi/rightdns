解决使用国外 DNS 服务器时，部分国内网站会解析到国外线路影响访问的问题。  

使用此工具的前提条件是本机能够获取到正确的 DNS 解析结果。  
首先，要有一台能够获取到提供正确结果的 DNS 服务器，例如 Google DNS， OpenDNS，或者自己架设的国外 DNS  
其次，还要保证从本地到目标服务器的解析请求不会被抢断（详间最下面`相关资料`）。  
可能的方法有：  

1. 通过 VPN 等工具连接 DNS 服务器
2. 使用一个支持非 53 端口的 DNS 服务器
3. 以 TCP 而不是 UDP 的方式获取 DNS 解析结果（例如利用 [Tcp-DNS-proxy](https://github.com/henices/Tcp-DNS-proxy) 工具）

在此前提下，此工具能判断出哪些域名是被污染了的，哪些是正常的。  
对于正常的域名，使用普通的 DNS 服务器（例如本地 ISP 提供的服务器，或是阿里 DNS 之类的公共 DNS），以保证解析出来的线路与本地网络环境匹配；  
对于确定被污染了的域名，才使用安全 DNS，以保证获得正确的结果。  


## 原理
当我们向一个国外的 DNS 服务器发起解析请求时，DNS 污染的运作方式是在正确的解析结果返回前，抢先返回一个错误的结果。  
它不关心后面的正确的结果是什么，甚至不关心后面是不是会返回一个结果。  

因此，对于任意一个域名，我们只要向一个肯定得不到解析结果的国外 IP 发起请求，如果得到了响应，它就是被污染的；如果没有响应，说明没有被污染。  
进而得知应该用哪个 DNS 服务器进行实际的解析。  

这样做会导致域名解析时间变长，因此可以考虑加长本地的 DNS 缓存时间。  


## 环境要求
本地能够运行 Python 2.7  
若在 openwrt 下运行，需安装 python-light 包  


## 使用方法
把 config.default.py 复制一份，更名为 config.py  
修改其中的参数值  
然后执行 `python dns.py`，现在此脚本就成了一个运行在指定端口上的 DNS 服务  
接下来只要把本机的 DNS 请求指向它即可  


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
