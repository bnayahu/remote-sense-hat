#!/usr/bin/env python3
"""
Simple WebSocket test client for Sense HAT server
Usage: python3 test_client.py <raspberry_pi_ip> [port]
"""

import asyncio
import json
import sys
from typing import Optional
import websockets


class SenseHatTestClient:
    """Simple test client for Sense HAT WebSocket server"""
    
    def __init__(self, host: str, port: int = 8765):
        self.host = host
        self.port = port
        self.url = f"ws://{host}:{port}"
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
    
    async def connect(self):
        """Connect to the server"""
        print(f"Connecting to {self.url}...")
        try:
            self.ws = await websockets.connect(self.url)
            print("✓ Connected successfully!")
            
            # Wait for welcome message
            msg = await self.ws.recv()
            data = json.loads(msg)
            print(f"✓ Server response: {data.get('message')}")
            if 'available_images' in data:
                print(f"  Available images: {', '.join(data['available_images'])}")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    async def send_command(self, action: str, data: dict):
        """Send a command to the server"""
        if not self.ws:
            print("✗ Not connected!")
            return
        
        message = {
            "type": "command",
            "action": action,
            "data": data
        }
        
        print(f"\nSending command: {action}")
        print(f"  Data: {data}")
        
        try:
            await self.ws.send(json.dumps(message))
            
            # Wait for response
            response = await asyncio.wait_for(self.ws.recv(), timeout=5.0)
            result = json.loads(response)
            
            if result.get('type') == 'response':
                print(f"✓ Command successful: {result.get('status')}")
            elif result.get('type') == 'error':
                print(f"✗ Command failed: {result.get('message')}")
            else:
                print(f"  Response: {result}")
                
        except asyncio.TimeoutError:
            print("✗ Command timeout (no response)")
        except Exception as e:
            print(f"✗ Command failed: {e}")
    
    async def get_sensors(self):
        """Request sensor data"""
        if not self.ws:
            print("✗ Not connected!")
            return
        
        print("\nRequesting sensor data...")
        
        try:
            await self.ws.send(json.dumps({"type": "get_sensors"}))
            
            # Wait for response
            response = await asyncio.wait_for(self.ws.recv(), timeout=5.0)
            result = json.loads(response)
            
            if result.get('type') == 'sensor_data':
                data = result.get('data', {})
                print("✓ Sensor data received:")
                print(f"  Temperature: {data.get('temperature')}°C")
                print(f"  Humidity: {data.get('humidity')}%")
                print(f"  Pressure: {data.get('pressure')} hPa")
            else:
                print(f"  Response: {result}")
                
        except asyncio.TimeoutError:
            print("✗ Request timeout")
        except Exception as e:
            print(f"✗ Request failed: {e}")
    
    async def disconnect(self):
        """Disconnect from server"""
        if self.ws:
            await self.ws.close()
            print("\n✓ Disconnected")


async def run_tests(host: str, port: int):
    """Run a series of tests"""
    client = SenseHatTestClient(host, port)
    
    # Connect
    if not await client.connect():
        return
    
    print("\n" + "="*50)
    print("Running Tests")
    print("="*50)
    
    # Test 1: Display text
    await client.send_command("display_text", {
        "text": "Hello from test client!",
        "scroll_speed": 0.1,
        "text_color": [0, 255, 0],
        "back_color": [0, 0, 0]
    })
    await asyncio.sleep(2)
    
    # Test 2: Show image
    await client.send_command("show_image", {
        "image_name": "heart"
    })
    await asyncio.sleep(2)
    
    # Test 3: Set pixel
    await client.send_command("set_pixel", {
        "x": 3,
        "y": 4,
        "color": [255, 0, 0]
    })
    await asyncio.sleep(1)
    
    # Test 4: Clear display
    await client.send_command("clear", {
        "color": [0, 0, 255]
    })
    await asyncio.sleep(1)
    
    # Test 5: Set brightness
    await client.send_command("set_brightness", {
        "brightness": 0.3
    })
    await asyncio.sleep(1)
    
    # Test 6: Get sensor data
    await client.get_sensors()
    
    # Test 7: Final clear
    await client.send_command("clear", {})
    
    print("\n" + "="*50)
    print("Tests Complete!")
    print("="*50)
    
    # Disconnect
    await client.disconnect()


async def interactive_mode(host: str, port: int):
    """Interactive mode for manual testing"""
    client = SenseHatTestClient(host, port)
    
    if not await client.connect():
        return
    
    print("\n" + "="*50)
    print("Interactive Mode")
    print("="*50)
    print("\nCommands:")
    print("  1 - Display text")
    print("  2 - Show image")
    print("  3 - Set pixel")
    print("  4 - Clear display")
    print("  5 - Set brightness")
    print("  6 - Get sensors")
    print("  q - Quit")
    print()
    
    while True:
        try:
            choice = input("Enter command (1-6, q): ").strip().lower()
            
            if choice == 'q':
                break
            
            elif choice == '1':
                text = input("  Enter text: ")
                await client.send_command("display_text", {
                    "text": text,
                    "text_color": [0, 255, 0]
                })
            
            elif choice == '2':
                print("  Available: heart, smile, check, cross, arrow_up, arrow_down")
                image = input("  Enter image name: ")
                await client.send_command("show_image", {
                    "image_name": image
                })
            
            elif choice == '3':
                x = int(input("  Enter X (0-7): "))
                y = int(input("  Enter Y (0-7): "))
                r = int(input("  Enter Red (0-255): "))
                g = int(input("  Enter Green (0-255): "))
                b = int(input("  Enter Blue (0-255): "))
                await client.send_command("set_pixel", {
                    "x": x,
                    "y": y,
                    "color": [r, g, b]
                })
            
            elif choice == '4':
                await client.send_command("clear", {})
            
            elif choice == '5':
                brightness = float(input("  Enter brightness (0.0-1.0): "))
                await client.send_command("set_brightness", {
                    "brightness": brightness
                })
            
            elif choice == '6':
                await client.get_sensors()
            
            else:
                print("Invalid choice!")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    await client.disconnect()


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python3 test_client.py <raspberry_pi_ip> [port] [--interactive]")
        print("\nExamples:")
        print("  python3 test_client.py 192.168.1.50")
        print("  python3 test_client.py 192.168.1.50 8765")
        print("  python3 test_client.py 192.168.1.50 --interactive")
        sys.exit(1)
    
    host = sys.argv[1]
    port = 8765
    interactive = False
    
    # Parse arguments
    for arg in sys.argv[2:]:
        if arg == "--interactive" or arg == "-i":
            interactive = True
        else:
            try:
                port = int(arg)
            except ValueError:
                print(f"Invalid port: {arg}")
                sys.exit(1)
    
    print("="*50)
    print("Sense HAT WebSocket Test Client")
    print("="*50)
    print(f"Target: {host}:{port}")
    print()
    
    try:
        if interactive:
            asyncio.run(interactive_mode(host, port))
        else:
            asyncio.run(run_tests(host, port))
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()

# Made with Bob
