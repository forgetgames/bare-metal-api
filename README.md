# Forget Games API

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![Project Backers](https://opencollective.com/forget-games/tiers/badge.svg)](https://opencollective.com/forget-games)

This application is to serve the available game actions with current bare metal contexts.

Requirements

* LinuxGSM
* OpenSSL
* Python3.11+
* poetry
* uvicorn
* docker
* devcontainers

## Gettings Started

```bash
# Create env vars and fill out your preferred values
cp .env.template .env

# Get application dependencies
poetry config virtualenvs.in-project true
poetry install

# Create certificates
openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem

# Run application
./start.sh
```

