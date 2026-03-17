"""Constants for the Remote Sense HAT integration."""

DOMAIN = "remote_sense_hat"

# Configuration
CONF_HOST = "host"
CONF_PORT = "port"

# Default values
DEFAULT_PORT = 8765
DEFAULT_NAME = "Sense HAT"

# Attributes
ATTR_BRIGHTNESS = "brightness"
ATTR_ROTATION = "rotation"
ATTR_LAST_COMMAND = "last_command"
ATTR_SERVER_ADDRESS = "server_address"
ATTR_AVAILABLE_IMAGES = "available_images"

# Service names
SERVICE_DISPLAY_TEXT = "display_text"
SERVICE_SET_PIXEL = "set_pixel"
SERVICE_SET_PIXELS = "set_pixels"
SERVICE_CLEAR = "clear"
SERVICE_SHOW_IMAGE = "show_image"
SERVICE_SET_BRIGHTNESS = "set_brightness"
SERVICE_SET_ROTATION = "set_rotation"
SERVICE_UPDATE_SENSORS = "update_sensors"

# Service parameters
ATTR_TEXT = "text"
ATTR_SCROLL_SPEED = "scroll_speed"
ATTR_TEXT_COLOR = "text_color"
ATTR_BACK_COLOR = "back_color"
ATTR_X = "x"
ATTR_Y = "y"
ATTR_COLOR = "color"
ATTR_PIXELS = "pixels"
ATTR_IMAGE_NAME = "image_name"

# Sensor types
SENSOR_TEMPERATURE = "temperature"
SENSOR_HUMIDITY = "humidity"
SENSOR_PRESSURE = "pressure"

# WebSocket message types
MSG_TYPE_COMMAND = "command"
MSG_TYPE_SENSOR_UPDATE = "sensor_update"
MSG_TYPE_RESPONSE = "response"
MSG_TYPE_ERROR = "error"
MSG_TYPE_CONNECTED = "connected"
MSG_TYPE_GET_SENSORS = "get_sensors"

# Reconnection settings
RECONNECT_DELAY = 5  # seconds
MAX_RECONNECT_DELAY = 300  # 5 minutes
RECONNECT_BACKOFF = 1.5  # exponential backoff multiplier

# Made with Bob
