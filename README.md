# Color Display API

A Python FastAPI service that provides an API to display colors in full screen. This service allows you to:

- Display a specific color using hex color codes
- Display a color using RGB values
- Use UI controls to change colors
- Toggle UI visibility for a cleaner full-screen experience
- Use keyboard shortcuts for quick color changes

## Installation

1. Clone the repository:
```bash
git clone https://github.com/stoneyen/AIBot.git
cd AIBot
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Service

Start the service with:
```bash
python main.py
```

The service will run on `http://localhost:8000` by default.

## API Endpoints

### HTTP Endpoints

1. **Root Endpoint**
   - URL: `/`
   - Method: GET
   - Description: Displays the default page with a white background

2. **Hex Color Display**
   - URL: `/color/{color_code}`
   - Method: GET
   - Parameters: `color_code` - A hex color code (with or without #), e.g., FF0000 or #00FF00
   - Description: Displays a full screen with the specified color

3. **RGB Color Display**
   - URL: `/rgb/{r}/{g}/{b}`
   - Method: GET
   - Parameters: 
     - `r` - Red component (0-255)
     - `g` - Green component (0-255)
     - `b` - Blue component (0-255)
   - Description: Displays a full screen with the specified RGB color

### WebSocket Endpoint

4. **Real-time Color Control**
   - URL: `/ws`
   - Protocol: WebSocket
   - Description: Allows real-time color changes from remote services
   - Message Format: JSON
   - Supported message types:
     - Hex colors: `{"type": "hex", "color": "#FF0000"}`
     - RGB colors: `{"type": "rgb", "r": 255, "g": 0, "b": 0}`
     - Preset colors: `{"type": "preset", "color": "red"}`
     - Random color: `{"type": "preset", "color": "random"}`

## UI Features

The color display page includes a user interface with:

- Current color information (hex and RGB values)
- Buttons for predefined colors (red, green, blue, white, black)
- A random color button
- A UI toggle button to hide/show the interface

## Keyboard Shortcuts

- `h` - Toggle UI visibility
- `r` - Red
- `g` - Green
- `b` - Blue
- `w` - White
- `k` - Black
- `Space` - Random color

## Example Usage

1. Open white background:
```
http://localhost:8000/
```

2. Display red:
```
http://localhost:8000/color/FF0000
```
or
```
http://localhost:8000/color/#FF0000
```

3. Display blue using RGB:
```
http://localhost:8000/rgb/0/0/255
```

## WebSocket Usage

### Connecting to WebSocket

Connect to the WebSocket endpoint at `ws://localhost:8000/ws` to send real-time color change commands.

### Message Examples

1. **Change to red using hex:**
```json
{"type": "hex", "color": "#FF0000"}
```

2. **Change to green using RGB:**
```json
{"type": "rgb", "r": 0, "g": 255, "b": 0}
```

3. **Use preset colors:**
```json
{"type": "preset", "color": "blue"}
```

4. **Generate random color:**
```json
{"type": "preset", "color": "random"}
```

### Available Preset Colors
- red, green, blue, white, black, yellow, cyan, magenta

### Python WebSocket Client Example

```python
import asyncio
import websockets
import json

async def send_color():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Send a color change command
        message = {"type": "hex", "color": "#FF0000"}
        await websocket.send(json.dumps(message))

# Run the client
asyncio.run(send_color())
```

### Testing WebSocket Functionality

A test client is included in the repository:

```bash
python websocket_test_client.py
```

This will demonstrate various WebSocket message types and show real-time color changes in any connected browser windows.

## Features

### Real-time Updates
- WebSocket connections provide instant color changes without page refreshes
- Multiple clients can connect simultaneously and see the same color changes
- Automatic reconnection if the WebSocket connection is lost

### Connection Status
- Visual indicator showing WebSocket connection status
- Green "Connected" or red "Disconnected" status in the top-left corner

### Remote Change Indicator
- When colors are changed via WebSocket, a "Color changed remotely" indicator appears
- Helps distinguish between local UI changes and remote API calls
