"""The Remote Sense HAT integration."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    SERVICE_DISPLAY_TEXT,
    SERVICE_SET_PIXEL,
    SERVICE_SET_PIXELS,
    SERVICE_CLEAR,
    SERVICE_SHOW_IMAGE,
    SERVICE_SET_BRIGHTNESS,
    SERVICE_SET_ROTATION,
    SERVICE_UPDATE_SENSORS,
    ATTR_TEXT,
    ATTR_SCROLL_SPEED,
    ATTR_TEXT_COLOR,
    ATTR_BACK_COLOR,
    ATTR_X,
    ATTR_Y,
    ATTR_COLOR,
    ATTR_PIXELS,
    ATTR_IMAGE_NAME,
    ATTR_BRIGHTNESS,
    ATTR_ROTATION,
    MSG_TYPE_COMMAND,
    MSG_TYPE_GET_SENSORS,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

# Service schemas
SERVICE_DISPLAY_TEXT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TEXT): cv.string,
        vol.Optional(ATTR_SCROLL_SPEED, default=0.1): vol.All(
            vol.Coerce(float), vol.Range(min=0.01, max=1.0)
        ),
        vol.Optional(ATTR_TEXT_COLOR): vol.All(
            cv.ensure_list, [vol.All(vol.Coerce(int), vol.Range(min=0, max=255))]
        ),
        vol.Optional(ATTR_BACK_COLOR): vol.All(
            cv.ensure_list, [vol.All(vol.Coerce(int), vol.Range(min=0, max=255))]
        ),
    }
)

SERVICE_SET_PIXEL_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_X): vol.All(vol.Coerce(int), vol.Range(min=0, max=7)),
        vol.Required(ATTR_Y): vol.All(vol.Coerce(int), vol.Range(min=0, max=7)),
        vol.Required(ATTR_COLOR): vol.All(
            cv.ensure_list, [vol.All(vol.Coerce(int), vol.Range(min=0, max=255))]
        ),
    }
)

SERVICE_SET_PIXELS_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_PIXELS): vol.All(cv.ensure_list, vol.Length(min=64, max=64)),
    }
)

SERVICE_CLEAR_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_COLOR): vol.All(
            cv.ensure_list, [vol.All(vol.Coerce(int), vol.Range(min=0, max=255))]
        ),
    }
)

SERVICE_SHOW_IMAGE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_IMAGE_NAME): cv.string,
        vol.Optional(ATTR_ROTATION): vol.In([0, 90, 180, 270]),
    }
)

SERVICE_SET_BRIGHTNESS_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_BRIGHTNESS): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
    }
)

SERVICE_SET_ROTATION_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ROTATION): vol.In([0, 90, 180, 270]),
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Remote Sense HAT from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    
    # Create WebSocket client
    client = SenseHatClient(hass, host, port)
    
    # Store client in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = client
    
    # Connect to server
    try:
        await client.connect()
    except Exception as err:
        _LOGGER.error("Failed to connect to Sense HAT server: %s", err)
        raise ConfigEntryNotReady from err
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register services
    async def handle_display_text(call: ServiceCall) -> None:
        """Handle display_text service call."""
        await client.send_command("display_text", dict(call.data))
    
    async def handle_set_pixel(call: ServiceCall) -> None:
        """Handle set_pixel service call."""
        await client.send_command("set_pixel", dict(call.data))
    
    async def handle_set_pixels(call: ServiceCall) -> None:
        """Handle set_pixels service call."""
        await client.send_command("set_pixels", dict(call.data))
    
    async def handle_clear(call: ServiceCall) -> None:
        """Handle clear service call."""
        await client.send_command("clear", dict(call.data))
    
    async def handle_show_image(call: ServiceCall) -> None:
        """Handle show_image service call."""
        await client.send_command("show_image", dict(call.data))
    
    async def handle_set_brightness(call: ServiceCall) -> None:
        """Handle set_brightness service call."""
        await client.send_command("set_brightness", dict(call.data))
    
    async def handle_set_rotation(call: ServiceCall) -> None:
        """Handle set_rotation service call."""
        await client.send_command("set_rotation", dict(call.data))
    
    async def handle_update_sensors(call: ServiceCall) -> None:
        """Handle update_sensors service call."""
        await client.request_sensor_update()
    
    # Register all services
    hass.services.async_register(
        DOMAIN, SERVICE_DISPLAY_TEXT, handle_display_text, schema=SERVICE_DISPLAY_TEXT_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SET_PIXEL, handle_set_pixel, schema=SERVICE_SET_PIXEL_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SET_PIXELS, handle_set_pixels, schema=SERVICE_SET_PIXELS_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_CLEAR, handle_clear, schema=SERVICE_CLEAR_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SHOW_IMAGE, handle_show_image, schema=SERVICE_SHOW_IMAGE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SET_BRIGHTNESS, handle_set_brightness, schema=SERVICE_SET_BRIGHTNESS_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SET_ROTATION, handle_set_rotation, schema=SERVICE_SET_ROTATION_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE_SENSORS, handle_update_sensors
    )
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        # Disconnect client
        client: SenseHatClient = hass.data[DOMAIN][entry.entry_id]
        await client.disconnect()
        
        # Remove from hass.data
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


class SenseHatClient:
    """WebSocket client for Sense HAT server."""
    
    def __init__(self, hass: HomeAssistant, host: str, port: int):
        """Initialize the client."""
        self.hass = hass
        self.host = host
        self.port = port
        self.url = f"ws://{host}:{port}"
        
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._session: aiohttp.ClientSession | None = None
        self._connected = False
        self._reconnect_task: asyncio.Task | None = None
        self._listen_task: asyncio.Task | None = None
        
        self.sensor_data: dict[str, Any] = {}
        self.available_images: list[str] = []
    
    @property
    def connected(self) -> bool:
        """Return connection status."""
        return self._connected
    
    async def connect(self) -> None:
        """Connect to the WebSocket server."""
        if self._connected:
            return
        
        try:
            self._session = aiohttp.ClientSession()
            self._ws = await self._session.ws_connect(
                self.url,
                timeout=aiohttp.ClientTimeout(total=10)
            )
            self._connected = True
            
            _LOGGER.info("Connected to Sense HAT server at %s", self.url)
            
            # Start listening for messages
            self._listen_task = asyncio.create_task(self._listen())
            
            # Wait for welcome message
            await asyncio.sleep(0.5)
            
        except Exception as err:
            _LOGGER.error("Failed to connect to Sense HAT server: %s", err)
            await self._cleanup()
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from the server."""
        self._connected = False
        
        if self._listen_task:
            self._listen_task.cancel()
        
        if self._reconnect_task:
            self._reconnect_task.cancel()
        
        await self._cleanup()
        _LOGGER.info("Disconnected from Sense HAT server")
    
    async def _cleanup(self) -> None:
        """Clean up connection resources."""
        if self._ws:
            await self._ws.close()
            self._ws = None
        
        if self._session:
            await self._session.close()
            self._session = None
    
    async def _listen(self) -> None:
        """Listen for messages from the server."""
        try:
            async for msg in self._ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self._handle_message(msg.data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    _LOGGER.error("WebSocket error: %s", self._ws.exception())
                    break
        except Exception as err:
            _LOGGER.error("Error in listen loop: %s", err)
        finally:
            self._connected = False
            # Attempt reconnection
            self._reconnect_task = asyncio.create_task(self._reconnect())
    
    async def _handle_message(self, data: str) -> None:
        """Handle incoming message."""
        try:
            message = json.loads(data)
            msg_type = message.get("type")
            
            if msg_type == "connected":
                self.available_images = message.get("available_images", [])
                _LOGGER.debug("Received welcome message")
            
            elif msg_type == "sensor_update":
                self.sensor_data = message.get("data", {})
                _LOGGER.debug("Received sensor update: %s", self.sensor_data)
                # Notify sensor entities
                self.hass.bus.async_fire(
                    f"{DOMAIN}_sensor_update",
                    {"data": self.sensor_data}
                )
            
            elif msg_type == "response":
                _LOGGER.debug("Command response: %s", message)
            
            elif msg_type == "error":
                _LOGGER.error("Server error: %s", message.get("message"))
        
        except json.JSONDecodeError as err:
            _LOGGER.error("Failed to decode message: %s", err)
    
    async def _reconnect(self) -> None:
        """Attempt to reconnect to the server."""
        delay = 5
        max_delay = 300
        
        while not self._connected:
            _LOGGER.info("Attempting to reconnect in %d seconds...", delay)
            await asyncio.sleep(delay)
            
            try:
                await self.connect()
                _LOGGER.info("Reconnected successfully")
                return
            except Exception as err:
                _LOGGER.error("Reconnection failed: %s", err)
                delay = min(delay * 1.5, max_delay)
    
    async def send_command(self, action: str, data: dict[str, Any]) -> None:
        """Send a command to the server."""
        if not self._connected or not self._ws:
            _LOGGER.error("Not connected to server")
            return
        
        message = {
            "type": MSG_TYPE_COMMAND,
            "action": action,
            "data": data
        }
        
        try:
            await self._ws.send_json(message)
            _LOGGER.debug("Sent command: %s", action)
        except Exception as err:
            _LOGGER.error("Failed to send command: %s", err)
    
    async def request_sensor_update(self) -> None:
        """Request immediate sensor update."""
        if not self._connected or not self._ws:
            _LOGGER.error("Not connected to server")
            return
        
        message = {"type": MSG_TYPE_GET_SENSORS}
        
        try:
            await self._ws.send_json(message)
            _LOGGER.debug("Requested sensor update")
        except Exception as err:
            _LOGGER.error("Failed to request sensor update: %s", err)

# Made with Bob
