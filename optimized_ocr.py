#!/usr/bin/env python3
"""
Optimized Roulette OCR Tool
Uses API Ninjas OCR for reliable number recognition
"""

import requests
from PIL import Image, ImageGrab
import io
import re
import os
from datetime import datetime

def capture_screen_area(x, y, width, height):
    """Capture screen area"""
    try:
        screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        return screenshot
    except Exception as e:
        print(f"❌ Error capturing screen: {e}")
        return None

def recognize_text_api_ninjas(image):
    """Extract text using API Ninjas OCR"""
    try:
        # Convert to bytes
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        
        # API Ninjas request
        url = "https://api.api-ninjas.com/v1/imagetotext"
        files = {'image': ('image.png', img_bytes, 'image/png')}
        
        response = requests.post(url, files=files, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            text = ' '.join([item.get('text', '') for item in result])
            
            # Output only the extracted text
            print(text.strip())
            return text.strip()
        else:
            print(f"API error: {response.status_code}")
            return ""
            
    except Exception as e:
        print(f"OCR error: {e}")
        return ""

def quick_test():
    """Quick test with example coordinates"""
    print("🎰 Quick Roulette Number Recognition Test")
    print("=" * 45)
    
    # Example: capture a 300x50 area at position (100, 100)
    print("📸 Capturing example area...")
    
    # You can modify these coordinates for your roulette table
    x, y, width, height = 100, 100, 300, 50
    
    image = capture_screen_area(x, y, width, height)
    if not image:
        return []
    
    print(f"✅ Captured area: ({x},{y}) size {width}x{height}")
    
    # Save for debugging
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    debug_dir = f"debug_{timestamp}"
    os.makedirs(debug_dir, exist_ok=True)
    image.save(f"{debug_dir}/captured_image.png")
    
    # Recognize text
    text = recognize_text_api_ninjas(image)
    
    if text:
        print(f"SUCCESS! Extracted text: {text}")
    else:
        print("No text found")
    
    return text

def interactive_mode():
    """Interactive coordinate input"""
    print("🎰 Interactive Roulette OCR")
    print("=" * 30)
    
    print("Enter the screen coordinates to capture:")
    try:
        x = int(input("X position (left): "))
        y = int(input("Y position (top): "))
        width = int(input("Width: "))
        height = int(input("Height: "))
        
        print(f"\n📸 Capturing area: ({x},{y}) size {width}x{height}")
        
        image = capture_screen_area(x, y, width, height)
        if not image:
            return []
        
        # Save for debugging
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        debug_dir = f"debug_{timestamp}"
        os.makedirs(debug_dir, exist_ok=True)
        image.save(f"{debug_dir}/captured_image.png")
        print(f"💾 Image saved: {debug_dir}/captured_image.png")
        
        # Recognize text
        text = recognize_text_api_ninjas(image)
        
        if text:
            print(f"SUCCESS! Extracted text: {text}")
        else:
            print("No text found")
        
        return text
        
    except ValueError as e:
        print(f"❌ Invalid input: {e}")
        return []

def main():
    """Main function"""
    print("🎰 Optimized Roulette OCR Tool")
    print("Using API Ninjas for reliable recognition")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Quick test (coordinates: 100,100 size 300x50)")
        print("2. Interactive mode (enter your coordinates)")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            quick_test()
        elif choice == "2":
            interactive_mode()
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
