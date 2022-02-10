#!/bin/bash

set -e

 # install wkhtmltopdf
wget -O /tmp/wkhtmltox.tar.xz https://github.com/frappe/wkhtmltopdf/raw/master/wkhtmltox-0.12.3_linux-generic-amd64.tar.xz
tar -xf /tmp/wkhtmltox.tar.xz -C /tmp
sudo mv /tmp/wkhtmltox/bin/wkhtmltopdf /usr/local/bin/wkhtmltopdf
sudo chmod o+x /usr/local/bin/wkhtmltopdf

# install cups
sudo apt-get install libcups2-dev

if [ "$TYPE" == "ui" ]; then
    # install redis
    sudo apt-get install redis-server
fi
