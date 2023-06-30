#!/bin/bash

set -o allexport
source .env
set +o allexport
export PATH=$PATH:/workspaces/bare-metal-api/.venv/bin
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out certificate.pem -sha256 -days 3650 -nodes -subj "/C=CA/ST=BC/L=V/O=ForgetGames/OU=Hosting/CN=forgetgames.com"
uvicorn apps.server_manager.main:app --host 0.0.0.0 --port 3131 --ssl-keyfile key.pem --ssl-certfile certificate.pem --reload

