#!/bin/bash

# Define the project root directory
ROOT_DIR=$(dirname $(dirname $(realpath $0)))

echo "[Unit]
Description=Runs a consumer of the rabbit MQ messages for all chat gpt responses processed

[Service]
ExecStart=${ROOT_DIR}/python/store_gpt_responses.py
User=dusty
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/store_gpt_responses.service


sudo chmod +x ${ROOT_DIR}/python/store_gpt_responses.py
sudo systemctl enable store_gpt_responses
sudo systemctl start store_gpt_responses

