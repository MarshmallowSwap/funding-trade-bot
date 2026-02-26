#!/bin/bash

cd /root/funding-trade-bot
git pull
source venv/bin/activate
pip install -r requirements.txt
systemctl restart fundingbot
echo "Deploy completato!"
