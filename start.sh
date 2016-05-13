killall python
python ./dns.py > /dev/null &
/etc/init.d/dnsmasq restart
