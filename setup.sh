#!/bin/bash

# installation script for Reticulum PiZero Monitor
#  works with the st7789 displays from Pimoroni

set -e

echo "=================================="
echo "    Reticulum Pi Monitor Setup    "
echo "=================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
   echo "Please run as regular user (not root)"
   exit 1
fi

echo "Installing system packages..."
sudo apt update
sudo apt install -y python3-pip python3-dev python3-pil lsof

echo "Installing Python requirements..."
pip3 install --user --break-system-packages -r requirements.txt

echo "Adding user to required groups..."
sudo usermod -a -G gpio,spi,dialout $USER

# Get current user info for systemd service
CURRENT_USER=$(whoami)
CURRENT_HOME=$(eval echo ~$CURRENT_USER)
INSTALL_DIR=$(pwd)

echo "Setting up systemd service for user: $CURRENT_USER"
echo "Home directory: $CURRENT_HOME"
echo "Install directory: $INSTALL_DIR"

# Create rnsd service
echo "Installing rnsd systemd service..."
sudo tee /etc/systemd/system/rnsd.service > /dev/null << EOF
[Unit]
Description=Reticulum Network Stack Daemon
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_HOME
ExecStart=$CURRENT_HOME/.local/bin/rnsd --verbose
Restart=always
RestartSec=10
Environment="HOME=$CURRENT_HOME"
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create display monitor service
echo "Installing reticulum-monitor systemd service..."
sudo tee /etc/systemd/system/reticulum-monitor.service > /dev/null << EOF
[Unit]
Description=Reticulum Pi Monitor Display
After=network.target rnsd.service

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/main.py
Restart=always
RestartSec=5
SupplementaryGroups=gpio spi dialout
Environment="HOME=$CURRENT_HOME"
Environment="PYTHONPATH=$INSTALL_DIR"
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "Enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable rnsd
sudo systemctl enable reticulum-monitor

echo "==================================="
echo "      Setup complete! Please        "
echo "       reboot your device           "
echo "==================================="
