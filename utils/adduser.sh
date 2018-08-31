#!/bin/bash

user=$1
pass=$2
sed -i "/^$user:/d" /proxydata/proxy.pass
printf "$user:$(openssl passwd -apr1 $pass)\n" >>/proxydata/proxy.pass

echo https://$user:$pass@$HOSTNAME.vhost38.genap.ca/galaxy
