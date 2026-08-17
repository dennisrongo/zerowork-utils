# zerowork-utils

Ubuntu VPS installer: XFCE, Chrome, and the ZeroWork agent as a systemd service.

Agent skills (TaskBot builder, ZeroWork → Playwright, n8n) live in the private repo **automation-skills**.

[YouTube demo](https://youtu.be/_uhx_y_ZvGM). Adapted from [DEPINspirationHUB](https://github.com/depinspirationhub/ubuntu-desktop/blob/main/ubuntu-desktop.sh); Dennis modified it for ZeroWork.

## Install

```bash
wget https://raw.githubusercontent.com/dennisrongo/zerowork-utils/refs/heads/master/ubuntu-chrome-zerowork-installation.sh && chmod +x ubuntu-chrome-zerowork-installation.sh && ./ubuntu-chrome-zerowork-installation.sh 1.1.66
```

Swap `1.1.66` for another agent version if needed. Type `y` on the disclaimer, then create an RDP username and password (typed twice, hidden).

## What you get

- System update
- XFCE
- XRDP on 3389, enabled on boot
- Google Chrome
- ZeroWork agent (version you pass)
- Xvfb + systemd service `zerowork` so the agent starts on boot and restarts after a crash

## After install

RDP to the VPS IP with the user you created (Windows Remote Desktop, Mac Microsoft Remote Desktop, Linux Remmina).

The agent is already running. Do not launch a second copy from Applications. The tray icon will not appear in RDP (virtual display :99). Expected.

```bash
sudo systemctl status zerowork
journalctl -u zerowork -f
curl http://localhost:9990
```

`curl` should return the agent-is-running message.

## Existing VPS

Do not re-run the full installer (it creates another user). Use this instead (replace the username):

```bash
EXISTING_USER="your-rdp-user"

sudo apt install xvfb x11-utils -y

sudo tee /usr/local/bin/zerowork-agent-start.sh > /dev/null <<'EOF'
#!/bin/bash
export DISPLAY=:99
if ! xdpyinfo -display :99 >/dev/null 2>&1; then
    Xvfb :99 -screen 0 1440x900x24 -ac +extension GLX +render -noreset &
fi
for i in $(seq 1 20); do
    if xdpyinfo -display :99 >/dev/null 2>&1; then
        break
    fi
    sleep 0.5
done
if ! xdpyinfo -display :99 >/dev/null 2>&1; then
    echo "Error: Xvfb display :99 did not become ready."
    exit 1
fi
exec /opt/ZeroWork/zerowork --no-sandbox
EOF

sudo chmod +x /usr/local/bin/zerowork-agent-start.sh

sudo tee /etc/systemd/system/zerowork.service > /dev/null <<EOF
[Unit]
Description=ZeroWork desktop agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$EXISTING_USER
Group=$EXISTING_USER
Environment=DISPLAY=:99
Environment=HOME=/home/$EXISTING_USER
WorkingDirectory=/home/$EXISTING_USER
ExecStart=/usr/local/bin/zerowork-agent-start.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now zerowork.service
```

## Troubleshooting

- RDP fail: port 3389
- Login fail: username/password
- VPS: at least 2GB RAM
- Agent down: `systemctl status` / `journalctl`
