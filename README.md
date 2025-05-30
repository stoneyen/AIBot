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
