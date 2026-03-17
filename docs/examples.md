# Usage Examples

This document provides practical examples for using the Remote Sense HAT integration in Home Assistant.

## Basic Display Operations

### Display Simple Text

```yaml
service: remote_sense_hat.display_text
data:
  text: "Hello World!"
```

### Display Text with Custom Colors

```yaml
service: remote_sense_hat.display_text
data:
  text: "Temperature: 22°C"
  text_color: [255, 0, 0]  # Red text
  back_color: [0, 0, 0]    # Black background
  scroll_speed: 0.08
```

### Clear Display

```yaml
service: remote_sense_hat.clear
```

### Clear with Color

```yaml
service: remote_sense_hat.clear
data:
  color: [0, 0, 255]  # Blue
```

### Show Predefined Image

```yaml
service: remote_sense_hat.show_image
data:
  image_name: "heart"
  rotation: 0
```

Available images: `heart`, `smile`, `check`, `cross`, `arrow_up`, `arrow_down`

### Set Individual Pixel

```yaml
service: remote_sense_hat.set_pixel
data:
  x: 3
  y: 4
  color: [0, 255, 0]  # Green
```

### Adjust Brightness

```yaml
service: remote_sense_hat.set_brightness
data:
  brightness: 0.3  # 30% brightness
```

### Rotate Display

```yaml
service: remote_sense_hat.set_rotation
data:
  rotation: 180  # Upside down
```

## Automations

### Welcome Home Message

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
          text: "Welcome Home, John!"
          text_color: [0, 255, 0]
          scroll_speed: 0.1
```

### Goodbye Message

```yaml
automation:
  - alias: "Goodbye Display"
    trigger:
      - platform: state
        entity_id: person.john
        from: "home"
        to: "not_home"
    action:
      - service: remote_sense_hat.display_text
        data:
          text: "Goodbye! Have a great day!"
          text_color: [255, 165, 0]
```

### Temperature Alert

```yaml
automation:
  - alias: "High Temperature Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.sense_hat_temperature
        above: 30
    action:
      - service: remote_sense_hat.display_text
        data:
          text: "HOT! {{ states('sensor.sense_hat_temperature') }}°C"
          text_color: [255, 0, 0]
          scroll_speed: 0.05
      - service: remote_sense_hat.show_image
        data:
          image_name: "cross"
```

### Humidity Warning

```yaml
automation:
  - alias: "High Humidity Warning"
    trigger:
      - platform: numeric_state
        entity_id: sensor.sense_hat_humidity
        above: 70
    action:
      - service: remote_sense_hat.display_text
        data:
          text: "Humidity: {{ states('sensor.sense_hat_humidity') }}%"
          text_color: [0, 0, 255]
```

### Doorbell Notification

```yaml
automation:
  - alias: "Doorbell Visual Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.doorbell
        to: "on"
    action:
      - service: remote_sense_hat.show_image
        data:
          image_name: "smile"
      - delay:
          seconds: 3
      - service: remote_sense_hat.clear
```

### Time-Based Greeting

```yaml
automation:
  - alias: "Morning Greeting"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: remote_sense_hat.display_text
        data:
          text: "Good Morning! {{ now().strftime('%H:%M') }}"
          text_color: [255, 255, 0]
```

### Weather Display

```yaml
automation:
  - alias: "Weather Update"
    trigger:
      - platform: time_pattern
        hours: "/3"  # Every 3 hours
    action:
      - service: remote_sense_hat.display_text
        data:
          text: >
            Weather: {{ states('weather.home') }}
            Temp: {{ state_attr('weather.home', 'temperature') }}°C
          text_color: [100, 200, 255]
```

### Cycling Sensor Display

```yaml
automation:
  - alias: "Cycle Sensor Display"
    trigger:
      - platform: time_pattern
        seconds: "/20"  # Every 20 seconds
    action:
      - choose:
          # Temperature (0-20 seconds)
          - conditions:
              - condition: template
                value_template: "{{ now().second % 60 < 20 }}"
            sequence:
              - service: remote_sense_hat.display_text
                data:
                  text: "Temp: {{ states('sensor.sense_hat_temperature') }}°C"
                  text_color: [255, 0, 0]
          
          # Humidity (20-40 seconds)
          - conditions:
              - condition: template
                value_template: "{{ now().second % 60 < 40 }}"
            sequence:
              - service: remote_sense_hat.display_text
                data:
                  text: "Humidity: {{ states('sensor.sense_hat_humidity') }}%"
                  text_color: [0, 0, 255]
        
        # Pressure (40-60 seconds)
        default:
          - service: remote_sense_hat.display_text
            data:
              text: "Pressure: {{ states('sensor.sense_hat_pressure') }} hPa"
              text_color: [0, 255, 0]
```

### Motion Detection Alert

```yaml
automation:
  - alias: "Motion Detected Display"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion_sensor
        to: "on"
    action:
      - service: remote_sense_hat.show_image
        data:
          image_name: "arrow_up"
      - service: remote_sense_hat.display_text
        data:
          text: "Motion Detected!"
          text_color: [255, 0, 0]
```

### Reminder System

```yaml
automation:
  - alias: "Medication Reminder"
    trigger:
      - platform: time
        at: "09:00:00"
      - platform: time
        at: "21:00:00"
    action:
      - service: remote_sense_hat.display_text
        data:
          text: "Time for medication!"
          text_color: [255, 165, 0]
          scroll_speed: 0.08
      - repeat:
          count: 3
          sequence:
            - service: remote_sense_hat.show_image
              data:
                image_name: "heart"
            - delay:
                seconds: 1
            - service: remote_sense_hat.clear
            - delay:
                seconds: 1
```

## Scripts

### Rainbow Effect

```yaml
script:
  sense_hat_rainbow:
    alias: "Sense HAT Rainbow"
    sequence:
      - repeat:
          count: 7
          sequence:
            - service: remote_sense_hat.clear
              data:
                color: >
                  {% set colors = [
                    [255, 0, 0],
                    [255, 127, 0],
                    [255, 255, 0],
                    [0, 255, 0],
                    [0, 0, 255],
                    [75, 0, 130],
                    [148, 0, 211]
                  ] %}
                  {{ colors[repeat.index - 1] }}
            - delay:
                milliseconds: 500
```

### Countdown Timer

```yaml
script:
  sense_hat_countdown:
    alias: "Sense HAT Countdown"
    fields:
      seconds:
        description: "Number of seconds to count down"
        example: 10
    sequence:
      - repeat:
          count: "{{ seconds }}"
          sequence:
            - service: remote_sense_hat.display_text
              data:
                text: "{{ seconds - repeat.index + 1 }}"
                text_color: [255, 255, 0]
                scroll_speed: 0.05
            - delay:
                seconds: 1
      - service: remote_sense_hat.show_image
        data:
          image_name: "check"
```

### Status Indicator

```yaml
script:
  sense_hat_status:
    alias: "Show System Status"
    sequence:
      - choose:
          - conditions:
              - condition: state
                entity_id: alarm_control_panel.home
                state: "armed_away"
            sequence:
              - service: remote_sense_hat.show_image
                data:
                  image_name: "cross"
          
          - conditions:
              - condition: state
                entity_id: alarm_control_panel.home
                state: "disarmed"
            sequence:
              - service: remote_sense_hat.show_image
                data:
                  image_name: "check"
```

## Dashboard Cards

### Sensor Display Card

```yaml
type: entities
title: Sense HAT Sensors
entities:
  - entity: sensor.sense_hat_temperature
    name: Temperature
    icon: mdi:thermometer
  - entity: sensor.sense_hat_humidity
    name: Humidity
    icon: mdi:water-percent
  - entity: sensor.sense_hat_pressure
    name: Pressure
    icon: mdi:gauge
```

### Control Card

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: "## Sense HAT Display Control"
  
  - type: entities
    entities:
      - type: button
        name: Show Heart
        tap_action:
          action: call-service
          service: remote_sense_hat.show_image
          service_data:
            image_name: heart
      
      - type: button
        name: Show Smile
        tap_action:
          action: call-service
          service: remote_sense_hat.show_image
          service_data:
            image_name: smile
      
      - type: button
        name: Clear Display
        tap_action:
          action: call-service
          service: remote_sense_hat.clear
```

### Quick Message Card

```yaml
type: entities
title: Quick Messages
entities:
  - type: button
    name: "Hello"
    tap_action:
      action: call-service
      service: remote_sense_hat.display_text
      service_data:
        text: "Hello!"
        text_color: [0, 255, 0]
  
  - type: button
    name: "Goodbye"
    tap_action:
      action: call-service
      service: remote_sense_hat.display_text
      service_data:
        text: "Goodbye!"
        text_color: [255, 0, 0]
  
  - type: button
    name: "Show Time"
    tap_action:
      action: call-service
      service: remote_sense_hat.display_text
      service_data:
        text: "{{ now().strftime('%H:%M') }}"
        text_color: [255, 255, 0]
```

### History Graph

```yaml
type: history-graph
title: Environmental Trends
entities:
  - entity: sensor.sense_hat_temperature
    name: Temperature
  - entity: sensor.sense_hat_humidity
    name: Humidity
  - entity: sensor.sense_hat_pressure
    name: Pressure
hours_to_show: 24
refresh_interval: 60
```

## Advanced Examples

### Custom Pixel Pattern

```yaml
service: remote_sense_hat.set_pixels
data:
  pixels:
    # Row 1
    - [255, 0, 0]
    - [255, 0, 0]
    - [0, 0, 0]
    - [0, 0, 0]
    - [0, 0, 0]
    - [0, 0, 0]
    - [255, 0, 0]
    - [255, 0, 0]
    # Row 2
    - [255, 0, 0]
    - [255, 0, 0]
    - [255, 0, 0]
    - [0, 0, 0]
    - [0, 0, 0]
    - [255, 0, 0]
    - [255, 0, 0]
    - [255, 0, 0]
    # ... (continue for all 64 pixels)
```

### Dynamic Color Based on Temperature

```yaml
automation:
  - alias: "Temperature Color Display"
    trigger:
      - platform: state
        entity_id: sensor.sense_hat_temperature
    action:
      - service: remote_sense_hat.display_text
        data:
          text: "{{ states('sensor.sense_hat_temperature') }}°C"
          text_color: >
            {% set temp = states('sensor.sense_hat_temperature') | float %}
            {% if temp < 15 %}
              [0, 0, 255]
            {% elif temp < 20 %}
              [0, 255, 255]
            {% elif temp < 25 %}
              [0, 255, 0]
            {% elif temp < 30 %}
              [255, 255, 0]
            {% else %}
              [255, 0, 0]
            {% endif %}
```

### Night Mode (Auto Brightness)

```yaml
automation:
  - alias: "Sense HAT Night Mode"
    trigger:
      - platform: sun
        event: sunset
      - platform: sun
        event: sunrise
    action:
      - service: remote_sense_hat.set_brightness
        data:
          brightness: >
            {% if is_state('sun.sun', 'below_horizon') %}
              0.1
            {% else %}
              0.5
            {% endif %}
```

### Notification Queue

```yaml
script:
  sense_hat_notify:
    alias: "Queue Notification"
    fields:
      message:
        description: "Message to display"
        example: "Hello World"
    sequence:
      - service: input_text.set_value
        target:
          entity_id: input_text.sense_hat_queue
        data:
          value: >
            {{ states('input_text.sense_hat_queue') }}|{{ message }}
      - service: script.process_sense_hat_queue

  process_sense_hat_queue:
    alias: "Process Notification Queue"
    sequence:
      - condition: template
        value_template: "{{ states('input_text.sense_hat_queue') != '' }}"
      - variables:
          messages: "{{ states('input_text.sense_hat_queue').split('|') }}"
          current: "{{ messages[0] }}"
      - service: remote_sense_hat.display_text
        data:
          text: "{{ current }}"
      - delay:
          seconds: 5
      - service: input_text.set_value
        target:
          entity_id: input_text.sense_hat_queue
        data:
          value: "{{ messages[1:] | join('|') }}"
```

## Tips and Best Practices

1. **Scroll Speed**: Use 0.08-0.1 for comfortable reading
2. **Color Contrast**: Ensure good contrast between text and background
3. **Message Length**: Keep messages concise for better readability
4. **Brightness**: Adjust based on ambient light (0.1-0.3 for night, 0.5-0.8 for day)
5. **Sensor Updates**: 60 seconds is usually sufficient for environmental monitoring
6. **Error Handling**: Always include fallbacks in templates
7. **Testing**: Test automations manually before relying on them
8. **Performance**: Avoid sending commands too frequently (< 1 second apart)

## Troubleshooting Examples

### Test Connection

```yaml
service: remote_sense_hat.display_text
data:
  text: "Connection Test"
```

### Force Sensor Update

```yaml
service: remote_sense_hat.update_sensors
```

### Reset Display

```yaml
service: remote_sense_hat.clear
```

```yaml
service: remote_sense_hat.set_brightness
data:
  brightness: 0.5
```

```yaml
service: remote_sense_hat.set_rotation
data:
  rotation: 0