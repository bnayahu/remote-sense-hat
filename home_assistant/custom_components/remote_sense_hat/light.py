"""Light platform for Remote Sense HAT LED matrix."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LIGHT_ENTITY_ID, DEFAULT_BRIGHTNESS, DEFAULT_RGB_COLOR

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Remote Sense HAT light from a config entry."""
    client = hass.data[DOMAIN][entry.entry_id]
    
    # Create light entity
    light = SenseHatLight(client, entry)
    
    async_add_entities([light])


class SenseHatLight(LightEntity):
    """Representation of the Sense HAT LED matrix as a light."""
    
    def __init__(self, client, entry: ConfigEntry):
        """Initialize the light."""
        self._client = client
        self._entry = entry
        self._attr_has_entity_name = True
        self._attr_name = "LED Matrix"
        self._attr_unique_id = f"{entry.entry_id}_{LIGHT_ENTITY_ID}"
        
        # Light capabilities
        self._attr_supported_color_modes = {ColorMode.RGB}
        self._attr_color_mode = ColorMode.RGB
        self._attr_supported_features = LightEntityFeature.EFFECT
        
        # State
        self._attr_is_on = False
        self._attr_brightness = DEFAULT_BRIGHTNESS
        self._attr_rgb_color = DEFAULT_RGB_COLOR
        
        # Effects (predefined images)
        self._attr_effect_list = []
        self._attr_effect = None
        
    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        
        # Get available images from client
        if self._client.available_images:
            self._attr_effect_list = self._client.available_images
            _LOGGER.debug(f"Available effects: {self._attr_effect_list}")
    
    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Sense HAT",
            "manufacturer": "Raspberry Pi Foundation",
            "model": "Sense HAT",
        }
    
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        # Extract parameters
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        rgb_color = kwargs.get(ATTR_RGB_COLOR)
        effect = kwargs.get(ATTR_EFFECT)
        
        # Update state
        if brightness is not None:
            self._attr_brightness = brightness
            # Convert brightness from 0-255 to 0.0-1.0 for the server
            brightness_float = brightness / 255.0
            await self._client.send_command("set_brightness", {"brightness": brightness_float})
        
        if rgb_color is not None:
            self._attr_rgb_color = rgb_color
        
        if effect is not None:
            # Show predefined image
            self._attr_effect = effect
            await self._client.send_command("show_image", {"image_name": effect})
            self._attr_is_on = True
        elif rgb_color is not None:
            # Fill display with solid color
            self._attr_effect = None
            color_list = list(rgb_color)
            await self._client.send_command("clear", {"color": color_list})
            self._attr_is_on = True
        elif not self._attr_is_on:
            # Just turn on with current color if off
            color_list = list(self._attr_rgb_color)
            await self._client.send_command("clear", {"color": color_list})
            self._attr_is_on = True
        
        self.async_write_ha_state()
        _LOGGER.debug(
            f"Light turned on: brightness={self._attr_brightness}, "
            f"color={self._attr_rgb_color}, effect={self._attr_effect}"
        )
    
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        # Clear the display (turn off all LEDs)
        await self._client.send_command("clear", {"color": [0, 0, 0]})
        self._attr_is_on = False
        self._attr_effect = None
        self.async_write_ha_state()
        _LOGGER.debug("Light turned off")
    
    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._attr_is_on
    
    @property
    def brightness(self) -> int:
        """Return the brightness of the light."""
        return self._attr_brightness
    
    @property
    def rgb_color(self) -> tuple[int, int, int]:
        """Return the RGB color value."""
        return self._attr_rgb_color
    
    @property
    def effect(self) -> str | None:
        """Return the current effect."""
        return self._attr_effect
    
    @property
    def effect_list(self) -> list[str]:
        """Return the list of supported effects."""
        return self._attr_effect_list


# Made with Bob