#!/bin/bash

# Set default ZeroWork version
ZEROWORK_VERSION="${1:-1.1.66}"

# Disclaimer
echo "************************************************************"
echo "* DISCLAIMER:                                              *"
echo "* This script is created by DEPINspirationHUB and is      *"
echo "* partially AI-generated. It is provided AS-IS without    *"
echo "* any warranties or guarantees. Use at your own risk.     *"
echo "* The developers will not be held liable for any issues,  *"
echo "* damages, or losses caused by running this script.       *"
echo "*                                                          *"
echo "* This script has been modified by Dennis (codingmenace)  *"
echo "* to include ZeroWork agent installation.                  *"
echo "************************************************************"

# Prompt user to agree to the disclaimer
read -p "Do you agree to proceed? (y/n): " AGREEMENT

# Check user input
if [[ "$AGREEMENT" != "y" ]]; then
    echo "You have declined the agreement. Exiting script."
    echo "Installation aborted. You can rerun the script anytime to proceed."
    
    # Prompt to delete the script file
    read -p "Do you want to delete the downloaded script file (ubuntu-desktop.sh)? (y/n): " DELETE_FILE
    if [[ "$DELETE_FILE" == "y" ]]; then
        SCRIPT_PATH="$(realpath "$0")"
        rm -- "$SCRIPT_PATH"
        echo "Script file deleted."
    else
        echo "Script file retained."
    fi
    
    exit 1
fi

# Proceeding with the setup...

echo "Updating and upgrading system..."
sudo apt update && sudo apt upgrade -y

echo "Installing XFCE Desktop..."
sudo apt install xfce4 xfce4-goodies -y

echo "Installing XRDP for Remote Desktop Access..."
sudo apt install xrdp -y
sudo systemctl enable xrdp
sudo systemctl start xrdp

echo "Configuring XRDP to use XFCE..."
echo "startxfce4" | sudo tee /etc/skel/.xsession
sudo systemctl restart xrdp

echo "Allowing RDP port through firewall..."
sudo ufw allow 3389/tcp
sudo ufw enable -y

echo "Creating a new user for RDP login..."
read -p "Enter a new username for RDP: " new_user
sudo useradd -m -s /bin/bash $new_user

# Ensure password confirmation matches before proceeding
while true; do
    read -s -p "Enter a password for $new_user: " password
    echo
    read -s -p "Retype the password: " password_confirm
    echo
    if [[ "$password" == "$password_confirm" ]]; then
        echo "$new_user:$password" | sudo chpasswd
        break
    else
        echo "Passwords do not match. Please try again."
    fi
done

echo "Granting the new user sudo privileges..."
sudo usermod -aG sudo $new_user

echo "Installing Google Chrome..."
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb -y

echo "Modifying Chrome launcher to use --no-sandbox..."
sudo sed -i 's|Exec=/usr/bin/google-chrome-stable %U|Exec=/usr/bin/google-chrome-stable %U|' /usr/share/applications/google-chrome.desktop

echo "Installing GDebi for easy .deb installations..."
sudo apt install gdebi -y

echo "Setting GDebi as default for .deb files..."
xdg-mime default gdebi.desktop application/vnd.debian.binary-package

echo "Installing ZeroWork version $ZEROWORK_VERSION..."
wget "https://zerowork-agent-releases.s3.amazonaws.com/public/linux/ZeroWork-$ZEROWORK_VERSION.deb"
sudo apt install "./ZeroWork-$ZEROWORK_VERSION.deb" -y

echo "Installing Xvfb for headless ZeroWork agent..."
sudo apt install xvfb x11-utils -y

if [ ! -x /opt/ZeroWork/zerowork ]; then
    echo "Error: /opt/ZeroWork/zerowork is missing or not executable."
    exit 1
fi

echo "Writing ZeroWork agent start wrapper..."
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

echo "Writing ZeroWork systemd service..."
sudo tee /etc/systemd/system/zerowork.service > /dev/null <<EOF
[Unit]
Description=ZeroWork desktop agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$new_user
Group=$new_user
Environment=DISPLAY=:99
Environment=HOME=/home/$new_user
WorkingDirectory=/home/$new_user
ExecStart=/usr/local/bin/zerowork-agent-start.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo chmod +x /usr/local/bin/zerowork-agent-start.sh

echo "Enabling and starting ZeroWork agent service..."
sudo systemctl daemon-reload
sudo systemctl enable zerowork.service
if ! sudo systemctl start zerowork.service; then
    echo "Error: Failed to start zerowork.service"
    sudo systemctl status zerowork.service --no-pager || true
    sudo journalctl -u zerowork.service -n 50 --no-pager || true
    exit 1
fi

echo "ZeroWork agent is enabled on boot."

echo "Restarting XRDP service..."
sudo systemctl restart xrdp

echo "Installation complete! You can now connect via RDP."
echo "Use the following credentials:"
echo "Username: $new_user"
echo "Password: (You set this during installation)"
echo "RDP Address: Use your VPS IP address."
echo "ZeroWork version $ZEROWORK_VERSION has been installed."
echo "The ZeroWork agent is enabled as systemd service zerowork and starts on boot."
echo "Check it with: sudo systemctl status zerowork"

# Prompt to delete the script file
read -p "Do you want to delete the downloaded script file (ubuntu-desktop.sh)? (y/n): " DELETE_FILE
if [[ "$DELETE_FILE" == "y" ]]; then
    SCRIPT_PATH="$(realpath "$0")"
    rm -- "$SCRIPT_PATH"
    echo "Script file deleted."
else
    echo "Script file retained."
fi
