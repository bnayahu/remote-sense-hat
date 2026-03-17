"""
Sensor Reader for Raspberry Pi Sense HAT
Handles periodic sensor data collection with smoothing
"""

import logging
from typing import Dict, Optional, List
from collections import deque
from sense_hat import SenseHat
import threading
import time

logger = logging.getLogger(__name__)


class SensorReader:
    """Reader for Sense HAT environmental sensors"""
    
    def __init__(
        self,
        sense: SenseHat,
        temperature_offset: float = 0.0,
        smoothing_enabled: bool = False,
        smoothing_window: int = 5
    ):
        """
        Initialize sensor reader
        
        Args:
            sense: SenseHat instance
            temperature_offset: Calibration offset for temperature in °C
            smoothing_enabled: Enable data smoothing
            smoothing_window: Number of readings to average
        """
        self.sense = sense
        self.temperature_offset = temperature_offset
        self.smoothing_enabled = smoothing_enabled
        self.smoothing_window = smoothing_window
        
        # Smoothing buffers
        self.temp_buffer: deque = deque(maxlen=smoothing_window)
        self.humidity_buffer: deque = deque(maxlen=smoothing_window)
        self.pressure_buffer: deque = deque(maxlen=smoothing_window)
        
        logger.info(
            f"Sensor reader initialized (offset={temperature_offset}°C, "
            f"smoothing={'enabled' if smoothing_enabled else 'disabled'})"
        )
    
    def read_sensors(self) -> Dict[str, float]:
        """
        Read all sensor values
        
        Returns:
            Dictionary with temperature, humidity, and pressure
        """
        try:
            # Read raw values
            raw_temp = self.sense.get_temperature()
            raw_humidity = self.sense.get_humidity()
            raw_pressure = self.sense.get_pressure()
            
            # Apply temperature offset
            calibrated_temp = raw_temp + self.temperature_offset
            
            # Apply smoothing if enabled
            if self.smoothing_enabled:
                self.temp_buffer.append(calibrated_temp)
                self.humidity_buffer.append(raw_humidity)
                self.pressure_buffer.append(raw_pressure)
                
                temperature = sum(self.temp_buffer) / len(self.temp_buffer)
                humidity = sum(self.humidity_buffer) / len(self.humidity_buffer)
                pressure = sum(self.pressure_buffer) / len(self.pressure_buffer)
            else:
                temperature = calibrated_temp
                humidity = raw_humidity
                pressure = raw_pressure
            
            # Round to reasonable precision
            result = {
                "temperature": round(temperature, 1),
                "humidity": round(humidity, 1),
                "pressure": round(pressure, 2),
                "timestamp": time.time()
            }
            
            logger.debug(f"Sensor reading: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error reading sensors: {e}")
            raise
    
    def get_temperature(self) -> float:
        """Get calibrated temperature reading"""
        try:
            raw_temp = self.sense.get_temperature()
            return round(raw_temp + self.temperature_offset, 1)
        except Exception as e:
            logger.error(f"Error reading temperature: {e}")
            raise
    
    def get_humidity(self) -> float:
        """Get humidity reading"""
        try:
            return round(self.sense.get_humidity(), 1)
        except Exception as e:
            logger.error(f"Error reading humidity: {e}")
            raise
    
    def get_pressure(self) -> float:
        """Get pressure reading"""
        try:
            return round(self.sense.get_pressure(), 2)
        except Exception as e:
            logger.error(f"Error reading pressure: {e}")
            raise
    
    def update_calibration(self, temperature_offset: float) -> None:
        """
        Update temperature calibration offset
        
        Args:
            temperature_offset: New offset in °C
        """
        logger.info(f"Updating temperature offset: {self.temperature_offset}°C -> {temperature_offset}°C")
        self.temperature_offset = temperature_offset
        
        # Clear smoothing buffer to avoid mixing calibrations
        if self.smoothing_enabled:
            self.temp_buffer.clear()
    
    def reset_smoothing(self) -> None:
        """Clear all smoothing buffers"""
        logger.debug("Resetting smoothing buffers")
        self.temp_buffer.clear()
        self.humidity_buffer.clear()
        self.pressure_buffer.clear()


class PeriodicSensorReader:
    """Periodic sensor reader with background thread"""
    
    def __init__(
        self,
        sensor_reader: SensorReader,
        update_interval: int = 60,
        callback=None
    ):
        """
        Initialize periodic sensor reader
        
        Args:
            sensor_reader: SensorReader instance
            update_interval: Seconds between readings
            callback: Optional callback function for sensor updates
        """
        self.sensor_reader = sensor_reader
        self.update_interval = update_interval
        self.callback = callback
        
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        logger.info(f"Periodic sensor reader initialized (interval={update_interval}s)")
    
    def start(self) -> None:
        """Start periodic sensor reading"""
        if self.running:
            logger.warning("Periodic sensor reader already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()
        logger.info("Periodic sensor reader started")
    
    def stop(self) -> None:
        """Stop periodic sensor reading"""
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Periodic sensor reader stopped")
    
    def _read_loop(self) -> None:
        """Background thread loop for reading sensors"""
        while self.running:
            try:
                # Read sensors
                data = self.sensor_reader.read_sensors()
                
                # Call callback if provided
                if self.callback:
                    self.callback(data)
                
                # Wait for next interval
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in sensor read loop: {e}")
                time.sleep(5)  # Wait before retrying
    
    def read_now(self) -> Dict[str, float]:
        """Force immediate sensor reading"""
        return self.sensor_reader.read_sensors()

# Made with Bob
