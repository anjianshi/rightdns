# -*- coding: utf-8 -*-

# 是否以调试模式运行（会输出更多信息）
debug = False

# rightdns 监听的端口
port = 5302

# 本地渠道的 DNS 服务器（必填）
# 默认设置的是 DNSPOD 的 public DNS
normal_dns_ip = "119.29.29.29"
normal_dns_port = 53

# 是否使用 Google 的 DNS-Over-HTTPS 来获取安全的解析结果。建议在翻墙网络不支持转发 UDP 请求时开启。
use_https_dns = False

# 安全渠道的 DNS 服务器，use_https_dns 为 False 时必填
safe_dns_ip = "8.8.8.8"
safe_dns_port = 53

# Google DNS-Over-HTTPS 相关配置，use_https_dns 为 True 时必填
# dns.google.com 域名的 IP 地址
dns_google_com_ip = "216.58.196.238"
# 此工具会在内部另建一个代理 Google HTTPS DNS 服务的 DNS 服务器，需要给它也指定一个端口
google_proxy_port = 5033

# 伪造渠道的 IP 地址
fake_dns_ip = '8.8.8.9'

# 等待伪造渠道返回结果的毫秒数。如果超过此时长还没收到伪造渠道的返回结果，即视为此域名没有通过此方式被污染。
# 此值越小，对 DNS 解析速度的影响越小，但是把被污染的域名误判为没被污染的可能性也越高。
# 可以在本地运行几次 `dig @8.8.8.9 google.com`，看看大约多少毫秒能够收到被污染的结果，相应地调整此数值。
fake_response_delay = 100

# 处理单个解析请求的最大毫秒数，如果超过这个时限还没能完成解析，则抛弃此次请求
# 设为 -1 或 0 则为不限制（非常不建议这样做）
resolve_timeout = 3000

# 缓存最近的多少条解析结果，设为 0 则不开启缓存
# 开启缓存后会无视 DNS 结果里的 TTL，在工具运行期间一直使用缓存了的值
max_cache_len = 0

# 日志文件地址。设为 None 即不记录日志（在路由器等存储空间较小的设备上不建议记录日志，万一把空间占满了会比较麻烦）
log_path = None
# 日志文件的缓冲区大小
log_buffer_size = 2048
