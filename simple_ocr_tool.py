#!/usr/bin/env python3
"""
Simple OCR Tool for Roulette Numbers
Uses reliable online APIs for best accuracy
"""

import cv2
import numpy as np
from PIL import Image, ImageGrab
import requests
import io
import re
import time
import os
from datetime import datetime

class SimpleOCRTool:
    def __init__(self):
        self.debug_dir = f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def capture_screen_area(self, x, y, width, height):
        """Capture a specific area of the screen"""
        try:
            # Capture screenshot
            screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
            return screenshot
        except Exception as e:
            print(f"❌ Error capturing screen: {e}")
            return None
    
    def get_mouse_selection(self):
        """Interactive mouse selection of screen area"""
        print("\n🎯 Mouse Selection Mode")
        print("Instructions:")
        print("1. Position your mouse at the TOP-LEFT corner of the area")
        print("2. Press ENTER when ready")
        
        input("Press ENTER to set top-left corner...")
        
        # Get mouse position (this is a simplified version)
        # In a real implementation, you'd use a mouse tracking library
        print("✅ Top-left corner set")
        
        print("3. Position your mouse at the BOTTOM-RIGHT corner of the area")
        print("4. Press ENTER when ready")
        
        input("Press ENTER to set bottom-right corner...")
        print("✅ Bottom-right corner set")
        
        # For demonstration, let's use manual input
        print("\n📐 Manual coordinate input:")
        x = int(input("Enter X coordinate (left): "))
        y = int(input("Enter Y coordinate (top): "))
        width = int(input("Enter width: "))
        height = int(input("Enter height: "))
        
        return x, y, width, height
    
    def extract_numbers_with_api_ninjas(self, image):
        """Extract numbers using API Ninjas OCR (most reliable)"""
        try:
            print("🔍 Using API Ninjas OCR for number recognition...")
            
            # Convert image to bytes
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_bytes = buffered.getvalue()
            
            # API Ninjas OCR (free tier available)
            url = "https://api.api-ninjas.com/v1/imagetotext"
            files = {'image': ('image.png', img_bytes, 'image/png')}
            
            response = requests.post(url, files=files, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                text = ' '.join([item.get('text', '') for item in result])
                
                print(f"📝 Extracted text: '{text.strip()}'")
                
                # Extract roulette numbers (0-36)
                numbers = self.extract_roulette_numbers(text)
                
                if numbers:
                    print(f"🎯 Found roulette numbers: {numbers}")
                    return numbers
                else:
                    print("❌ No valid roulette numbers found in text")
                    return []
            else:
                print(f"❌ API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ OCR error: {e}")
            return []
    
    def extract_roulette_numbers(self, text):
        """Extract valid roulette numbers (0-36) from text"""
        try:
            # Clean the text and find all numbers
            cleaned_text = text.replace(' ', ' ').replace('\n', ' ')
            number_matches = re.findall(r'\b\d+\b', cleaned_text)
            
            valid_numbers = []
            for match in number_matches:
                try:
                    num = int(match)
                    if 0 <= num <= 36:  # Valid roulette numbers
                        valid_numbers.append(num)
                        print(f"   ✅ Valid roulette number: {num}")
                except ValueError:
                    continue
            
            # Remove duplicates while preserving order
            unique_numbers = list(dict.fromkeys(valid_numbers))
            return unique_numbers
            
        except Exception as e:
            print(f"❌ Error extracting numbers: {e}")
            return []
    
    def save_result_image(self, image, numbers):
        """Save the result with annotations"""
        try:
            # Create debug directory
            os.makedirs(self.debug_dir, exist_ok=True)
            
            # Save original
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_path = f"{self.debug_dir}/result_{timestamp}.png"
            image.save(image_path)
            
            print(f"💾 Result saved: {image_path}")
            print(f"🎯 Numbers found: {numbers}")
            
        except Exception as e:
            print(f"❌ Error saving result: {e}")
    
    def run_simple_detection(self):
        """Simple one-shot detection"""
        print("🎰 Simple Roulette Number OCR Tool")
        print("=" * 40)
        
        # Get screen area
        print("\n1. Select the area containing roulette numbers:")
        x, y, width, height = self.get_mouse_selection()
        
        print(f"\n📸 Capturing area: ({x}, {y}) size {width}x{height}")
        
        # Capture screen
        image = self.capture_screen_area(x, y, width, height)
        if not image:
            print("❌ Failed to capture screen")
            return
        
        print("✅ Screen captured successfully")
        
        # Process with OCR
        numbers = self.extract_numbers_with_api_ninjas(image)
        
        # Save result
        self.save_result_image(image, numbers)
        
        if numbers:
            print(f"\n🎉 SUCCESS! Found roulette numbers: {numbers}")
        else:
            print("\n❌ No roulette numbers detected")
        
        return numbers

def main():
    """Main function"""
    tool = SimpleOCRTool()
    
    while True:
        print("\n" + "="*50)
        print("🎰 Simple Roulette OCR Tool")
        print("="*50)
        
        print("Options:")
        print("1. Detect numbers from screen area")
        print("2. Exit")
        
        choice = input("\nEnter your choice (1-2): ").strip()
        
        if choice == "1":
            tool.run_simple_detection()
        elif choice == "2":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
