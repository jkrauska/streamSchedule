#!/bin/bash


set -euo pipefail


# certbot renew --post-hook "/path/to/your/script.sh"

CERTDIR=/home/stream411/streamSchedule/certs/
cp /etc/letsencrypt/live/*/fullchain.pem $CERTDIR
cp /etc/letsencrypt/live/*/privkey.pem $CERTDIR
chown stream411:stream411 $CERTDIR/*.pem
chmod 600 $CERTDIR/*.pem
