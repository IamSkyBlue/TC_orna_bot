#!/bin/bash
echo "${GOOGLE_CREDENTIALS}" > client_secret.json
python -u bot.py