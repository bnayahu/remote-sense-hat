#!/usr/bin/env python3
"""
Sense HAT WebSocket Server
Main server for controlling Raspberry Pi Sense HAT remotely via WebSocket
"""

import asyncio
import json
import logging
import signal
import sys
from pathlib import Path
from typing import Set, Dict, Any, Optional
import yaml
import websockets
from websockets.server import WebSocketServerProtocol

from display_controller import DisplayController
from sensor_reader import SensorReader, PeriodicSensorReader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SenseHatServer:
    """WebSocket server for Sense HAT control"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize server
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.clients: Set[WebSocketServerProtocol] = set()
        self.running = False
        
        # Initialize display controller
        display_config = self.config.get('display', {})
        self.display = DisplayController(
            brightness=display_config.get('brightness', 0.5),
            rotation=display_config.get('rotation', 0)
        )
        
        # Initialize sensor reader if enabled
        sensor_config = self.config.get('sensors', {})
        if sensor_config.get('enabled', True):
            from sense_hat import SenseHat
            sense = SenseHat()
            
            smoothing_config = sensor_config.get('smoothing', {})
            self.sensor_reader = SensorReader(
                sense=sense,
                temperature_offset=sensor_config.get('temperature_offset', 0.0),
                smoothing_enabled=smoothing_config.get('enabled', False),
                smoothing_window=smoothing_config.get('window_size', 5)
            )
            
            self.periodic_sensor = PeriodicSensorReader(
                sensor_reader=self.sensor_reader,
                update_interval=sensor_config.get('update_interval', 60),
                callback=self._on_sensor_update
            )
        else:
            self.sensor_reader = None
            self.periodic_sensor = None
        
        logger.info("Sense HAT server initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return self._default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'server': {'host': '0.0.0.0', 'port': 8765},
            'display': {'brightness': 0.5, 'rotation': 0},
            'sensors': {'enabled': True, 'update_interval': 60},
            'logging': {'level': 'INFO'}
        }
    
    async def _on_sensor_update(self, data: Dict[str, float]) -> None:
        """
        Callback for sensor updates
        
        Args:
            data: Sensor data dictionary
        """
        # Broadcast sensor data to all connected clients
        if self.clients:
            message = {
                'type': 'sensor_update',
                'data': data
            }
            await self._broadcast(message)
    
    async def _broadcast(self, message: Dict[str, Any]) -> None:
        """
        Broadcast message to all connected clients
        
        Args:
            message: Message dictionary to broadcast
        """
        if not self.clients:
            return
        
        message_str = json.dumps(message)
        # Send to all clients, remove disconnected ones
        disconnected = set()
        
        for client in self.clients:
            try:
                await client.send(message_str)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
        
        # Remove disconnected clients
        self.clients -= disconnected
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str) -> None:
        """
        Handle WebSocket client connection
        
        Args:
            websocket: WebSocket connection
            path: Connection path
        """
        # Register client
        self.clients.add(websocket)
        client_addr = websocket.remote_address
        logger.info(f"Client connected: {client_addr}")
        
        try:
            # Send welcome message
            await websocket.send(json.dumps({
                'type': 'connected',
                'message': 'Connected to Sense HAT server',
                'available_images': self.display.get_available_images()
            }))
            
            # Handle messages
            async for message in websocket:
                try:
                    await self._handle_message(websocket, message)
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    await self._send_error(websocket, str(e))
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_addr}")
        finally:
            self.clients.discard(websocket)
    
    async def _handle_message(self, websocket: WebSocketServerProtocol, message: str) -> None:
        """
        Handle incoming WebSocket message
        
        Args:
            websocket: WebSocket connection
            message: Message string
        """
        try:
            data = json.loads(message)
        except json.JSONDecodeError as e:
            await self._send_error(websocket, f"Invalid JSON: {e}")
            return
        
        msg_type = data.get('type')
        action = data.get('action')
        msg_data = data.get('data', {})
        
        logger.debug(f"Received message: type={msg_type}, action={action}")
        
        if msg_type == 'command':
            await self._handle_command(websocket, action, msg_data)
        elif msg_type == 'get_sensors':
            await self._handle_get_sensors(websocket)
        else:
            await self._send_error(websocket, f"Unknown message type: {msg_type}")
    
    async def _handle_command(
        self,
        websocket: WebSocketServerProtocol,
        action: str,
        data: Dict[str, Any]
    ) -> None:
        """
        Handle display command
        
        Args:
            websocket: WebSocket connection
            action: Command action
            data: Command data
        """
        try:
            if action == 'display_text':
                self.display.display_text(
                    text=data.get('text', ''),
                    scroll_speed=data.get('scroll_speed', 0.1),
                    text_color=data.get('text_color'),
                    back_color=data.get('back_color')
                )
            
            elif action == 'set_pixel':
                self.display.set_pixel(
                    x=data.get('x'),
                    y=data.get('y'),
                    color=data.get('color')
                )
            
            elif action == 'set_pixels':
                self.display.set_pixels(pixels=data.get('pixels'))
            
            elif action == 'clear':
                self.display.clear(color=data.get('color'))
            
            elif action == 'show_image':
                self.display.show_image(
                    image_name=data.get('image_name'),
                    rotation=data.get('rotation')
                )
            
            elif action == 'set_brightness':
                self.display.set_brightness(brightness=data.get('brightness'))
            
            elif action == 'set_rotation':
                self.display.set_rotation(rotation=data.get('rotation'))
            
            else:
                await self._send_error(websocket, f"Unknown action: {action}")
                return
            
            # Send success response
            await websocket.send(json.dumps({
                'type': 'response',
                'status': 'success',
                'action': action
            }))
            
        except Exception as e:
            logger.error(f"Error executing command {action}: {e}")
            await self._send_error(websocket, str(e))
    
    async def _handle_get_sensors(self, websocket: WebSocketServerProtocol) -> None:
        """
        Handle sensor data request
        
        Args:
            websocket: WebSocket connection
        """
        if not self.sensor_reader:
            await self._send_error(websocket, "Sensors not enabled")
            return
        
        try:
            data = self.sensor_reader.read_sensors()
            await websocket.send(json.dumps({
                'type': 'sensor_data',
                'data': data
            }))
        except Exception as e:
            logger.error(f"Error reading sensors: {e}")
            await self._send_error(websocket, str(e))
    
    async def _send_error(self, websocket: WebSocketServerProtocol, message: str) -> None:
        """
        Send error message to client
        
        Args:
            websocket: WebSocket connection
            message: Error message
        """
        try:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': message
            }))
        except Exception as e:
            logger.error(f"Error sending error message: {e}")
    
    async def start(self) -> None:
        """Start the WebSocket server"""
        server_config = self.config.get('server', {})
        host = server_config.get('host', '0.0.0.0')
        port = server_config.get('port', 8765)
        
        self.running = True
        
        # Start periodic sensor reader if enabled
        if self.periodic_sensor:
            self.periodic_sensor.start()
        
        logger.info(f"Starting WebSocket server on {host}:{port}")
        
        async with websockets.serve(self.handle_client, host, port):
            logger.info("Server started successfully")
            
            # Show green checkmark on successful initialization
            try:
                self.display.show_image("check")
                logger.info("Displaying initialization success indicator")
                
                # Clear display after 2 seconds
                await asyncio.sleep(2)
                self.display.clear()
                logger.info("Cleared initialization indicator")
            except Exception as e:
                logger.error(f"Error displaying initialization indicator: {e}")
            
            # Keep server running
            while self.running:
                await asyncio.sleep(1)
    
    def stop(self) -> None:
        """Stop the server"""
        logger.info("Stopping server...")
        self.running = False
        
        # Stop periodic sensor reader
        if self.periodic_sensor:
            self.periodic_sensor.stop()
        
        # Clear display
        try:
            self.display.clear()
        except Exception as e:
            logger.error(f"Error clearing display: {e}")


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)


async def main():
    """Main entry point"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Find config file
    config_path = Path(__file__).parent / "config.yaml"
    
    # Create and start server
    server = SenseHatServer(str(config_path))
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        server.stop()
        logger.info("Server stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Exiting...")

# Made with Bob
