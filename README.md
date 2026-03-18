# Remote Sense HAT Control

Control your Raspberry Pi Sense HAT 8x8 LED display remotely from Home Assistant using WebSocket communication.

## Overview

This project provides a complete solution for controlling a Raspberry Pi Sense HAT display from Home Assistant running on a separate machine. It uses WebSocket for real-time, bidirectional communication and supports full control over the LED matrix including text scrolling, pixel manipulation, and custom animations.

## Features

- 🔌 **WebSocket Communication**: Real-time, low-latency control
- 💡 **Light Entity**: Control LED matrix as a native Home Assistant light
- 📝 **Text Display**: Scroll text messages with customizable colors and speed
- 🎨 **Pixel Control**: Set individual pixels or entire display patterns
- 🖼️ **Image Library**: Display predefined icons and patterns
- 🌡️ **Sensor Integration**: Temperature, humidity, and pressure sensors
- 🔄 **Auto-Reconnect**: Automatic reconnection on network issues
- ⚙️ **Easy Configuration**: UI-based setup in Home Assistant
- 🚀 **Auto-Start**: Systemd service for automatic startup on boot
- 🎭 **Animation Support**: Queue and manage display animations

## Architecture

```
┌─────────────────────┐         WebSocket          ┌──────────────────────┐
│  Home Assistant     │◄──────────────────────────►│  Raspberry Pi        │
│  Custom Component   │      (Port 8765)           │  WebSocket Server    │
└─────────────────────┘                            └──────────────────────┘
         │                                                    │
         │                                                    │
         ▼                                                    ▼
┌─────────────────────┐                            ┌──────────────────────┐
│  Services & UI      │                            │  Sense HAT Library   │
│  - display_text     │                            │  - LED Control       │
│  - set_pixel        │                            │  - 8x8 Matrix        │
│  - show_image       │                            │  - Animations        │
│  - Sensor Entities  │                            │  - Sensors           │
└─────────────────────┘                            └──────────────────────┘
```

## Entities

### Light Entity: LED Matrix

The 8x8 LED matrix is exposed as a native Home Assistant light entity (`light.sense_hat_led_matrix`), providing:

- **On/Off Control**: Turn the display on or off
- **Brightness**: Adjust display brightness (0-100%)
- **RGB Color**: Set solid colors across the entire display
- **Effects**: Display predefined images/patterns (heart, smile, check, cross, arrows)

**Example Usage:**
```yaml
# Turn on with a solid blue color
service: light.turn_on
target:
  entity_id: light.sense_hat_led_matrix
data:
  brightness: 200
  rgb_color: [0, 0, 255]

# Show a heart effect
service: light.turn_on
target:
  entity_id: light.sense_hat_led_matrix
data:
  effect: "heart"
```

### Sensor Entities

The Sense HAT includes environmental sensors that are automatically exposed to Home Assistant:

- **Temperature**: Ambient temperature in °C (with calibration offset)
- **Humidity**: Relative humidity percentage
- **Pressure**: Atmospheric pressure in hPa

These sensors update automatically and can be used in automations, displayed on dashboards, or shown on the LED matrix.

## Quick Start

### Prerequisites

**Raspberry Pi:**
- Raspberry Pi with Sense HAT attached
- Raspberry Pi OS installed
- Python 3.7 or higher
- Network connectivity

**Home Assistant:**
- Home Assistant OS (or Core/Supervised)
- Access to custom_components directory
- Network connectivity to Raspberry Pi

### Installation

#### 1. Raspberry Pi Setup

```bash
# Install required Python packages
sudo pip3 install sense-hat websockets pyyaml

# Create installation directory
sudo mkdir -p /opt/sense-hat-server

# Copy server files (after implementation)
sudo cp raspberry_pi/* /opt/sense-hat-server/

# Install and enable systemd service
sudo cp raspberry_pi/sense-hat-server.service /etc/systemd/system/
sudo systemctl enable sense-hat-server
sudo systemctl start sense-hat-server

# Check status
sudo systemctl status sense-hat-server
```

#### 2. Home Assistant Setup

```bash
# Navigate to Home Assistant config directory
cd /config

# Create custom_components directory if it doesn't exist
mkdir -p custom_components

# Copy the custom component (after implementation)
cp -r home_assistant/custom_components/remote_sense_hat custom_components/

# Restart Home Assistant
# (Use UI or: ha core restart)
```

#### 3. Configuration

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Remote Sense HAT"
4. Enter your Raspberry Pi's IP address and port (default: 8765)
5. Click **Submit**

## Usage Examples

### Using the Light Entity

The light entity provides simple, intuitive control for basic operations:

```yaml
# Turn on with default white color
service: light.turn_on
target:
  entity_id: light.sense_hat_led_matrix

# Set a specific color and brightness
service: light.turn_on
target:
  entity_id: light.sense_hat_led_matrix
data:
  brightness: 150
  rgb_color: [255, 100, 0]  # Orange

# Show a predefined effect
service: light.turn_on
target:
  entity_id: light.sense_hat_led_matrix
data:
  effect: "check"

# Turn off the display
service: light.turn_off
target:
  entity_id: light.sense_hat_led_matrix
```

### Using Services for Advanced Control

For more complex operations like scrolling text and pixel manipulation, use the dedicated services:

#### Display Text

```yaml
service: remote_sense_hat.display_text
data:
  text: "Hello World!"
  scroll_speed: 0.1
  text_color: [255, 0, 0]  # Red
  back_color: [0, 0, 0]    # Black
```

#### Set Individual Pixel

```yaml
service: remote_sense_hat.set_pixel
data:
  x: 3
  y: 4
  color: [0, 255, 0]  # Green
```

#### Clear Display

```yaml
service: remote_sense_hat.clear
data:
  color: [0, 0, 255]  # Blue background
```

#### Show Predefined Image

```yaml
service: remote_sense_hat.show_image
data:
  image_name: "heart"
  rotation: 0
```

### Automation Examples

#### Using Light Entity in Automation

```yaml
automation:
  - alias: "Notification Indicator"
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door
        to: "on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.sense_hat_led_matrix
        data:
          effect: "check"
          brightness: 255
      - delay: "00:00:03"
      - service: light.turn_off
        target:
          entity_id: light.sense_hat_led_matrix
```

#### Using Services in Automation

```yaml
automation:
  - alias: "Welcome Home Display"
    trigger:
      - platform: state
        entity_id: person.john
        to: "home"
    action:
      - service: remote_sense_hat.display_text
        data:
          text: "Welcome Home!"
          text_color: [0, 255, 0]
          scroll_speed: 0.08
```

## Project Structure

```
remote-sense-hat/
├── raspberry_pi/              # Raspberry Pi server code
│   ├── sense_hat_server.py
│   ├── display_controller.py
│   ├── config.yaml
│   ├── requirements.txt
│   └── sense-hat-server.service
├── home_assistant/            # Home Assistant integration
│   └── custom_components/
│       └── remote_sense_hat/
│           ├── __init__.py
│           ├── manifest.json
│           ├── config_flow.py
│           ├── const.py
│           ├── display.py
│           ├── services.yaml
│           └── strings.json
├── docs/                      # Documentation
│   ├── installation.md
│   ├── configuration.md
│   └── examples.md
├── PLAN.md                    # Detailed implementation plan
└── README.md                  # This file
```

## Services

### `remote_sense_hat.display_text`
Scroll text across the display.

**Parameters:**
- `text` (required): Text to display
- `scroll_speed` (optional): Speed in seconds (default: 0.1)
- `text_color` (optional): RGB array [r, g, b] (default: [255, 255, 255])
- `back_color` (optional): RGB array [r, g, b] (default: [0, 0, 0])

### `remote_sense_hat.set_pixel`
Set a single pixel color.

**Parameters:**
- `x` (required): X coordinate (0-7)
- `y` (required): Y coordinate (0-7)
- `color` (required): RGB array [r, g, b]

### `remote_sense_hat.set_pixels`
Set all 64 pixels at once.

**Parameters:**
- `pixels` (required): Array of 64 RGB arrays

### `remote_sense_hat.clear`
Clear the display.

**Parameters:**
- `color` (optional): RGB array [r, g, b] (default: [0, 0, 0])

### `remote_sense_hat.show_image`
Display a predefined image/pattern.

**Parameters:**
- `image_name` (required): Name of the image
- `rotation` (optional): Rotation angle (0, 90, 180, 270)

### `remote_sense_hat.set_brightness`
Set display brightness.

**Parameters:**
- `brightness` (required): Value between 0.0 and 1.0

### `remote_sense_hat.set_rotation`
Set display rotation.

**Parameters:**
- `rotation` (required): Angle (0, 90, 180, 270)

## Troubleshooting

### Server won't start
```bash
# Check service status
sudo systemctl status sense-hat-server

# View logs
sudo journalctl -u sense-hat-server -f

# Check if port is in use
sudo netstat -tulpn | grep 8765
```

### Home Assistant can't connect
1. Verify Raspberry Pi IP address
2. Check firewall settings on Raspberry Pi
3. Ensure server is running: `sudo systemctl status sense-hat-server`
4. Test WebSocket connection: `telnet <raspberry-pi-ip> 8765`

### Display not updating
1. Check Home Assistant logs: Settings → System → Logs
2. Verify Sense HAT is properly connected
3. Test Sense HAT directly: `python3 -c "from sense_hat import SenseHat; s = SenseHat(); s.show_message('Test')"`

## Development

See [`PLAN.md`](PLAN.md) for detailed implementation plan and architecture.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - feel free to use this project for any purpose.

## Acknowledgments

- Raspberry Pi Foundation for the Sense HAT
- Home Assistant community
- Python websockets library maintainers