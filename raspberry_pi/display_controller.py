"""
Display Controller for Raspberry Pi Sense HAT
Provides abstraction layer for display operations
"""

import logging
from typing import List, Tuple, Optional
from sense_hat import SenseHat
import threading

logger = logging.getLogger(__name__)


class DisplayController:
    """Controller for Sense HAT LED display operations"""
    
    def __init__(self, brightness: float = 0.5, rotation: int = 0):
        """
        Initialize display controller
        
        Args:
            brightness: Initial brightness (0.0 - 1.0)
            rotation: Initial rotation (0, 90, 180, 270)
        """
        self.sense = SenseHat()
        self.sense.low_light = False
        self.lock = threading.Lock()
        
        self.set_brightness(brightness)
        self.set_rotation(rotation)
        
        # Predefined images/patterns
        self.images = self._load_predefined_images()
        
        logger.info(f"Display controller initialized (brightness={brightness}, rotation={rotation})")
    
    def _load_predefined_images(self) -> dict:
        """Load predefined 8x8 images/patterns"""
        
        # Colors
        R = [255, 0, 0]    # Red
        G = [0, 255, 0]    # Green
        B = [0, 0, 255]    # Blue
        Y = [255, 255, 0]  # Yellow
        W = [255, 255, 255]  # White
        O = [0, 0, 0]      # Off/Black
        
        return {
            "heart": [
                O, R, R, O, O, R, R, O,
                R, R, R, R, R, R, R, R,
                R, R, R, R, R, R, R, R,
                R, R, R, R, R, R, R, R,
                O, R, R, R, R, R, R, O,
                O, O, R, R, R, R, O, O,
                O, O, O, R, R, O, O, O,
                O, O, O, O, O, O, O, O,
            ],
            "smile": [
                O, O, Y, Y, Y, Y, O, O,
                O, Y, Y, Y, Y, Y, Y, O,
                Y, Y, O, Y, Y, O, Y, Y,
                Y, Y, Y, Y, Y, Y, Y, Y,
                Y, O, Y, Y, Y, Y, O, Y,
                Y, Y, O, O, O, O, Y, Y,
                O, Y, Y, Y, Y, Y, Y, O,
                O, O, Y, Y, Y, Y, O, O,
            ],
            "check": [
                O, O, O, O, O, O, O, G,
                O, O, O, O, O, O, G, G,
                O, O, O, O, O, G, G, O,
                G, O, O, O, G, G, O, O,
                G, G, O, G, G, O, O, O,
                O, G, G, G, O, O, O, O,
                O, O, G, O, O, O, O, O,
                O, O, O, O, O, O, O, O,
            ],
            "cross": [
                R, O, O, O, O, O, O, R,
                O, R, O, O, O, O, R, O,
                O, O, R, O, O, R, O, O,
                O, O, O, R, R, O, O, O,
                O, O, O, R, R, O, O, O,
                O, O, R, O, O, R, O, O,
                O, R, O, O, O, O, R, O,
                R, O, O, O, O, O, O, R,
            ],
            "arrow_up": [
                O, O, O, G, G, O, O, O,
                O, O, G, G, G, G, O, O,
                O, G, G, G, G, G, G, O,
                G, G, O, G, G, O, G, G,
                O, O, O, G, G, O, O, O,
                O, O, O, G, G, O, O, O,
                O, O, O, G, G, O, O, O,
                O, O, O, G, G, O, O, O,
            ],
            "arrow_down": [
                O, O, O, B, B, O, O, O,
                O, O, O, B, B, O, O, O,
                O, O, O, B, B, O, O, O,
                O, O, O, B, B, O, O, O,
                B, B, O, B, B, O, B, B,
                O, B, B, B, B, B, B, O,
                O, O, B, B, B, B, O, O,
                O, O, O, B, B, O, O, O,
            ],
        }
    
    def display_text(
        self,
        text: str,
        scroll_speed: float = 0.1,
        text_color: Optional[List[int]] = None,
        back_color: Optional[List[int]] = None
    ) -> None:
        """
        Display scrolling text
        
        Args:
            text: Text to display
            scroll_speed: Speed in seconds per character
            text_color: RGB color for text [r, g, b]
            back_color: RGB color for background [r, g, b]
        """
        with self.lock:
            try:
                text_color = text_color or [255, 255, 255]
                back_color = back_color or [0, 0, 0]
                
                logger.info(f"Displaying text: '{text}' (speed={scroll_speed})")
                self.sense.show_message(
                    text,
                    scroll_speed=scroll_speed,
                    text_colour=text_color,
                    back_colour=back_color
                )
            except Exception as e:
                logger.error(f"Error displaying text: {e}")
                raise
    
    def set_pixel(self, x: int, y: int, color: List[int]) -> None:
        """
        Set individual pixel color
        
        Args:
            x: X coordinate (0-7)
            y: Y coordinate (0-7)
            color: RGB color [r, g, b]
        """
        with self.lock:
            try:
                if not (0 <= x <= 7 and 0 <= y <= 7):
                    raise ValueError(f"Coordinates out of range: ({x}, {y})")
                
                logger.debug(f"Setting pixel ({x}, {y}) to {color}")
                self.sense.set_pixel(x, y, color)
            except Exception as e:
                logger.error(f"Error setting pixel: {e}")
                raise
    
    def set_pixels(self, pixels: List[List[int]]) -> None:
        """
        Set all 64 pixels at once
        
        Args:
            pixels: List of 64 RGB colors [[r,g,b], ...]
        """
        with self.lock:
            try:
                if len(pixels) != 64:
                    raise ValueError(f"Expected 64 pixels, got {len(pixels)}")
                
                logger.debug("Setting all pixels")
                self.sense.set_pixels(pixels)
            except Exception as e:
                logger.error(f"Error setting pixels: {e}")
                raise
    
    def clear(self, color: Optional[List[int]] = None) -> None:
        """
        Clear the display
        
        Args:
            color: Optional RGB color [r, g, b], defaults to black
        """
        with self.lock:
            try:
                color = color or [0, 0, 0]
                logger.debug(f"Clearing display with color {color}")
                self.sense.clear(color)
            except Exception as e:
                logger.error(f"Error clearing display: {e}")
                raise
    
    def show_image(self, image_name: str, rotation: Optional[int] = None) -> None:
        """
        Display predefined image
        
        Args:
            image_name: Name of the image
            rotation: Optional rotation override (0, 90, 180, 270)
        """
        with self.lock:
            try:
                if image_name not in self.images:
                    available = ", ".join(self.images.keys())
                    raise ValueError(f"Unknown image '{image_name}'. Available: {available}")
                
                logger.info(f"Showing image: {image_name}")
                
                # Temporarily change rotation if specified
                original_rotation = None
                if rotation is not None:
                    original_rotation = self.sense.rotation
                    self.sense.rotation = rotation
                
                self.sense.set_pixels(self.images[image_name])
                
                # Restore original rotation
                if original_rotation is not None:
                    self.sense.rotation = original_rotation
                    
            except Exception as e:
                logger.error(f"Error showing image: {e}")
                raise
    
    def set_brightness(self, brightness: float) -> None:
        """
        Set display brightness
        
        Args:
            brightness: Brightness level (0.0 - 1.0)
        """
        try:
            if not 0.0 <= brightness <= 1.0:
                raise ValueError(f"Brightness must be between 0.0 and 1.0, got {brightness}")
            
            # Convert to 0-255 range for Sense HAT
            brightness_value = int(brightness * 255)
            
            logger.info(f"Setting brightness to {brightness} ({brightness_value}/255)")
            self.sense.low_light = (brightness < 0.3)
            
            # Get current pixels, adjust brightness, and set them back
            current_pixels = self.sense.get_pixels()
            self.sense.clear()
            self.sense.set_pixels(current_pixels)
            
        except Exception as e:
            logger.error(f"Error setting brightness: {e}")
            raise
    
    def set_rotation(self, rotation: int) -> None:
        """
        Set display rotation
        
        Args:
            rotation: Rotation angle (0, 90, 180, 270)
        """
        try:
            if rotation not in [0, 90, 180, 270]:
                raise ValueError(f"Rotation must be 0, 90, 180, or 270, got {rotation}")
            
            logger.info(f"Setting rotation to {rotation}°")
            self.sense.rotation = rotation
            
        except Exception as e:
            logger.error(f"Error setting rotation: {e}")
            raise
    
    def get_available_images(self) -> List[str]:
        """Get list of available predefined images"""
        return list(self.images.keys())

# Made with Bob
