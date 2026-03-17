# Sense HAT WebSocket Test Client

A simple Python client to test your Sense HAT WebSocket server.

## Installation

Install the required dependency:

```bash
pip3 install websockets
```

## Usage

### Automatic Test Mode (Default)

Runs a series of automated tests:

```bash
python3 test_client.py <raspberry_pi_ip>
```

Example:
```bash
python3 test_client.py 192.168.1.50
```

With custom port:
```bash
python3 test_client.py 192.168.1.50 8765
```

### Interactive Mode

For manual testing:

```bash
python3 test_client.py <raspberry_pi_ip> --interactive
```

Example:
```bash
python3 test_client.py 192.168.1.50 --interactive
```

## Automatic Tests

The automatic mode runs these tests in sequence:

1. **Display Text** - Shows "Hello from test client!" in green
2. **Show Image** - Displays a heart icon
3. **Set Pixel** - Sets a single red pixel at position (3, 4)
4. **Clear Display** - Clears with blue color
5. **Set Brightness** - Sets brightness to 30%
6. **Get Sensors** - Retrieves temperature, humidity, and pressure
7. **Final Clear** - Clears the display

## Interactive Mode Commands

When in interactive mode, you can use these commands:

- **1** - Display text (you'll be prompted for the text)
- **2** - Show image (choose from: heart, smile, check, cross, arrow_up, arrow_down)
- **3** - Set pixel (enter X, Y coordinates and RGB color)
- **4** - Clear display
- **5** - Set brightness (0.0 to 1.0)
- **6** - Get sensor data
- **q** - Quit

## Example Session

```bash
$ python3 test_client.py 192.168.1.50
==================================================
Sense HAT WebSocket Test Client
==================================================
Target: 192.168.1.50:8765

Connecting to ws://192.168.1.50:8765...
✓ Connected successfully!
✓ Server response: Connected to Sense HAT server
  Available images: heart, smile, check, cross, arrow_up, arrow_down

==================================================
Running Tests
==================================================

Sending command: display_text
  Data: {'text': 'Hello from test client!', 'scroll_speed': 0.1, 'text_color': [0, 255, 0], 'back_color': [0, 0, 0]}
✓ Command successful: success

Sending command: show_image
  Data: {'image_name': 'heart'}
✓ Command successful: success

Sending command: set_pixel
  Data: {'x': 3, 'y': 4, 'color': [255, 0, 0]}
✓ Command successful: success

Sending command: clear
  Data: {'color': [0, 0, 255]}
✓ Command successful: success

Sending command: set_brightness
  Data: {'brightness': 0.3}
✓ Command successful: success

Requesting sensor data...
✓ Sensor data received:
  Temperature: 22.5°C
  Humidity: 45.2%
  Pressure: 1013.25 hPa

Sending command: clear
  Data: {}
✓ Command successful: success

==================================================
Tests Complete!
==================================================

✓ Disconnected
```

## Troubleshooting

### Connection Failed

```
✗ Connection failed: [Errno 111] Connection refused
```

**Solutions:**
1. Check if the server is running: `sudo systemctl status sense-hat-server`
2. Verify the IP address is correct
3. Check if port 8765 is open: `sudo netstat -tulpn | grep 8765`
4. Test network connectivity: `ping <raspberry_pi_ip>`

### Module Not Found

```
ModuleNotFoundError: No module named 'websockets'
```

**Solution:**
```bash
pip3 install websockets
```

### Command Timeout

```
✗ Command timeout (no response)
```

**Solutions:**
1. Check server logs: `sudo journalctl -u sense-hat-server -f`
2. Verify Sense HAT is connected properly
3. Restart the server: `sudo systemctl restart sense-hat-server`

### Invalid Image Name

```
✗ Command failed: Unknown image 'invalid'
```

**Solution:**
Use one of the available images: heart, smile, check, cross, arrow_up, arrow_down

## Testing Specific Features

### Test Text Display Only

```python
python3 test_client.py 192.168.1.50 --interactive
# Then press 1 and enter your text
```

### Test Sensors Only

```python
python3 test_client.py 192.168.1.50 --interactive
# Then press 6
```

### Test All Images

In interactive mode, press 2 and try each image:
- heart
- smile
- check
- cross
- arrow_up
- arrow_down

## Advanced Usage

### Custom Test Script

You can modify `test_client.py` to add your own tests. Look for the `run_tests()` function:

```python
async def run_tests(host: str, port: int):
    client = SenseHatTestClient(host, port)
    
    if not await client.connect():
        return
    
    # Add your custom tests here
    await client.send_command("display_text", {
        "text": "My custom test",
        "text_color": [255, 0, 255]
    })
    
    await client.disconnect()
```

### Using as a Library

You can also import and use the client in your own scripts:

```python
import asyncio
from test_client import SenseHatTestClient

async def my_test():
    client = SenseHatTestClient("192.168.1.50", 8765)
    await client.connect()
    
    await client.send_command("display_text", {
        "text": "Hello!",
        "text_color": [0, 255, 0]
    })
    
    await client.get_sensors()
    await client.disconnect()

asyncio.run(my_test())
```

## What Gets Tested

### Connection Test
- Verifies WebSocket connection
- Receives welcome message
- Lists available images

### Display Commands
- Text scrolling with colors
- Image display
- Pixel manipulation
- Display clearing
- Brightness adjustment

### Sensor Commands
- Temperature reading
- Humidity reading
- Pressure reading

## Next Steps

After successful testing:

1. **Verify all tests pass** - All commands should show ✓
2. **Check sensor readings** - Ensure values are reasonable
3. **Test interactive mode** - Try manual commands
4. **Install Home Assistant component** - Follow installation.md
5. **Create automations** - See examples.md for ideas

## Support

If you encounter issues:
1. Check the server logs: `sudo journalctl -u sense-hat-server -f`
2. Verify Sense HAT hardware: `python3 -c "from sense_hat import SenseHat; s = SenseHat(); s.show_message('Test')"`
3. Review the installation guide: `docs/installation.md`
4. Check network connectivity between machines