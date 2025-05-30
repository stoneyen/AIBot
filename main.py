from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import re

app = FastAPI(title="Color Display API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Regular expression to validate hex color codes
hex_pattern = re.compile(r'^#?([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$')

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
