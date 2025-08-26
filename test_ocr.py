#!/usr/bin/env python3
"""
Simple test for the screen capture functionality
"""

try:
    import pyautogui
    import pytesseract
    from PIL import Image
    import cv2
    import numpy as np
    
    print("✅ All screen capture packages imported successfully")
    
    # Test tesseract path
    pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
    
    # Test OCR on a simple image
    print("🔍 Testing OCR...")
    
    # Get mouse position
    x, y = pyautogui.position()
    print(f"📍 Mouse position: {x}, {y}")
    
    # Take a small screenshot
    screenshot = pyautogui.screenshot(region=(x-50, y-50, 100, 100))
    
    # Test OCR
    text = pytesseract.image_to_string(screenshot)
    print(f"📝 OCR result: '{text.strip()}'")
    
    print("🎉 Screen capture system is working!")

except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
