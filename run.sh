#!/bin/bash

source .venv/bin/activate

if ! test -f certs/fullchain.pem; then
  echo "ERROR: Cert File DOES NOT EXIST."
  exit 1
fi

if ! test -f secrets.json; then
  echo "ERROR: secrets.json DOES NOT EXIST."
  exit 1
fi


# SSL Server
# NOTE: Lazy Apps is necessary for APScheduler
uwsgi --master \
    --https 0.0.0.0:8443,certs/fullchain.pem,certs/privkey.pem \
    --enable-threads \
    --lazy-apps \
    --wsgi main:app 
