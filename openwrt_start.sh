killall python          # 危险！
python ./dns.py > /dev/null &
/etc/init.d/dnsmasq restart     # 清除原来的可能错误的 DNS 缓存
