#!/usr/bin/env python3
"""
Simple Text OCR - API Ninjas Only
Outputs only the extracted text from API Ninjas OCR
"""

import requests
from PIL import Image, ImageGrab
import io

def capture_and_extract_text(x, y, width, height):
    """Capture screen area and extract text using API Ninjas"""
    try:
        # Capture screenshot
        screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        
        # Convert to bytes
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        
        # API Ninjas request
        url = "https://api.api-ninjas.com/v1/imagetotext"
        files = {'image': ('image.png', img_bytes, 'image/png')}
        
        response = requests.post(url, files=files, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            text = ' '.join([item.get('text', '') for item in result])
            return text.strip()
        else:
            return f"API error: {response.status_code}"
            
    except Exception as e:
        return f"Error: {e}"

def main():
    """Simple interactive text extraction"""
    print("Text OCR - API Ninjas Only")
    print("Enter coordinates to extract text:")
    
    try:
        x = int(input("X: "))
        y = int(input("Y: "))
        width = int(input("Width: "))
        height = int(input("Height: "))
        
        # Extract and output text
        text = capture_and_extract_text(x, y, width, height)
        print(text)
        
    except ValueError:
        print("Invalid coordinates")
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
