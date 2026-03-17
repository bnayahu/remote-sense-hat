# Installation Guide

This guide will walk you through installing and configuring the Remote Sense HAT control system.

## Prerequisites

### Raspberry Pi Requirements
- Raspberry Pi (any model with GPIO pins)
- Sense HAT attached and working
- Raspberry Pi OS (Bullseye or newer recommended)
- Python 3.7 or higher
- Network connectivity (WiFi or Ethernet)

### Home Assistant Requirements
- Home Assistant OS, Core, Supervised, or Container
- Version 2023.1 or newer
- Access to the `custom_components` directory
- Network connectivity to Raspberry Pi

## Part 1: Raspberry Pi Setup

### Step 1: Verify Sense HAT Installation

First, ensure your Sense HAT is properly connected and working:

```bash
# Test the Sense HAT
python3 -c "from sense_hat import SenseHat; s = SenseHat(); s.show_message('Test')"
```

If you see "Test" scrolling on the LED matrix, your Sense HAT is working correctly.

### Step 2: Install Python Dependencies

```bash
# Update package list
sudo apt update

# Install required Python packages
sudo pip3 install sense-hat websockets pyyaml

# Verify installation
python3 -c "import sense_hat, websockets, yaml; print('All dependencies installed')"
```

### Step 3: Create Installation Directory

```bash
# Create directory for the server
sudo mkdir -p /opt/sense-hat-server

# Set ownership (replace 'pi' with your username if different)
sudo chown -R pi:pi /opt/sense-hat-server
```

### Step 4: Copy Server Files

Copy all files from the `raspberry_pi/` directory to `/opt/sense-hat-server/`:

```bash
# If you have the files locally
cd /path/to/remote-sense-hat
sudo cp raspberry_pi/*.py /opt/sense-hat-server/
sudo cp raspberry_pi/config.yaml /opt/sense-hat-server/
sudo cp raspberry_pi/requirements.txt /opt/sense-hat-server/

# Set permissions
sudo chmod +x /opt/sense-hat-server/sense_hat_server.py
sudo chown -R pi:pi /opt/sense-hat-server
```

Or download directly from your repository:

```bash
cd /opt/sense-hat-server
# Download files using wget or git clone
```

### Step 5: Configure the Server

Edit the configuration file:

```bash
nano /opt/sense-hat-server/config.yaml
```

Key settings to adjust:

```yaml
server:
  host: "0.0.0.0"  # Listen on all interfaces
  port: 8765       # Default port (change if needed)

display:
  brightness: 0.5  # Adjust to your preference (0.0 - 1.0)
  rotation: 0      # Rotate display if needed (0, 90, 180, 270)

sensors:
  enabled: true
  update_interval: 60  # Seconds between updates
  temperature_offset: -5.0  # Calibrate temperature (Sense HAT runs warm)
```

**Important:** Calibrate the temperature offset:
1. Place a reference thermometer near your Raspberry Pi
2. Wait 30 minutes for stabilization
3. Compare readings and adjust `temperature_offset`

### Step 6: Test the Server

Run the server manually to test:

```bash
cd /opt/sense-hat-server
python3 sense_hat_server.py
```

You should see:
```
INFO - Sense HAT server initialized
INFO - Starting WebSocket server on 0.0.0.0:8765
INFO - Server started successfully
```

Press `Ctrl+C` to stop the test.

### Step 7: Install Systemd Service

Install the service for automatic startup:

```bash
# Copy service file
sudo cp /opt/sense-hat-server/sense-hat-server.service /etc/systemd/system/

# Or create it manually
sudo nano /etc/systemd/system/sense-hat-server.service
```

Reload systemd and enable the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable sense-hat-server

# Start the service
sudo systemctl start sense-hat-server

# Check status
sudo systemctl status sense-hat-server
```

You should see "active (running)" in green.

### Step 8: Configure Firewall (if enabled)

If you have a firewall enabled, allow the WebSocket port:

```bash
# For UFW
sudo ufw allow 8765/tcp

# For iptables
sudo iptables -A INPUT -p tcp --dport 8765 -j ACCEPT
sudo iptables-save | sudo tee /etc/iptables/rules.v4
```

### Step 9: Find Your Raspberry Pi's IP Address

```bash
hostname -I
```

Note this IP address - you'll need it for Home Assistant configuration.

## Part 2: Home Assistant Setup

### Step 1: Access Custom Components Directory

The location depends on your Home Assistant installation:

- **Home Assistant OS/Supervised**: `/config/custom_components/`
- **Home Assistant Core**: `~/.homeassistant/custom_components/`
- **Home Assistant Container**: `/path/to/config/custom_components/`

### Step 2: Copy Custom Component

```bash
# Navigate to your Home Assistant config directory
cd /config  # or your config path

# Create custom_components directory if it doesn't exist
mkdir -p custom_components

# Copy the integration
cp -r /path/to/remote-sense-hat/home_assistant/custom_components/remote_sense_hat custom_components/
```

Or using SFTP/SCP from your computer:

```bash
scp -r home_assistant/custom_components/remote_sense_hat user@homeassistant:/config/custom_components/
```

### Step 3: Verify File Structure

Ensure the structure looks like this:

```
/config/custom_components/remote_sense_hat/
├── __init__.py
├── config_flow.py
├── const.py
├── manifest.json
├── sensor.py
├── services.yaml
└── strings.json
```

### Step 4: Restart Home Assistant

Restart Home Assistant to load the custom component:

- **UI Method**: Settings → System → Restart
- **CLI Method**: `ha core restart`
- **Docker**: `docker restart homeassistant`

### Step 5: Add the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration** (bottom right)
3. Search for "Remote Sense HAT"
4. Click on it to start configuration

### Step 6: Configure Connection

Enter your Raspberry Pi details:
- **Raspberry Pi IP Address**: The IP you noted earlier (e.g., `192.168.1.50`)
- **WebSocket Port**: `8765` (or your custom port)

Click **Submit**.

### Step 7: Verify Connection

If successful, you should see:
- A new device: "Sense HAT"
- Three sensor entities:
  - `sensor.sense_hat_temperature`
  - `sensor.sense_hat_humidity`
  - `sensor.sense_hat_pressure`

### Step 8: Test Services

Go to **Developer Tools** → **Services** and test:

```yaml
service: remote_sense_hat.display_text
data:
  text: "Hello from Home Assistant!"
  text_color: [0, 255, 0]
```

You should see the text scroll on your Sense HAT display!

## Troubleshooting

### Raspberry Pi Issues

#### Server won't start
```bash
# Check logs
sudo journalctl -u sense-hat-server -f

# Check if port is in use
sudo netstat -tulpn | grep 8765

# Test Sense HAT directly
python3 -c "from sense_hat import SenseHat; s = SenseHat(); s.show_message('Test')"
```

#### Permission errors
```bash
# Fix ownership
sudo chown -R pi:pi /opt/sense-hat-server

# Fix permissions
sudo chmod +x /opt/sense-hat-server/sense_hat_server.py
```

#### Service fails to start
```bash
# Check service status
sudo systemctl status sense-hat-server

# View detailed logs
sudo journalctl -u sense-hat-server -n 50

# Restart service
sudo systemctl restart sense-hat-server
```

### Home Assistant Issues

#### Integration not found
1. Verify files are in correct location
2. Check file permissions
3. Restart Home Assistant
4. Check logs: Settings → System → Logs

#### Cannot connect to server
1. Verify Raspberry Pi IP address
2. Check if server is running: `sudo systemctl status sense-hat-server`
3. Test connection: `telnet <raspberry-pi-ip> 8765`
4. Check firewall settings
5. Ensure both devices are on same network

#### Sensor entities not updating
1. Check Home Assistant logs
2. Verify sensor configuration in `config.yaml`
3. Force update: Call `remote_sense_hat.update_sensors` service
4. Check Raspberry Pi logs for sensor errors

### Network Issues

#### Connection timeout
```bash
# From Home Assistant machine, test connectivity
ping <raspberry-pi-ip>

# Test WebSocket connection
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: test" \
  http://<raspberry-pi-ip>:8765
```

#### Firewall blocking
```bash
# On Raspberry Pi, check firewall status
sudo ufw status

# Allow port if needed
sudo ufw allow 8765/tcp
```

## Verification Checklist

- [ ] Sense HAT displays test message
- [ ] Python dependencies installed
- [ ] Server files copied to `/opt/sense-hat-server/`
- [ ] Configuration file edited and saved
- [ ] Server runs manually without errors
- [ ] Systemd service enabled and running
- [ ] Raspberry Pi IP address noted
- [ ] Custom component copied to Home Assistant
- [ ] Home Assistant restarted
- [ ] Integration added successfully
- [ ] Sensor entities visible and updating
- [ ] Test service call works
- [ ] Display shows text from Home Assistant

## Next Steps

Once installation is complete:

1. **Calibrate Temperature**: Adjust `temperature_offset` in config.yaml
2. **Create Automations**: See [examples.md](examples.md) for ideas
3. **Add to Dashboard**: Create cards for sensors and controls
4. **Explore Services**: Try different display commands
5. **Monitor Logs**: Keep an eye on logs for any issues

## Updating

### Update Raspberry Pi Server

```bash
# Stop service
sudo systemctl stop sense-hat-server

# Backup config
cp /opt/sense-hat-server/config.yaml ~/config.yaml.backup

# Update files
cd /opt/sense-hat-server
# Copy new files or git pull

# Restore config if needed
cp ~/config.yaml.backup /opt/sense-hat-server/config.yaml

# Restart service
sudo systemctl start sense-hat-server
```

### Update Home Assistant Component

```bash
# Stop Home Assistant (if using Core)
# Update files
cd /config/custom_components/remote_sense_hat
# Copy new files or git pull

# Restart Home Assistant
```

## Uninstallation

### Remove from Raspberry Pi

```bash
# Stop and disable service
sudo systemctl stop sense-hat-server
sudo systemctl disable sense-hat-server

# Remove service file
sudo rm /etc/systemd/system/sense-hat-server.service
sudo systemctl daemon-reload

# Remove server files
sudo rm -rf /opt/sense-hat-server
```

### Remove from Home Assistant

1. Remove integration: Settings → Devices & Services → Remote Sense HAT → Delete
2. Remove files: `rm -rf /config/custom_components/remote_sense_hat`
3. Restart Home Assistant

## Support

For issues and questions:
- Check the [troubleshooting section](#troubleshooting)
- Review logs on both systems
- Consult the [architecture documentation](architecture.md)
- Check the [examples](examples.md) for usage patterns