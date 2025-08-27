#!/usr/bin/env python3
"""
Roulette Number Extractor - API Ninjas Only
Simple tool to extract roulette numbers (0-36) from screen areas using API Ninjas OCR
"""

import requests
import re
from PIL import Image, ImageGrab
import io
import time

def capture_screen_area(x, y, width, height):
    """Capture a specific area of the screen"""
    try:
        screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        return screenshot
    except Exception as e:
        print(f"❌ Error capturing screen: {e}")
        return None

def extract_text_with_ninja_api(image):
    """Extract text from image using API Ninjas OCR"""
    try:
        print("🔍 Using API Ninjas OCR to extract text...")
        
        # Convert image to bytes
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        
        # API Ninjas OCR request
        url = "https://api.api-ninjas.com/v1/imagetotext"
        files = {'image': ('image.png', img_bytes, 'image/png')}
        
        response = requests.post(url, files=files, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            text = ' '.join([item.get('text', '') for item in result])
            return text.strip()
        else:
            print(f"❌ API error: HTTP {response.status_code}")
            return ""
            
    except Exception as e:
        print(f"❌ OCR error: {e}")
        return ""

def extract_roulette_numbers(text):
    """Extract roulette numbers (0-36) from text"""
    try:
        print(f"📝 Extracted text: '{text}'")
        
        if not text:
            print("❌ No text to analyze")
            return []
        
        # Find all numbers in the text
        number_matches = re.findall(r'\b\d+\b', text)
        
        valid_numbers = []
        for match in number_matches:
            try:
                num = int(match)
                if 0 <= num <= 36:  # Valid roulette numbers
                    valid_numbers.append(num)
                    print(f"   ✅ Found roulette number: {num}")
                else:
                    print(f"   ❌ Number out of range (0-36): {num}")
            except ValueError:
                continue
        
        # Remove duplicates while preserving order
        unique_numbers = list(dict.fromkeys(valid_numbers))
        
        return unique_numbers
        
    except Exception as e:
        print(f"❌ Error extracting numbers: {e}")
        return []

def main():
    """Main function for interactive roulette number extraction"""
    print("🎰 Roulette Number Extractor - API Ninjas")
    print("=" * 45)
    
    while True:
        print("\nOptions:")
        print("1. Extract numbers from screen area")
        print("2. Exit")
        
        choice = input("\nEnter choice (1-2): ").strip()
        
        if choice == "1":
            try:
                print("\n📐 Enter screen coordinates:")
                x = int(input("X position (left): "))
                y = int(input("Y position (top): "))
                width = int(input("Width: "))
                height = int(input("Height: "))
                
                print(f"\n📸 Capturing area: ({x},{y}) size {width}x{height}")
                
                # Capture screen
                image = capture_screen_area(x, y, width, height)
                if not image:
                    continue
                
                # Extract text with API Ninjas
                text = extract_text_with_ninja_api(image)
                
                # Extract roulette numbers from text
                numbers = extract_roulette_numbers(text)
                
                # Display results
                if numbers:
                    print(f"\n🎯 ROULETTE NUMBERS FOUND: {numbers}")
                    print(f"📊 Total count: {len(numbers)}")
                    
                    # Show unique numbers
                    unique_set = set(numbers)
                    if len(unique_set) != len(numbers):
                        print(f"🔢 Unique numbers: {sorted(unique_set)}")
                else:
                    print("\n❌ No roulette numbers found")
                
            except ValueError:
                print("❌ Invalid coordinates. Please enter numbers only.")
            except KeyboardInterrupt:
                print("\n👋 Cancelled")
                
        elif choice == "2":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
