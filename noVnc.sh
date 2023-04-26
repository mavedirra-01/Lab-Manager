#!/bin/bash

# Update the package list
sudo apt-get update

# Install noVNC and its dependencies
sudo apt-get install novnc websockify -y

# Create a self-signed SSL certificate
sudo openssl req -x509 -nodes -newkey rsa:2048 -keyout /etc/novnc/self.pem -out /etc/novnc/self.pem -days 3650 -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=www.example.com"

# Create a systemd service for noVNC
sudo tee /etc/systemd/system/novnc.service <<EOF
[Unit]
Description=noVNC Websocket Proxy
After=syslog.target network.target

[Service]
Type=simple
ExecStart=/usr/bin/websockify --web=/usr/share/novnc/ --cert=/etc/novnc/self.pem 6080 localhost:5900
Restart=always
User=novnc

[Install]
WantedBy=multi-user.target
EOF

# Start and enable the service
sudo systemctl daemon-reload
sudo systemctl start novnc
sudo systemctl enable novnc

echo "noVNC has been installed and configured. You can access it at https://<your-server-ip>:6080/vnc.html"