from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import re
import json
from typing import List

app = FastAPI(title="Color Display API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Regular expression to validate hex color codes
hex_pattern = re.compile(r'^#?([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$')

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                # Remove disconnected clients
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Predefined colors
PRESET_COLORS = {
    "red": "#FF0000",
    "green": "#00FF00",
    "blue": "#0000FF",
    "white": "#FFFFFF",
    "black": "#000000",
    "yellow": "#FFFF00",
    "cyan": "#00FFFF",
    "magenta": "#FF00FF"
}

def hex_to_rgb(hex_color: str) -> dict:
    """Convert hex color to RGB values"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    
    return {
        "r": int(hex_color[0:2], 16),
        "g": int(hex_color[2:4], 16),
        "b": int(hex_color[4:6], 16)
    }

def validate_and_process_color(message: dict) -> tuple:
    """Validate and process color message, return (hex_color, error_dict)"""
    msg_type = message.get("type")
    
    if msg_type == "hex":
        color = message.get("color", "")
        if not color.startswith('#'):
            color = f"#{color}"
        
        if not hex_pattern.match(color):
            return None, {"error": "Invalid hex color format"}
        
        return color, None
    
    elif msg_type == "rgb":
        r = message.get("r")
        g = message.get("g")
        b = message.get("b")
        
        if not all(isinstance(val, int) and 0 <= val <= 255 for val in [r, g, b]):
            return None, {"error": "RGB values must be integers between 0-255"}
        
        color = f"#{r:02x}{g:02x}{b:02x}"
        return color, None
    
    elif msg_type == "preset":
        preset_name = message.get("color", "").lower()
        
        if preset_name == "random":
            import random
            color = f"#{random.randint(0, 16777215):06x}"
            return color, None
        
        if preset_name not in PRESET_COLORS:
            return None, {"error": f"Unknown preset color. Available: {list(PRESET_COLORS.keys())}"}
        
        return PRESET_COLORS[preset_name], None
    
    else:
        return None, {"error": "Invalid message type. Use 'hex', 'rgb', or 'preset'"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time color changes
    """
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON format"}))
                continue
            
            # Process the color change request
            hex_color, error = validate_and_process_color(message)
            
            if error:
                await websocket.send_text(json.dumps(error))
                continue
            
            # Convert to RGB for response
            rgb_values = hex_to_rgb(hex_color)
            
            # Broadcast color change to all connected clients
            response = {
                "type": "color_update",
                "hex": hex_color,
                "rgb": rgb_values,
                "source": "remote"
            }
            
            await manager.broadcast(response)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Root endpoint that displays the default page
    """
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "color": "#FFFFFF"}
    )

@app.get("/color/{color_code}", response_class=HTMLResponse)
async def display_color(request: Request, color_code: str):
    """
    Display a specific color fullscreen
    
    Args:
        color_code: Hex color code (with or without #)
    """
    # Add # if missing
    if not color_code.startswith('#'):
        color_code = f"#{color_code}"
    
    # Validate the color code
    if not hex_pattern.match(color_code):
        raise HTTPException(status_code=400, detail="Invalid color code. Please use a valid hex color (e.g., #FF0000 or #F00)")
    
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "color": color_code}
    )

@app.get("/rgb/{r}/{g}/{b}", response_class=HTMLResponse)
async def display_rgb_color(request: Request, r: int, g: int, b: int):
    """
    Display a color based on RGB values
    
    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)
    """
    # Validate RGB values
    for value, name in [(r, "red"), (g, "green"), (b, "blue")]:
        if not 0 <= value <= 255:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid {name} value. Must be between 0 and 255."
            )
    
    # Convert to hex
    color_code = f"#{r:02x}{g:02x}{b:02x}"
    
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "color": color_code}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
