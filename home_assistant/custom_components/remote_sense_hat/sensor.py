"""Sensor platform for Remote Sense HAT."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta

from .const import DOMAIN, SENSOR_TEMPERATURE, SENSOR_HUMIDITY, SENSOR_PRESSURE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Remote Sense HAT sensors from a config entry."""
    client = hass.data[DOMAIN][entry.entry_id]
    
    # Create sensor entities
    sensors = [
        SenseHatTemperatureSensor(client, entry),
        SenseHatHumiditySensor(client, entry),
        SenseHatPressureSensor(client, entry),
    ]
    
    async_add_entities(sensors)


class SenseHatSensorBase(SensorEntity):
    """Base class for Sense HAT sensors."""
    
    def __init__(self, client, entry: ConfigEntry, sensor_type: str):
        """Initialize the sensor."""
        self._client = client
        self._entry = entry
        self._sensor_type = sensor_type
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        
    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        
        # Listen for sensor updates
        @callback
        def handle_sensor_update(event):
            """Handle sensor update event."""
            data = event.data.get("data", {})
            self._update_from_data(data)
            self.async_write_ha_state()
        
        self.async_on_remove(
            self.hass.bus.async_listen(
                f"{DOMAIN}_sensor_update",
                handle_sensor_update
            )
        )
        
        # Initial update if data available
        if self._client.sensor_data:
            self._update_from_data(self._client.sensor_data)
    
    def _update_from_data(self, data: dict[str, Any]) -> None:
        """Update sensor from data. Override in subclasses."""
        pass
    
    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Sense HAT",
            "manufacturer": "Raspberry Pi Foundation",
            "model": "Sense HAT",
        }


class SenseHatTemperatureSensor(SenseHatSensorBase):
    """Temperature sensor for Sense HAT."""
    
    def __init__(self, client, entry: ConfigEntry):
        """Initialize the temperature sensor."""
        super().__init__(client, entry, SENSOR_TEMPERATURE)
        self._attr_name = "Temperature"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_native_value = None
    
    def _update_from_data(self, data: dict[str, Any]) -> None:
        """Update temperature from sensor data."""
        if SENSOR_TEMPERATURE in data:
            self._attr_native_value = data[SENSOR_TEMPERATURE]
            _LOGGER.debug("Temperature updated: %s°C", self._attr_native_value)


class SenseHatHumiditySensor(SenseHatSensorBase):
    """Humidity sensor for Sense HAT."""
    
    def __init__(self, client, entry: ConfigEntry):
        """Initialize the humidity sensor."""
        super().__init__(client, entry, SENSOR_HUMIDITY)
        self._attr_name = "Humidity"
        self._attr_device_class = SensorDeviceClass.HUMIDITY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_native_value = None
    
    def _update_from_data(self, data: dict[str, Any]) -> None:
        """Update humidity from sensor data."""
        if SENSOR_HUMIDITY in data:
            self._attr_native_value = data[SENSOR_HUMIDITY]
            _LOGGER.debug("Humidity updated: %s%%", self._attr_native_value)


class SenseHatPressureSensor(SenseHatSensorBase):
    """Pressure sensor for Sense HAT."""
    
    def __init__(self, client, entry: ConfigEntry):
        """Initialize the pressure sensor."""
        super().__init__(client, entry, SENSOR_PRESSURE)
        self._attr_name = "Pressure"
        self._attr_device_class = SensorDeviceClass.PRESSURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfPressure.HPA
        self._attr_native_value = None
    
    def _update_from_data(self, data: dict[str, Any]) -> None:
        """Update pressure from sensor data."""
        if SENSOR_PRESSURE in data:
            self._attr_native_value = data[SENSOR_PRESSURE]
            _LOGGER.debug("Pressure updated: %s hPa", self._attr_native_value)

# Made with Bob
