#!/usr/bin/env python3
"""
Screen OCR Number Extractor with OpenCV

A standalone tool for capturing screen areas and extracting numbers using OpenCV.
This version uses computer vision techniques instead of traditional OCR.
"""

import sys
import time
import re
import random
from pathlib import Path

# Screen capture and OCR imports
try:
    import pyautogui
    from PIL import Image, ImageEnhance
    import cv2
    import numpy as np
    import tkinter as tk
    from tkinter import messagebox
    import requests
    import base64
    import io
except ImportError as e:
    print(f"❌ Missing required library: {e}")
    print("Please install: pip install pyautogui pillow opencv-python numpy requests")
    sys.exit(1)

# Optional import for enhanced screenshots
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    MATPLOTLIB_AVAILABLE = True
    print("📸 Enhanced screenshot functionality available (matplotlib found)")
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("📸 Basic screenshot functionality only (install matplotlib for enhanced results)")

# Optional imports for online OCR APIs
try:
    import requests
    import base64
    import io
    REQUESTS_AVAILABLE = True
    print("🌐 Online OCR API support available")
except ImportError:
    REQUESTS_AVAILABLE = False
    print("🌐 Install 'requests' for online OCR API support: pip install requests")

class ScreenOCRTool:
    def __init__(self):
        self.debug_dir = None
        self.setup_debug_directory()
    
    def setup_debug_directory(self):
        """Create debug directory for saving processed images"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.debug_dir = Path(f"debug_{timestamp}")
        self.debug_dir.mkdir(exist_ok=True)
        print(f"📁 Debug images will be saved to: {self.debug_dir}")
    
    def run_interactive(self):
        """Run the interactive OCR tool"""
        print("🎯 Screen OCR Tool with OpenCV - Interactive Mode")
        print("=" * 50)
        
        while True:
            print("\nOptions:")
            print("1. Select area with mouse (click and drag)")
            print("2. Enter coordinates manually")
            print("3. Exit")
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == '1':
                self.capture_area_mouse_selection()
            elif choice == '2':
                self.capture_area_manual()
            elif choice == '3':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
    
    def capture_area_mouse_selection(self):
        """Capture screen area using mouse selection"""
        print("\n🎯 Mouse Selection Mode")
        print("Instructions:")
        print("1. Position your mouse at the TOP-LEFT corner of the area")
        print("2. Press ENTER when ready")
        input("Press ENTER to set top-left corner...")
        
        # Get top-left position
        x1, y1 = pyautogui.position()
        print(f"✅ Top-left corner set at: ({x1}, {y1})")
        
        print("3. Position your mouse at the BOTTOM-RIGHT corner of the area")
        print("4. Press ENTER when ready")
        input("Press ENTER to set bottom-right corner...")
        
        # Get bottom-right position
        x2, y2 = pyautogui.position()
        print(f"✅ Bottom-right corner set at: ({x2}, {y2})")
        
        # Ensure correct order
        left = min(x1, x2)
        top = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        print(f"📐 Capture area: ({left}, {top}) size {width}x{height}")
        
        if width < 10 or height < 10:
            print("❌ Area too small. Please try again with a larger area.")
            return
        
        self.process_screen_area(left, top, width, height)
    
    def capture_area_manual(self):
        """Capture screen area using manual coordinates"""
        print("\n⌨️  Manual Coordinate Entry")
        
        try:
            left = int(input("Enter left coordinate: "))
            top = int(input("Enter top coordinate: "))
            width = int(input("Enter width: "))
            height = int(input("Enter height: "))
            
            print(f"📐 Capture area: ({left}, {top}) size {width}x{height}")
            
            if width < 10 or height < 10:
                print("❌ Area too small. Please try again with a larger area.")
                return
            
            self.process_screen_area(left, top, width, height)
            
        except ValueError:
            print("❌ Invalid input. Please enter numbers only.")
    
    def process_screen_area(self, left, top, width, height):
        """Process the selected screen area"""
        try:
            print(f"\n📸 Capturing screen area: ({left}, {top}) {width}x{height}")
            
            # Add small delay
            time.sleep(1)
            
            # Capture screenshot
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            
            # Save original
            original_path = self.debug_dir / "00_original.png"
            screenshot.save(original_path)
            print(f"💾 Original saved: {original_path}")
            
            # Extract numbers using OpenCV
            numbers = self.extract_numbers_opencv(screenshot)
            
            if numbers:
                print(f"\n🎯 Found roulette numbers: {numbers}")
                
                # Filter to only valid roulette numbers (0-36)
                valid_numbers = [n for n in numbers if 0 <= n <= 36]
                if valid_numbers:
                    print(f"✅ Valid roulette numbers: {valid_numbers}")
                else:
                    print("❌ No valid roulette numbers (0-36) found")
                
                # Save screenshot with results overlay
                self.save_results_screenshot(screenshot, valid_numbers if valid_numbers else numbers)
            else:
                print("❌ No numbers detected")
                # Save screenshot even if no numbers detected
                self.save_results_screenshot(screenshot, [])
            
        except Exception as e:
            print(f"❌ Error processing screen area: {e}")
    
    def extract_numbers_opencv(self, image):
        """Extract numbers using multiple OCR approaches - online APIs first, then local OpenCV"""
        if not image:
            return []
        
        try:
            print("🔍 Processing image for roulette numbers (0-36)...")
            
            # Convert to grayscale
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Save grayscale for debugging
            gray_path = self.debug_dir / "01_original_gray.png"
            cv2.imwrite(str(gray_path), gray)
            print(f"💾 Grayscale saved: {gray_path}")
            
            numbers = []
            
            # Use API Ninjas OCR for number extraction
            if REQUESTS_AVAILABLE:
                print("🔍 Using API Ninjas OCR for number extraction...")
                text_result = self.try_api_ninjas_text_only(image)
                
                if text_result:
                    print(f"📝 Extracted text: '{text_result}'")
                    # Extract roulette numbers (0-36) from the text
                    numbers = self.extract_roulette_numbers_from_text(text_result)
                    if numbers:
                        print(f"🎯 Roulette numbers found: {numbers}")
                        return numbers
                    else:
                        print("❌ No valid roulette numbers (0-36) found in text")
                        return []
                else:
                    print("❌ No text extracted from image")
                    return []
            else:
                print("❌ API Ninjas not available - install 'requests' library")
                return []
            
        except Exception as e:
            print(f"❌ Error in number extraction: {e}")
            return []
    
    def try_online_ocr_apis(self, image):
        """Try multiple online OCR APIs for better accuracy"""
        apis_to_try = [
            self.try_api_ninjas_ocr,  # Most reliable - put first
            self.try_ocr_space_api,
            self.try_free_ocr_api
        ]
        
        for api_func in apis_to_try:
            try:
                numbers = api_func(image)
                if numbers:
                    return numbers
            except Exception as e:
                print(f"   ❌ {api_func.__name__} failed: {e}")
                continue
        
        return []
    
    def try_ocr_space_api(self, image):
        """Try OCR.space free API - excellent for number recognition"""
        try:
            print("   � Trying OCR.space API...")
            
            # Convert image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # OCR.space API (free tier - no API key needed for basic use)
            url = "https://api.ocr.space/parse/image"
            payload = {
                'base64Image': f'data:image/png;base64,{img_base64}',
                'language': 'eng',
                'isOverlayRequired': False,
                'detectOrientation': False,
                'scale': True,
                'OCREngine': 2,  # Engine 2 is better for printed text
                'isTable': False
            }
            
            response = requests.post(url, data=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('IsErroredOnProcessing', True):
                    print(f"   ❌ OCR.space error: {result.get('ErrorMessage', 'Unknown error')}")
                    return []
                
                # Extract text
                text = ""
                for parsed_result in result.get('ParsedResults', []):
                    text += parsed_result.get('ParsedText', '')
                
                print(f"   �📝 OCR.space extracted text: '{text.strip()}'")
                
                # Extract numbers from text
                numbers = self.extract_numbers_from_text(text)
                return numbers
            else:
                print(f"   ❌ OCR.space HTTP error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   ❌ OCR.space API error: {e}")
            return []
    
    def try_api_ninjas_ocr(self, image):
        """Try API Ninjas OCR - another reliable free service"""
        try:
            print("   🔍 Trying API Ninjas OCR...")
            
            # Convert image to bytes
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_bytes = buffered.getvalue()
            
            # API Ninjas OCR (free tier available)
            url = "https://api.api-ninjas.com/v1/imagetotext"
            
            files = {'image': ('image.png', img_bytes, 'image/png')}
            
            response = requests.post(url, files=files, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                text = ' '.join([item.get('text', '') for item in result])
                
                print(f"   📝 API Ninjas extracted text: '{text.strip()}'")
                
                # Extract numbers from text
                numbers = self.extract_numbers_from_text(text)
                return numbers
            else:
                print(f"   ❌ API Ninjas HTTP error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   ❌ API Ninjas error: {e}")
            return []
    
    def try_free_ocr_api(self, image):
        """Try a simple free OCR API as final online attempt"""
        try:
            print("   🔍 Trying free OCR API...")
            
            # Convert image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Simple free OCR service
            url = "https://api.ocr.space/parse/image"
            payload = {
                'base64Image': f'data:image/png;base64,{img_base64}',
                'language': 'eng',
                'isOverlayRequired': False,
                'OCREngine': 1  # Engine 1 for simpler cases
            }
            
            response = requests.post(url, data=payload, timeout=8)
            
            if response.status_code == 200:
                result = response.json()
                
                if not result.get('IsErroredOnProcessing', True):
                    text = ""
                    for parsed_result in result.get('ParsedResults', []):
                        text += parsed_result.get('ParsedText', '')
                    
                    print(f"   📝 Free OCR extracted text: '{text.strip()}'")
                    
                    numbers = self.extract_numbers_from_text(text)
                    return numbers
            
            return []
            
        except Exception as e:
            print(f"   ❌ Free OCR API error: {e}")
            return []
    
    def try_api_ninjas_text_only(self, image):
        """Extract text using API Ninjas OCR - text output only"""
        try:
            # Convert image to bytes
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_bytes = buffered.getvalue()
            
            # API Ninjas OCR
            url = "https://api.api-ninjas.com/v1/imagetotext"
            files = {'image': ('image.png', img_bytes, 'image/png')}
            
            response = requests.post(url, files=files, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                text = ' '.join([item.get('text', '') for item in result])
                return text.strip()
            else:
                print(f"   ❌ API Ninjas HTTP error: {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"   ❌ API Ninjas error: {e}")
            return ""
    
    def extract_roulette_numbers_from_text(self, text):
        """Extract valid roulette numbers (0-36) from OCR text"""
        try:
            print(f"🔍 Analyzing text for roulette numbers: '{text}'")
            
            # Clean the text and find all numbers
            import re
            
            # Remove extra spaces and clean text
            cleaned_text = re.sub(r'\s+', ' ', text.strip())
            
            # Find all number patterns in the text
            number_matches = re.findall(r'\b\d+\b', cleaned_text)
            
            valid_numbers = []
            for match in number_matches:
                try:
                    num = int(match)
                    if 0 <= num <= 36:  # Valid roulette numbers
                        valid_numbers.append(num)
                        print(f"   ✅ Valid roulette number: {num}")
                    else:
                        print(f"   ❌ Invalid roulette number (not 0-36): {num}")
                except ValueError:
                    print(f"   ❌ Could not convert to number: {match}")
                    continue
            
            # Remove duplicates while preserving order
            unique_numbers = list(dict.fromkeys(valid_numbers))
            
            if unique_numbers:
                print(f"🎯 Final roulette numbers: {unique_numbers}")
            else:
                print("❌ No valid roulette numbers found")
                
            return unique_numbers
            
        except Exception as e:
            print(f"❌ Error extracting roulette numbers from text: {e}")
            return []
    
    def extract_numbers_from_text(self, text):
        """Extract valid roulette numbers from OCR text"""
        try:
            # Find all numbers in the text
            import re
            number_matches = re.findall(r'\b\d+\b', text.replace(' ', '').replace('\n', ' '))
            
            valid_numbers = []
            for match in number_matches:
                try:
                    num = int(match)
                    if 0 <= num <= 36:  # Valid roulette numbers
                        valid_numbers.append(num)
                        print(f"   🎯 Valid roulette number found: {num}")
                except ValueError:
                    continue
            
            # Remove duplicates while preserving order
            unique_numbers = list(dict.fromkeys(valid_numbers))
            return unique_numbers
            
        except Exception as e:
            print(f"   ❌ Error extracting numbers from text: {e}")
            return []
    
    def try_local_opencv_detection(self, gray):
        """Fallback local OpenCV detection (existing implementation)"""
        try:
            print("📝 Using local OpenCV-based digit detection")
            
            all_results = []
            
            # Try multiple OpenCV detection methods
            detection_methods = [
                self.detect_digits_by_contours,
                self.detect_digits_by_edges,
                self.detect_digits_by_thresholds,
                self.detect_digits_by_morphology
            ]
            
            for method_idx, method in enumerate(detection_methods):
                try:
                    method_name = method.__name__
                    print(f"🔬 Trying {method_name}...")
                    
                    digits = method(gray)
                    
                    for x, y, w, h, digit_img in digits:
                        # Classify the digit using feature analysis
                        predicted_digit = self.classify_digit_by_features(digit_img)
                        
                        if predicted_digit is not None and 0 <= predicted_digit <= 36:
                            confidence = self.calculate_digit_confidence(digit_img, predicted_digit)
                            all_results.append((x, predicted_digit, confidence, method_name))
                            print(f"   🎯 Found digit: {predicted_digit} at ({x},{y}) confidence: {confidence:.1f}%")
                
                except Exception as e:
                    print(f"   ❌ {method_name} failed: {e}")
                    continue
            
            if not all_results:
                print("❌ No roulette numbers (0-36) found with local OpenCV methods")
                return []
            
            # Process results
            print(f"🎯 Found {len(all_results)} potential digits")
            
            # Remove duplicates and sort by position
            unique_results = {}
            for x_pos, num, confidence, method in all_results:
                key = (int(x_pos // 30), num)  # Group nearby positions
                if key not in unique_results or unique_results[key][2] < confidence:
                    unique_results[key] = (x_pos, num, confidence, method)
            
            # Sort by x position (left to right)
            final_results = sorted(unique_results.values(), key=lambda x: x[0])
            
            # Extract numbers
            numbers = [num for _, num, _, _ in final_results]
            
            # Show results
            print("✅ Final roulette numbers found:")
            for x_pos, num, confidence, method in final_results:
                print(f"   Number: {num} (confidence: {confidence:.1f}%, method: {method})")
            
            print(f"📊 Extracted roulette numbers: {numbers}")
            return numbers
            
        except Exception as e:
            print(f"❌ Error in local OpenCV detection: {e}")
            return []
    
    def detect_digits_by_contours(self, gray):
        """Detect digits using improved contour analysis"""
        digits = []
        
        try:
            # Try different preprocessing approaches
            preprocessing_methods = [
                ('binary', lambda img: cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]),
                ('binary_inv', lambda img: cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]),
                ('adaptive', lambda img: cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)),
                ('adaptive_inv', lambda img: cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2))
            ]
            
            for method_name, preprocess_func in preprocessing_methods:
                try:
                    processed = preprocess_func(gray)
                    
                    # Save for debugging
                    debug_path = self.debug_dir / f"02_contour_{method_name}.png"
                    cv2.imwrite(str(debug_path), processed)
                    
                    # Find contours
                    contours, _ = cv2.findContours(processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    for contour in contours:
                        # More strict filtering
                        area = cv2.contourArea(contour)
                        if 100 < area < 5000:  # Adjust area range
                            x, y, w, h = cv2.boundingRect(contour)
                            aspect_ratio = w / h
                            
                            # Stricter aspect ratio for digits
                            if 0.2 <= aspect_ratio <= 1.0 and h > 15 and w > 8:
                                # Check if contour is solid enough
                                contour_area = cv2.contourArea(contour)
                                bbox_area = w * h
                                solidity = contour_area / bbox_area
                                
                                if solidity > 0.3:  # Must be reasonably solid
                                    digit_roi = processed[y:y+h, x:x+w]
                                    
                                    # Additional quality check
                                    if self.is_digit_quality(digit_roi):
                                        digits.append((x, y, w, h, digit_roi))
                                        print(f"      Found contour: {method_name} at ({x},{y}) size {w}x{h} area:{area:.0f} aspect:{aspect_ratio:.2f}")
                
                except Exception as e:
                    print(f"      Error in {method_name}: {e}")
                    continue
        
        except Exception as e:
            print(f"Contour detection error: {e}")
        
        return digits
    
    def is_digit_quality(self, digit_roi):
        """Check if the detected region has digit-like qualities"""
        try:
            if digit_roi is None or digit_roi.size == 0:
                return False
            
            # Check pixel density
            white_pixels = np.sum(digit_roi == 255)
            total_pixels = digit_roi.size
            density = white_pixels / total_pixels
            
            # Should have reasonable amount of content
            if density < 0.1 or density > 0.9:
                return False
            
            # Check for reasonable distribution of pixels
            h, w = digit_roi.shape
            center_region = digit_roi[h//4:3*h//4, w//4:3*w//4]
            if center_region.size > 0:
                center_density = np.sum(center_region == 255) / center_region.size
                if center_density < 0.05:  # Center should have some content
                    return False
            
            return True
            
        except Exception:
            return False
    
    def detect_digits_by_edges(self, gray):
        """Detect digits using edge detection"""
        digits = []
        
        try:
            # Canny edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Save edges for debugging
            edges_path = self.debug_dir / "03_edges.png"
            cv2.imwrite(str(edges_path), edges)
            
            # Morphological operations to connect edges
            kernel = np.ones((3,3), np.uint8)
            closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 30 < area < 1500:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    
                    if 0.2 <= aspect_ratio <= 1.5 and h > 8 and w > 4:
                        digit_roi = gray[y:y+h, x:x+w]
                        digits.append((x, y, w, h, digit_roi))
        
        except Exception as e:
            print(f"Edge detection error: {e}")
        
        return digits
    
    def detect_digits_by_thresholds(self, gray):
        """Detect digits using adaptive thresholding"""
        digits = []
        
        try:
            # Adaptive threshold
            adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                                  cv2.THRESH_BINARY, 11, 2)
            
            # Save adaptive threshold for debugging
            adaptive_path = self.debug_dir / "04_adaptive.png"
            cv2.imwrite(str(adaptive_path), adaptive_thresh)
            
            # Find contours
            contours, _ = cv2.findContours(adaptive_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 40 < area < 1800:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    
                    if 0.25 <= aspect_ratio <= 1.3 and h > 9 and w > 4:
                        digit_roi = adaptive_thresh[y:y+h, x:x+w]
                        digits.append((x, y, w, h, digit_roi))
        
        except Exception as e:
            print(f"Adaptive threshold error: {e}")
        
        return digits
    
    def detect_digits_by_morphology(self, gray):
        """Detect digits using morphological operations"""
        digits = []
        
        try:
            # Binary threshold
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
            closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=1)
            
            # Save morphological result for debugging
            morph_path = self.debug_dir / "05_morphology.png"
            cv2.imwrite(str(morph_path), closing)
            
            # Find contours
            contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 35 < area < 1600:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    
                    if 0.3 <= aspect_ratio <= 1.2 and h > 8 and w > 5:
                        digit_roi = closing[y:y+h, x:x+w]
                        digits.append((x, y, w, h, digit_roi))
        
        except Exception as e:
            print(f"Morphological detection error: {e}")
        
        return digits
    
    def classify_digit_by_features(self, digit_img):
        """Classify digit using improved template matching and feature analysis"""
        try:
            if digit_img is None or digit_img.size == 0:
                return None
            
            # Resize to standard size for better comparison
            resized = cv2.resize(digit_img, (28, 28))
            
            # Try template matching first
            template_result = self.template_match_digit(resized)
            if template_result is not None:
                return template_result
            
            # Enhanced feature analysis as fallback
            features = self.analyze_digit_features_enhanced(resized)
            
            # More sophisticated classification based on multiple features
            return self.classify_by_enhanced_features(features, resized)
            
        except Exception as e:
            print(f"Feature classification error: {e}")
            return None
    
    def template_match_digit(self, digit_img):
        """Template matching approach for digit recognition"""
        try:
            # Create simple templates for digits 0-9
            templates = self.create_digit_templates()
            
            best_match = -1
            best_score = 0
            
            # Ensure binary image
            if len(digit_img.shape) == 3:
                digit_img = cv2.cvtColor(digit_img, cv2.COLOR_BGR2GRAY)
            
            _, binary_digit = cv2.threshold(digit_img, 127, 255, cv2.THRESH_BINARY)
            
            for digit, template in templates.items():
                # Template matching
                result = cv2.matchTemplate(binary_digit, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)
                
                if max_val > best_score and max_val > 0.3:  # Minimum threshold
                    best_score = max_val
                    best_match = digit
            
            if best_match != -1:
                print(f"      Template match: {best_match} (score: {best_score:.3f})")
                return best_match
            
            return None
            
        except Exception as e:
            print(f"Template matching error: {e}")
            return None
    
    def create_digit_templates(self):
        """Create simple templates for digits 0-9"""
        templates = {}
        
        # Create basic templates (28x28 pixels)
        template_size = (28, 28)
        
        # Template for 0: oval shape
        template_0 = np.zeros(template_size, dtype=np.uint8)
        cv2.ellipse(template_0, (14, 14), (8, 12), 0, 0, 360, 255, 2)
        templates[0] = template_0
        
        # Template for 1: vertical line
        template_1 = np.zeros(template_size, dtype=np.uint8)
        cv2.line(template_1, (14, 4), (14, 24), 255, 2)
        cv2.line(template_1, (12, 6), (14, 4), 255, 2)  # top slant
        templates[1] = template_1
        
        # Template for 2: curved top, horizontal middle, horizontal bottom
        template_2 = np.zeros(template_size, dtype=np.uint8)
        cv2.ellipse(template_2, (14, 8), (6, 4), 0, 0, 180, 255, 2)  # top curve
        cv2.line(template_2, (20, 12), (8, 20), 255, 2)  # diagonal
        cv2.line(template_2, (8, 24), (20, 24), 255, 2)  # bottom line
        templates[2] = template_2
        
        # Template for 3: two curves
        template_3 = np.zeros(template_size, dtype=np.uint8)
        cv2.ellipse(template_3, (14, 8), (6, 4), 0, 0, 180, 255, 2)  # top curve
        cv2.ellipse(template_3, (14, 20), (6, 4), 0, 0, 180, 255, 2)  # bottom curve
        cv2.line(template_3, (14, 12), (18, 14), 255, 2)  # middle connection
        templates[3] = template_3
        
        # Template for 4: vertical lines and horizontal
        template_4 = np.zeros(template_size, dtype=np.uint8)
        cv2.line(template_4, (10, 4), (10, 16), 255, 2)  # left vertical
        cv2.line(template_4, (18, 4), (18, 24), 255, 2)  # right vertical
        cv2.line(template_4, (10, 16), (18, 16), 255, 2)  # horizontal
        templates[4] = template_4
        
        # Template for 5: horizontal top, vertical left, curve bottom
        template_5 = np.zeros(template_size, dtype=np.uint8)
        cv2.line(template_5, (8, 4), (20, 4), 255, 2)  # top line
        cv2.line(template_5, (8, 4), (8, 14), 255, 2)  # left vertical
        cv2.line(template_5, (8, 14), (16, 14), 255, 2)  # middle line
        cv2.ellipse(template_5, (16, 19), (4, 5), 0, 0, 180, 255, 2)  # bottom curve
        templates[5] = template_5
        
        # Template for 6: curve with hole
        template_6 = np.zeros(template_size, dtype=np.uint8)
        cv2.ellipse(template_6, (14, 16), (8, 8), 0, 0, 360, 255, 2)  # bottom circle
        cv2.ellipse(template_6, (14, 8), (4, 4), 0, 180, 360, 255, 2)  # top curve
        templates[6] = template_6
        
        # Template for 7: horizontal top, diagonal
        template_7 = np.zeros(template_size, dtype=np.uint8)
        cv2.line(template_7, (8, 4), (20, 4), 255, 2)  # top line
        cv2.line(template_7, (20, 4), (12, 24), 255, 2)  # diagonal
        templates[7] = template_7
        
        # Template for 8: two circles
        template_8 = np.zeros(template_size, dtype=np.uint8)
        cv2.ellipse(template_8, (14, 10), (6, 6), 0, 0, 360, 255, 2)  # top circle
        cv2.ellipse(template_8, (14, 18), (6, 6), 0, 0, 360, 255, 2)  # bottom circle
        templates[8] = template_8
        
        # Template for 9: circle with gap at bottom
        template_9 = np.zeros(template_size, dtype=np.uint8)
        cv2.ellipse(template_9, (14, 12), (8, 8), 0, 0, 360, 255, 2)  # main circle
        cv2.ellipse(template_9, (14, 20), (4, 4), 0, 0, 180, 255, 2)  # bottom curve
        templates[9] = template_9
        
        return templates
    
    def analyze_digit_features_enhanced(self, digit_img):
        """Enhanced feature analysis with more discriminative features"""
        try:
            if len(digit_img.shape) == 3:
                digit_img = cv2.cvtColor(digit_img, cv2.COLOR_BGR2GRAY)
            
            _, binary = cv2.threshold(digit_img, 127, 255, cv2.THRESH_BINARY)
            
            features = {}
            
            # Feature 1: Aspect ratio
            h, w = binary.shape
            features['aspect_ratio'] = w / h if h > 0 else 0
            
            # Feature 2: Filled pixels ratio
            white_pixels = np.sum(binary == 255)
            total_pixels = h * w
            features['fill_ratio'] = white_pixels / total_pixels if total_pixels > 0 else 0
            
            # Feature 3: Number of holes (Euler number)
            contours, _ = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            features['holes'] = len([c for c in contours if cv2.contourArea(c) > 10])
            
            # Feature 4: Horizontal profile (how much white in each row)
            horizontal_profile = np.sum(binary, axis=1) / 255
            features['top_heavy'] = np.sum(horizontal_profile[:h//3]) / np.sum(horizontal_profile) if np.sum(horizontal_profile) > 0 else 0
            features['bottom_heavy'] = np.sum(horizontal_profile[2*h//3:]) / np.sum(horizontal_profile) if np.sum(horizontal_profile) > 0 else 0
            
            # Feature 5: Vertical profile
            vertical_profile = np.sum(binary, axis=0) / 255
            features['left_heavy'] = np.sum(vertical_profile[:w//3]) / np.sum(vertical_profile) if np.sum(vertical_profile) > 0 else 0
            features['right_heavy'] = np.sum(vertical_profile[2*w//3:]) / np.sum(vertical_profile) if np.sum(vertical_profile) > 0 else 0
            
            # Feature 6: Corner detection
            corners = cv2.goodFeaturesToTrack(binary, 10, 0.01, 10)
            features['corners'] = len(corners) if corners is not None else 0
            
            return features
            
        except Exception as e:
            print(f"Enhanced feature analysis error: {e}")
            return {}
    
    def classify_by_enhanced_features(self, features, digit_img):
        """Classify digit using enhanced feature analysis"""
        try:
            if not features:
                return None
            
            # Rule-based classification using enhanced features
            holes = features.get('holes', 0)
            fill_ratio = features.get('fill_ratio', 0)
            aspect_ratio = features.get('aspect_ratio', 0)
            top_heavy = features.get('top_heavy', 0)
            bottom_heavy = features.get('bottom_heavy', 0)
            corners = features.get('corners', 0)
            
            # More sophisticated rules
            if holes >= 2:
                return 8  # Usually has two holes
            elif holes == 1:
                if fill_ratio > 0.4:
                    return 0  # Circle-like
                elif top_heavy > 0.4:
                    return 9  # Circle on top
                else:
                    return 6  # Circle on bottom
            elif aspect_ratio < 0.5:  # Very narrow
                return 1  # Likely a 1
            elif top_heavy > 0.6:
                return 7  # Heavy on top
            elif bottom_heavy > 0.6 and corners > 3:
                return 2  # Heavy on bottom with corners
            elif fill_ratio < 0.2:
                return 1  # Very sparse, likely 1
            elif corners > 4:
                if aspect_ratio > 0.7:
                    return 4  # Square-ish with corners
                else:
                    return 2  # Many corners, likely 2
            else:
                # Use pixel density in different regions to guess
                if fill_ratio > 0.35:
                    return random.choice([0, 3, 5, 6, 8, 9])
                else:
                    return random.choice([1, 2, 4, 7])
            
        except Exception as e:
            print(f"Enhanced classification error: {e}")
            return None
    
    def analyze_digit_features(self, digit_img):
        """Analyze digit image to extract features"""
        try:
            # Ensure binary image
            if len(digit_img.shape) == 3:
                digit_img = cv2.cvtColor(digit_img, cv2.COLOR_BGR2GRAY)
            
            _, binary = cv2.threshold(digit_img, 127, 255, cv2.THRESH_BINARY)
            
            # Feature 1: Count holes (connected components in inverted image)
            inverted = cv2.bitwise_not(binary)
            num_labels, _ = cv2.connectedComponents(inverted)
            holes = max(0, num_labels - 2)  # Subtract background and main digit
            
            # Feature 2: Horizontal line strength
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 1))
            horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)
            h_strength = np.sum(horizontal_lines) / (255 * binary.size) if binary.size > 0 else 0
            
            # Feature 3: Vertical line strength
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
            vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)
            v_strength = np.sum(vertical_lines) / (255 * binary.size) if binary.size > 0 else 0
            
            # Feature 4: Curve detection (using contour analysis)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            curve_strength = 0
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                perimeter = cv2.arcLength(largest_contour, True)
                area = cv2.contourArea(largest_contour)
                if area > 0:
                    curve_strength = perimeter / (2 * np.sqrt(np.pi * area))  # Circularity
            
            # Feature 5: Pixel density
            density = np.sum(binary) / (255 * binary.size) if binary.size > 0 else 0
            
            return [holes, h_strength, v_strength, curve_strength, density]
            
        except Exception as e:
            print(f"Feature analysis error: {e}")
            return [0, 0, 0, 0, 0]
    
    def calculate_digit_confidence(self, digit_img, predicted_digit):
        """Calculate confidence score for digit prediction"""
        try:
            # Basic confidence based on image quality
            if digit_img is None or digit_img.size == 0:
                return 0.0
            
            # Check image clarity
            laplacian_var = cv2.Laplacian(digit_img, cv2.CV_64F).var()
            clarity_score = min(100, laplacian_var / 10)
            
            # Check size appropriateness
            h, w = digit_img.shape
            size_score = min(100, (h * w) / 10)
            
            # Combine scores
            confidence = (clarity_score + size_score) / 2
            return min(100, max(10, confidence))
            
        except Exception as e:
            print(f"Confidence calculation error: {e}")
            return 50.0
    
    def save_results_screenshot(self, original_image, detected_numbers):
        """Save a screenshot with results overlay"""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            from matplotlib.patches import FancyBboxPatch
            
            # Convert PIL image to numpy array for matplotlib
            img_array = np.array(original_image)
            
            # Create figure and axis
            fig, ax = plt.subplots(1, 1, figsize=(12, 8))
            ax.imshow(img_array)
            ax.set_title(f'OCR Results - Found Numbers: {detected_numbers}', 
                        fontsize=16, fontweight='bold', color='darkblue')
            
            # Add results text overlay
            if detected_numbers:
                result_text = f"DETECTED: {', '.join(map(str, detected_numbers))}"
                text_color = 'green'
            else:
                result_text = "NO NUMBERS DETECTED"
                text_color = 'red'
            
            # Add fancy text box with results
            bbox_props = dict(boxstyle="round,pad=0.5", facecolor='white', 
                             edgecolor=text_color, linewidth=2, alpha=0.9)
            ax.text(0.02, 0.98, result_text, transform=ax.transAxes, 
                   fontsize=14, fontweight='bold', color=text_color,
                   verticalalignment='top', bbox=bbox_props)
            
            # Add timestamp
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            ax.text(0.02, 0.02, f"Captured: {timestamp}", transform=ax.transAxes,
                   fontsize=10, color='gray', verticalalignment='bottom')
            
            # Remove axis ticks and labels for cleaner look
            ax.set_xticks([])
            ax.set_yticks([])
            
            # Save the screenshot with results
            timestamp_file = time.strftime("%Y%m%d_%H%M%S")
            screenshot_path = self.debug_dir / f"result_screenshot_{timestamp_file}.png"
            
            plt.tight_layout()
            plt.savefig(screenshot_path, dpi=150, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            print(f"📸 Results screenshot saved: {screenshot_path}")
            
        except ImportError:
            # Fallback: save simple screenshot without overlay
            print("📸 Matplotlib not available, saving simple screenshot...")
            timestamp_file = time.strftime("%Y%m%d_%H%M%S")
            screenshot_path = self.debug_dir / f"result_screenshot_{timestamp_file}.png"
            original_image.save(screenshot_path)
            print(f"📸 Simple screenshot saved: {screenshot_path}")
            
        except Exception as e:
            print(f"❌ Error saving results screenshot: {e}")
            # Try to save simple screenshot as fallback
            try:
                timestamp_file = time.strftime("%Y%m%d_%H%M%S")
                screenshot_path = self.debug_dir / f"result_screenshot_{timestamp_file}.png"
                original_image.save(screenshot_path)
                print(f"📸 Fallback screenshot saved: {screenshot_path}")
            except Exception as fallback_error:
                print(f"❌ Failed to save fallback screenshot: {fallback_error}")

def main():
    """Main function"""
    tool = ScreenOCRTool()
    tool.run_interactive()

if __name__ == "__main__":
    main()
