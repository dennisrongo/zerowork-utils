# How to Install ZeroWork on Ubuntu

This guide provides step-by-step instructions on how to execute the ZeroWork installation script on your Ubuntu VPS. This automated script will set up a complete desktop environment with Google Chrome and ZeroWork.

## Video Demonstration

For a visual walkthrough of this installation process, check out this [YouTube demonstration video](https://youtu.be/_uhx_y_ZvGM) which shows the entire process in action.

## Credit

This installation script is adapted from the original work by [DEPINspirationHUB](https://github.com/depinspirationhub/ubuntu-desktop/blob/main/ubuntu-desktop.sh). I've modified it specifically for ZeroWork installation while maintaining the core functionality.

## Running the Installation Script

### The Installation Command

Copy and paste the following command into your SSH terminal:

```bash
wget https://raw.githubusercontent.com/dennisrongo/zerowork-utils/refs/heads/master/ubuntu-chrome-zerowork-installation.sh && chmod +x ubuntu-chrome-zerowork-installation.sh && ./ubuntu-chrome-zerowork-installation.sh 1.1.60
```

### Understanding the Command

This command performs three actions in sequence:

1. `wget https://raw.githubusercontent.com/dennisrongo/zerowork-utils/refs/heads/master/ubuntu-chrome-zerowork-installation.sh`
   - Downloads the installation script from the GitHub repository

2. `chmod +x ubuntu-chrome-zerowork-installation.sh`
   - Makes the downloaded script executable (grants permission to run the script)

3. `./ubuntu-chrome-zerowork-installation.sh 1.1.60`
   - Executes the script with version 1.1.60 of ZeroWork as a parameter
   - You can replace "1.1.60" with a different version number if needed

## Installation Process Walkthrough

### 1. Disclaimer Acknowledgment

After running the command:

- A disclaimer will appear, explaining potential risks
- Type `y` and press Enter to agree and continue
- If you type anything else, the installation will abort

### 2. System Updates

- The script will update your system packages
- You'll see package lists being refreshed and upgrades being applied
- This may take several minutes depending on your system

### 3. Desktop Environment Installation

- XFCE desktop environment will be installed
- You'll see progress as packages are downloaded and configured

### 4. Remote Desktop Configuration

- XRDP (Remote Desktop Protocol) service is installed and configured
- The firewall is updated to allow RDP connections on port 3389

### 5. User Account Setup

- You'll be prompted to enter a new username for RDP login
- Type your desired username and press Enter
- You'll then be asked to create and confirm a password
  - The password won't be visible as you type (for security)
  - You must enter the same password twice

### 6. Application Installation

- Google Chrome will be downloaded and installed
- GDebi package manager will be installed for handling .deb files
- ZeroWork version 1.1.60 (or your specified version) will be downloaded and installed

### 7. Completion

- The script will display a completion message with connection details
- You'll be asked if you want to delete the installation script
  - Type `y` to remove it (recommended for security)
  - Type `n` to keep it

## Connecting to Your Desktop

After successful installation:

1. Use any RDP client software on your local computer
   - Windows: Built-in Remote Desktop Connection
   - Mac: Microsoft Remote Desktop from the App Store
   - Linux: Remmina or similar RDP client

2. Enter your VPS IP address as the connection address

3. When prompted, enter the username and password you created during installation

4. You should now see the XFCE desktop with Google Chrome and ZeroWork installed

## Troubleshooting Tips

- If connection fails, ensure port 3389 is open on your VPS firewall
- If login fails, double-check the username and password you created
- For VPS performance issues, ensure your server has at least 2GB of RAM

## Next Steps

Once connected to your desktop environment:

1. Launch Google Chrome from the Applications menu
2. Open ZeroWork from the Applications menu to begin using the software

The installation process is now complete, and your Ubuntu system is ready with ZeroWork installed.
