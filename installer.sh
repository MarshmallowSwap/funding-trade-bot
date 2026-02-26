#!/bin/bash

echo "=== Funding Bot Installer ==="

REPO_URL="https://github.com/TUO_USERNAME/funding-trade-bot.git"
INSTALL_DIR="/root/funding-trade-bot"
SERVICE_FILE="/etc/systemd/system/fundingbot.service"

apt update -y && apt install -y python3 python3-venv python3-pip git

if [ -d "$INSTALL_DIR" ]; then
    cd "$INSTALL_DIR"
    git pull
else
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "⚠️  File .env mancante!"
    exit 1
fi

cat > $SERVICE_FILE <<EOF
[Unit]
Description=Funding Trade Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/bot.py
Restart=always
RestartSec=5
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable fundingbot
systemctl restart fundingbot

systemctl status fundingbot --no-pager
