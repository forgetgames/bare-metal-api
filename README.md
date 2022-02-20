# Forget Games API

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![Project Backers](https://opencollective.com/forget-games/tiers/badge.svg)](https://opencollective.com/forget-games)

This application is to serve the available game actions with current bare metal contexts.

Requirements

* LinuxGSM
* OpenSSL
* Python3.6+
* pip 3
* uvicorn

## Gettings Started

```bash
# Create env vars and fill out your preferred values
cp .env.template .env

# Get application dependencies
pip install -r requirements.txt

# Create certificates
openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem

# Run application
python3 -m uvicorn main:app --host 0.0.0.0 --ssl-keyfile key.pem --ssl-certfile certificate.pem --reload
```

