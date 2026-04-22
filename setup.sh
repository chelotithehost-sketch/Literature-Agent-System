#!/bin/bash
set -e

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
mkdir -p data/checkpoints data/output logs

# Install pandoc for exports
sudo apt update
sudo apt install -y pandoc texlive-xetex

# Setup systemd service (optional)
sudo cp literature_agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable literature_agent
echo "Setup complete. Start service with: sudo systemctl start literature_agent"
