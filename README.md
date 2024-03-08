
# Service Status Monitor

## Description
This program is designed to monitor the status of various hosts (IP addresses or domains) by periodically pinging them. It provides a web interface for users to add, monitor, and remove hosts dynamically. The system supports notification via Discord webhook when the status of a host changes. This version is the latest stable release, but more versions with additional options and enhanced reliability are currently in development.

## Installation

### Requirements
- Python 3.6 or higher
- Flask
- Requests library for Python

### Setup on Linux

1. **Install Python3**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```

2. **Install Flask**:
   ```bash
   pip3 install Flask
   ```

3. **Install Requests**:
   ```bash
   pip3 install requests
   ```

### Setup on Windows

1. **Install Python3**:
   - Download and install Python from the [official website](https://www.python.org/). Ensure to check the box 'Add Python to PATH' during installation.

2. **Install Flask**:
   ```cmd
   pip install Flask
   ```

3. **Install Requests**:
   ```cmd
   pip install requests
   ```

## Usage

1. **Start the Server**:
   - On Linux: `python3 app.py`
   - On Windows: `python app.py`

2. **Accessing the Web Interface**:
   - Open a browser and navigate to `http://localhost:5000` or `http://ip-server:5000`to access the user interface.

3. **Add a Host**:
   - Use the form on the page to add a new host by entering its IP address or domain name, optional label, and whether to enable notifications.

4. **Monitoring Hosts**:
   - The status of each host (OK or KO), response time, and other details will be displayed in the table on the web interface.

5. **Remove a Host**:
   - Click the 'Remove' button next to the host you wish to remove.

6. **Toggle Notifications**:
   - Click the 'Notifications: ON/OFF' button to toggle notification settings for each host.

## Support
For any questions or support, please contact "Kali" on Discord at "kalienclaquettes" or visit the GitHub repository at https://github.com/Kali3159 for more information.
