#!/usr/bin/env python3
"""
WebSocket test client for the Color Display API
This script demonstrates how to send color change commands via WebSocket
"""

import asyncio
import websockets
import json
import time

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket server")
            
            # Test different message types
            test_messages = [
                {"type": "hex", "color": "#FF0000"},  # Red
                {"type": "rgb", "r": 0, "g": 255, "b": 0},  # Green
                {"type": "preset", "color": "blue"},  # Blue
                {"type": "hex", "color": "FFFF00"},  # Yellow (without #)
                {"type": "preset", "color": "random"},  # Random color
                {"type": "preset", "color": "white"},  # White
            ]
            
            for i, message in enumerate(test_messages):
                print(f"\nSending message {i+1}: {message}")
                await websocket.send(json.dumps(message))
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    print(f"Response: {response}")
                except asyncio.TimeoutError:
                    print("No response received (this is normal for broadcasts)")
                
                # Wait 2 seconds between color changes
                await asyncio.sleep(2)
            
            print("\nTest completed!")
            
    except ConnectionRefusedError:
        print("Could not connect to WebSocket server.")
        print("Make sure the Color Display API is running on localhost:8000")
    except Exception as e:
        print(f"Error: {e}")

def test_invalid_messages():
    """Test invalid message formats"""
    print("\nTesting invalid messages...")
    
    invalid_messages = [
        {"type": "invalid"},  # Invalid type
        {"type": "hex", "color": "invalid"},  # Invalid hex
        {"type": "rgb", "r": 300, "g": 0, "b": 0},  # Invalid RGB
        {"type": "preset", "color": "nonexistent"},  # Invalid preset
        "invalid json",  # Invalid JSON
    ]
    
    async def test_invalid():
        uri = "ws://localhost:8000/ws"
        try:
            async with websockets.connect(uri) as websocket:
                for message in invalid_messages:
                    print(f"Sending invalid message: {message}")
                    if isinstance(message, str):
                        await websocket.send(message)
                    else:
                        await websocket.send(json.dumps(message))
                    
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        print(f"Error response: {response}")
                    except asyncio.TimeoutError:
                        print("No response received")
                    
                    await asyncio.sleep(1)
        except Exception as e:
            print(f"Error: {e}")
    
    asyncio.run(test_invalid())

if __name__ == "__main__":
    print("Color Display API WebSocket Test Client")
    print("======================================")
    print("This script will test the WebSocket functionality")
    print("Make sure the Color Display API is running first with: python main.py")
    print()
    
    # Run the main test
    asyncio.run(test_websocket())
    
    # Test invalid messages
    test_invalid_messages()
    
    print("\nYou can also test manually by opening http://localhost:8000 in your browser")
    print("and running this script to see real-time color changes!")
