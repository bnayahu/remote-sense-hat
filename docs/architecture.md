# System Architecture

## High-Level Overview

The Remote Sense HAT Control system consists of two main components that communicate over WebSocket:

```mermaid
graph TB
    subgraph "Home Assistant Machine"
        A[Home Assistant Core]
        B[Custom Component]
        C[Configuration UI]
        D[Services]
        A --> B
        B --> C
        B --> D
    end
    
    subgraph "Raspberry Pi"
        E[WebSocket Server]
        F[Display Controller]
        G[Sense HAT Hardware]
        H[Systemd Service]
        E --> F
        F --> G
        H --> E
    end
    
    B <-->|WebSocket| E
    
    subgraph "User Interaction"
        I[Automations]
        J[Scripts]
        K[Manual Control]
    end
    
    I --> D
    J --> D
    K --> D
```

## Communication Flow

### 1. Command Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant HA as Home Assistant
    participant WS as WebSocket Client
    participant Server as Raspberry Pi Server
    participant Display as Sense HAT
    
    User->>HA: Call service (e.g., display_text)
    HA->>WS: Format command
    WS->>Server: Send WebSocket message
    Server->>Server: Validate command
    Server->>Display: Execute display operation
    Display-->>Server: Operation complete
    Server-->>WS: Send response
    WS-->>HA: Update entity state
    HA-->>User: Show result
```

### 2. Connection Management

```mermaid
stateDiagram-v2
    [*] --> Disconnected
    Disconnected --> Connecting: Initialize
    Connecting --> Connected: Success
    Connecting --> Disconnected: Failure
    Connected --> Disconnected: Connection Lost
    Disconnected --> Connecting: Auto-Reconnect
    Connected --> [*]: Shutdown
```

### 3. Message Processing Pipeline

```mermaid
flowchart LR
    A[Incoming Message] --> B{Valid JSON?}
    B -->|No| C[Return Error]
    B -->|Yes| D{Valid Command?}
    D -->|No| C
    D -->|Yes| E{Valid Parameters?}
    E -->|No| C
    E -->|Yes| F[Execute Command]
    F --> G{Success?}
    G -->|Yes| H[Return Success]
    G -->|No| C
```

## Component Details

### Raspberry Pi Server Components

#### WebSocket Server
- **Technology**: Python `websockets` library
- **Port**: 8765 (configurable)
- **Protocol**: WebSocket (ws://)
- **Concurrency**: Async/await pattern
- **Features**:
  - Multiple client support
  - Message validation
  - Error handling
  - Graceful shutdown

#### Display Controller
- **Technology**: Python `sense-hat` library
- **Features**:
  - Thread-safe operations
  - Animation queue
  - Brightness control
  - Rotation support
  - Predefined patterns

#### Configuration
- **Format**: YAML
- **Location**: `/opt/sense-hat-server/config.yaml`
- **Hot-reload**: No (requires restart)

### Home Assistant Component

#### Custom Integration
- **Domain**: `remote_sense_hat`
- **Platform**: Display
- **Configuration**: UI-based (config_flow)
- **Features**:
  - Auto-discovery (optional)
  - Multiple device support
  - Service registration
  - Entity state management

#### Entity Structure
```
remote_sense_hat.display
├── State: connected/disconnected
├── Attributes:
│   ├── brightness: 0.0-1.0
│   ├── rotation: 0/90/180/270
│   ├── last_command: string
│   ├── server_address: string
│   └── server_port: integer
└── Services:
    ├── display_text
    ├── set_pixel
    ├── set_pixels
    ├── clear
    ├── show_image
    ├── set_brightness
    └── set_rotation
```

## Data Flow

### Text Display Example

```mermaid
sequenceDiagram
    participant User
    participant HA as Home Assistant
    participant Server as Pi Server
    participant HAT as Sense HAT
    
    User->>HA: display_text("Hello", color=[255,0,0])
    HA->>HA: Validate parameters
    HA->>Server: {"type":"command","action":"display_text","data":{...}}
    Server->>Server: Parse message
    Server->>Server: Validate data
    Server->>HAT: show_message("Hello", text_colour=[255,0,0])
    
    loop For each character
        HAT->>HAT: Scroll character
        HAT->>HAT: Update LEDs
    end
    
    HAT-->>Server: Complete
    Server-->>HA: {"status":"success","message":"Text displayed"}
    HA-->>User: Success notification
```

### Pixel Manipulation Example

```mermaid
sequenceDiagram
    participant User
    participant HA as Home Assistant
    participant Server as Pi Server
    participant HAT as Sense HAT
    
    User->>HA: set_pixel(x=3, y=4, color=[0,255,0])
    HA->>Server: {"type":"command","action":"set_pixel","data":{...}}
    Server->>HAT: set_pixel(3, 4, [0,255,0])
    HAT->>HAT: Update LED at position
    HAT-->>Server: Complete
    Server-->>HA: {"status":"success"}
    HA-->>User: Success
```

## Network Architecture

```mermaid
graph LR
    subgraph "Local Network 192.168.1.0/24"
        A[Home Assistant<br/>192.168.1.100]
        B[Raspberry Pi<br/>192.168.1.50:8765]
        C[Router]
        
        A <-->|WebSocket| B
        A <--> C
        B <--> C
    end
    
    D[Internet] <--> C
    
    style A fill:#4CAF50
    style B fill:#2196F3
```

### Network Requirements
- **Bandwidth**: Minimal (< 1 Kbps typical)
- **Latency**: < 100ms recommended
- **Ports**: 8765 (WebSocket)
- **Protocol**: TCP
- **Security**: Local network only (no external exposure)

## Error Handling Strategy

```mermaid
flowchart TD
    A[Error Occurs] --> B{Error Type}
    
    B -->|Connection Error| C[Log Error]
    C --> D[Wait Backoff Period]
    D --> E[Attempt Reconnect]
    E --> F{Success?}
    F -->|Yes| G[Resume Normal Operation]
    F -->|No| D
    
    B -->|Command Error| H[Log Error]
    H --> I[Send Error Response]
    I --> J[Update Entity State]
    
    B -->|Hardware Error| K[Log Critical Error]
    K --> L[Notify User]
    L --> M[Attempt Recovery]
    M --> N{Recovered?}
    N -->|Yes| G
    N -->|No| O[Mark Unavailable]
```

## Security Considerations

### Network Security
- WebSocket server binds to all interfaces (0.0.0.0) but should only be accessible on local network
- No authentication by default (trusted local network)
- Optional: Add token-based authentication
- Optional: Use WSS (WebSocket Secure) with TLS

### Input Validation
```mermaid
flowchart LR
    A[User Input] --> B[Type Check]
    B --> C[Range Check]
    C --> D[Sanitization]
    D --> E[Command Execution]
    
    B -->|Invalid| F[Reject]
    C -->|Out of Range| F
    D -->|Malicious| F
```

### Best Practices
1. Run server as non-root user
2. Use systemd for process management
3. Implement rate limiting for commands
4. Log all operations for audit trail
5. Keep software dependencies updated

## Performance Characteristics

### Latency Breakdown
- **Network transmission**: 1-10ms (local network)
- **Message parsing**: < 1ms
- **Display update**: 10-100ms (depends on operation)
- **Total end-to-end**: 15-150ms typical

### Throughput
- **Commands per second**: 10-50 (limited by display refresh)
- **Concurrent clients**: 5-10 (more than needed)
- **Message size**: < 1KB typical

### Resource Usage
- **Raspberry Pi CPU**: < 5% idle, < 20% during animations
- **Memory**: ~50MB for server process
- **Network**: < 1 Kbps average

## Scalability

### Current Design
- Single Raspberry Pi with one Sense HAT
- Single Home Assistant instance
- Multiple automations/scripts can use the display

### Future Expansion
- Multiple Sense HATs (multiple server instances)
- Load balancing (if needed)
- Command queuing for complex animations
- Distributed display coordination

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development"
        A[Local Testing]
        B[Unit Tests]
    end
    
    subgraph "Staging"
        C[Test Raspberry Pi]
        D[Test Home Assistant]
    end
    
    subgraph "Production"
        E[Production Raspberry Pi]
        F[Production Home Assistant]
    end
    
    A --> C
    B --> C
    C --> E
    D --> F
```

## Monitoring and Logging

### Log Locations
- **Raspberry Pi**: `/var/log/sense-hat-server.log`
- **Systemd**: `journalctl -u sense-hat-server`
- **Home Assistant**: `config/home-assistant.log`

### Metrics to Monitor
- Connection status
- Command success rate
- Error frequency
- Response times
- Server uptime

### Health Checks
```python
# Simple health check endpoint
{
    "status": "healthy",
    "uptime": 3600,
    "connected_clients": 1,
    "commands_processed": 150,
    "errors": 2
}