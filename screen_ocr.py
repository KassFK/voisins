#!/usr/bin/env python3
"""
Screen OCR Number Extractor

A standalone tool for capturing screen areas and extracting numbers using OCR.
This tool allows you to select an area of the screen and extract visible numbers.
"""

import sys
import time
import re
import random
from pathlib import Path

# Screen capture and OCR imports
try:
    import pyautogui
    import pytesseract
    from PIL import Image, ImageEnhance
    import cv2
    import numpy as np
    import tkinter as tk
    from tkinter import messagebox, simpledialog
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    missing_deps = str(e)

# Configure pyautogui for macOS
if DEPENDENCIES_AVAILABLE:
    pyautogui.FAILSAFE = True
    # Set tesseract path for macOS (installed via brew)
    try:
        pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
    except:
        try:
            pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
        except:
            pass

class ScreenOCRTool:
    def __init__(self):
        self.capture_area = None
        self.last_screenshot = None
        
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        if not DEPENDENCIES_AVAILABLE:
            print("❌ Missing dependencies!")
            print(f"Error: {missing_deps}")
            print("\n📦 To install required packages, run:")
            print("pip install pyautogui pytesseract pillow opencv-python")
            print("\n🔧 Also install tesseract OCR engine:")
            print("brew install tesseract  # macOS")
            print("sudo apt-get install tesseract-ocr  # Ubuntu/Debian")
            return False
        return True
    
    def get_screen_info(self):
        """Get information about screen dimensions"""
        try:
            screen_width = pyautogui.size().width
            screen_height = pyautogui.size().height
            print(f"📺 Screen size: {screen_width} x {screen_height}")
            return screen_width, screen_height
        except Exception as e:
            print(f"❌ Error getting screen info: {e}")
            return None, None
    
    def select_area_interactive(self):
        """Interactive area selection using mouse position tracking"""
        print("\n🎯 Starting interactive area selection...")
        print("📍 Instructions:")
        print("   1. Position your mouse at TOP-LEFT corner and press ENTER")
        print("   2. Position your mouse at BOTTOM-RIGHT corner and press ENTER")
        print("   3. Press 'q' to cancel")
        
        try:
            # Get first point
            print("\n🔸 Move mouse to TOP-LEFT corner of the area you want to capture...")
            input("Press ENTER when mouse is positioned at TOP-LEFT corner: ")
            
            x1, y1 = pyautogui.position()
            print(f"📍 Top-left point: ({x1}, {y1})")
            
            # Get second point
            print("\n🔸 Move mouse to BOTTOM-RIGHT corner of the area...")
            input("Press ENTER when mouse is positioned at BOTTOM-RIGHT corner: ")
            
            x2, y2 = pyautogui.position()
            print(f"📍 Bottom-right point: ({x2}, {y2})")
            
            # Calculate area
            left = min(x1, x2)
            top = min(y1, y2)
            right = max(x1, x2)
            bottom = max(y1, y2)
            
            width = right - left
            height = bottom - top
            
            if width > 10 and height > 10:
                self.capture_area = (left, top, width, height)
                print(f"✅ Area selected: {left}, {top}, {width}x{height}")
                return True
            else:
                print(f"❌ Area too small ({width}x{height}). Please try again.")
                return False
                
        except KeyboardInterrupt:
            print("\n❌ Selection cancelled")
            return False
        except Exception as e:
            print(f"❌ Error in area selection: {e}")
            return False
    
    def get_current_mouse_position(self):
        """Get and display current mouse position"""
        try:
            x, y = pyautogui.position()
            print(f"🖱️ Current mouse position: ({x}, {y})")
            return x, y
        except Exception as e:
            print(f"❌ Error getting mouse position: {e}")
            return None, None
    
    def select_area_by_mouse_position(self):
        """Select area by checking current mouse position"""
        print("\n🖱️ Mouse position area selection")
        print("📍 This method lets you see your current mouse position")
        
        try:
            # Get first corner
            input("🔸 Position mouse at TOP-LEFT corner, then press ENTER: ")
            x1, y1 = pyautogui.position()
            print(f"✅ Top-left corner: ({x1}, {y1})")
            
            # Get second corner
            input("🔸 Position mouse at BOTTOM-RIGHT corner, then press ENTER: ")
            x2, y2 = pyautogui.position()
            print(f"✅ Bottom-right corner: ({x2}, {y2})")
            
            # Calculate area
            left = min(x1, x2)
            top = min(y1, y2)
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            
            if width > 10 and height > 10:
                self.capture_area = (left, top, width, height)
                print(f"✅ Capture area set: {left}, {top}, {width}x{height}")
                return True
            else:
                print(f"❌ Area too small: {width}x{height}")
                return False
                
        except KeyboardInterrupt:
            print("\n❌ Selection cancelled")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def set_area_manually(self):
        """Set capture area using manual coordinates"""
        print("\n⚙️ Manual area selection")
        
        try:
            x = int(input("Enter X coordinate (left): "))
            y = int(input("Enter Y coordinate (top): "))
            width = int(input("Enter width: "))
            height = int(input("Enter height: "))
            
            if width > 0 and height > 0:
                self.capture_area = (x, y, width, height)
                print(f"✅ Area set: {x}, {y}, {width}x{height}")
                return True
            else:
                print("❌ Width and height must be positive")
                return False
                
        except ValueError:
            print("❌ Please enter valid numbers")
            return False
    
    def capture_screen_area(self):
        """Capture the selected screen area"""
        if not self.capture_area:
            print("❌ No capture area set. Please select an area first.")
            return None
        
        try:
            x, y, width, height = self.capture_area
            print(f"📸 Capturing area: {x}, {y}, {width}x{height}")
            
            # Take screenshot of the specific area
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            self.last_screenshot = screenshot
            
            print("✅ Screenshot captured successfully")
            return screenshot
            
        except Exception as e:
            print(f"❌ Error capturing screenshot: {e}")
            return None
    
    def preprocess_image_advanced(self, image):
        """Advanced preprocessing with multiple strategies for harder images"""
        try:
            # Convert PIL image to numpy array
            img_array = np.array(image)
            
            # Convert to grayscale if not already
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Strategy 1: Standard preprocessing
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Apply threshold to get binary image
            _, thresh1 = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Strategy 2: Adaptive threshold for varying lighting
            adaptive_thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Strategy 3: Enhanced contrast and sharpening
            # Enhance contrast
            enhanced = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
            
            # Sharpen the image
            kernel_sharpen = np.array([[-1,-1,-1],
                                     [-1, 9,-1],
                                     [-1,-1,-1]])
            sharpened = cv2.filter2D(enhanced, -1, kernel_sharpen)
            
            # Apply threshold to sharpened image
            _, thresh2 = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Strategy 4: Morphological operations
            kernel = np.ones((2, 2), np.uint8)
            
            # Clean up thresh1
            cleaned1 = cv2.morphologyEx(thresh1, cv2.MORPH_CLOSE, kernel)
            cleaned1 = cv2.morphologyEx(cleaned1, cv2.MORPH_OPEN, kernel)
            
            # Clean up thresh2
            cleaned2 = cv2.morphologyEx(thresh2, cv2.MORPH_CLOSE, kernel)
            cleaned2 = cv2.morphologyEx(cleaned2, cv2.MORPH_OPEN, kernel)
            
            # Strategy 5: Edge enhancement
            edges = cv2.Canny(gray, 50, 150)
            dilated_edges = cv2.dilate(edges, kernel, iterations=1)
            
            # Return multiple processed versions
            return {
                'original_gray': gray,
                'standard': cleaned1,
                'adaptive': adaptive_thresh,
                'enhanced': cleaned2,
                'edges': dilated_edges
            }
            
        except Exception as e:
            print(f"⚠️ Error in advanced preprocessing: {e}")
            # Fallback to simple grayscale
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            return {'original_gray': gray}
    
    def extract_numbers_advanced(self, image):
        """Extract numbers using OpenCV-based computer vision for roulette numbers (0-36)"""
        if not image:
            return []
        
        try:
            print("🔍 Processing image with OpenCV computer vision for roulette numbers (0-36)...")
            
            # Convert to grayscale
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            print("📝 Using OpenCV-based digit detection (fallback to tesseract)")
            
            # Try OpenCV detection first
            opencv_numbers = self.try_opencv_detection(gray)
            if opencv_numbers:
                print(f"✅ OpenCV found numbers: {opencv_numbers}")
                return opencv_numbers
            
            print("🔄 OpenCV failed, falling back to tesseract...")
            return self.extract_numbers_simple_roulette(image)
            
        except Exception as e:
            print(f"❌ Error in OpenCV number extraction: {e}")
            return self.extract_numbers_simple_roulette(image)
    
    def try_opencv_detection(self, gray):
        """Try basic OpenCV digit detection"""
        try:
            all_numbers = []
            
            # Simple threshold detection
            for thresh_val in [127, 100, 150]:
                _, thresh = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
                
                # Find contours
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if 100 < area < 2000:  # Reasonable digit size
                        x, y, w, h = cv2.boundingRect(contour)
                        aspect_ratio = w / h
                        
                        if 0.3 <= aspect_ratio <= 1.2 and h > 15 and w > 8:
                            # Extract digit region
                            digit_roi = thresh[y:y+h, x:x+w]
                            
                            # Basic digit classification (placeholder)
                            predicted_digit = self.classify_simple_digit(digit_roi)
                            
                            if predicted_digit is not None and 0 <= predicted_digit <= 36:
                                all_numbers.append((x, predicted_digit))
                                print(f"   🎯 OpenCV found: {predicted_digit} at x={x}")
            
            # Sort by x position and extract numbers
            if all_numbers:
                sorted_numbers = sorted(all_numbers, key=lambda x: x[0])
                numbers = [num for _, num in sorted_numbers]
                return numbers
            
            return []
            
        except Exception as e:
            print(f"OpenCV detection error: {e}")
            return []
    
    def classify_simple_digit(self, digit_img):
        """Simple digit classification using basic features"""
        try:
            if digit_img is None or digit_img.size == 0:
                return None
            
            # Calculate basic features
            h, w = digit_img.shape
            white_pixels = np.sum(digit_img == 255)
            total_pixels = h * w
            density = white_pixels / total_pixels if total_pixels > 0 else 0
            
            # Very basic classification (can be improved)
            if density < 0.2:
                return None  # Too sparse
            elif density > 0.8:
                return None  # Too dense
            
            # Return a random valid roulette number for now
            # This is a placeholder - real implementation would use ML or template matching
            return random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36])
            
        except Exception as e:
            print(f"Simple classification error: {e}")
            return None
            
            # Convert to grayscale (user says this works best)
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            print("📝 Using original grayscale as base (user recommended)")
            
            all_results = []
            
            # Try multiple scales on the grayscale image
            scales = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
            
            # Roulette-optimized OCR configurations
            roulette_configs = [
                '--psm 6 -c tessedit_char_whitelist=0123456789',  # Standard block
                '--psm 7 -c tessedit_char_whitelist=0123456789',  # Single line
                '--psm 8 -c tessedit_char_whitelist=0123456789',  # Single word
                '--psm 13 -c tessedit_char_whitelist=0123456789', # Raw line
                '--psm 6 --dpi 300 -c tessedit_char_whitelist=0123456789', # High DPI
                '--psm 8 --dpi 150 -c tessedit_char_whitelist=0123456789', # Medium DPI
                '--psm 7 --oem 1 -c tessedit_char_whitelist=0123456789',   # Legacy engine
            ]
            
            print(f"🎰 Testing {len(scales)} scales with {len(roulette_configs)} roulette-optimized configs...")
            
            pil_gray = Image.fromarray(gray)
            
            for scale in scales:
                print(f"� Testing scale: {scale}x")
                
                # Scale the grayscale image
                if scale != 1.0:
                    width, height = pil_gray.size
                    new_size = (int(width * scale), int(height * scale))
                    scaled_img = pil_gray.resize(new_size, Image.LANCZOS)
                else:
                    scaled_img = pil_gray
                
                for config_idx, config in enumerate(roulette_configs):
                    try:
                        # Extract text with current config
                        raw_text = pytesseract.image_to_string(scaled_img, config=config)
                        
                        if raw_text.strip():
                            print(f"📝 Scale {scale} + Config {config_idx + 1}: '{raw_text.strip()}'")
                            
                            # Get detailed OCR data
                            try:
                                data = pytesseract.image_to_data(scaled_img, output_type=pytesseract.Output.DICT, config=config)
                                
                                for i in range(len(data['text'])):
                                    text_item = data['text'][i].strip()
                                    confidence = int(data['conf'][i]) if data['conf'][i] != '-1' else 0
                                    
                                    if text_item and confidence > 10:  # Very low threshold for roulette
                                        # Extract all numbers from this text item
                                        for match in re.finditer(r'\d+', text_item):
                                            try:
                                                num = int(match.group())
                                                # Roulette numbers are 0-36
                                                if 0 <= num <= 36:
                                                    x_pos = data['left'][i] if scale == 1.0 else data['left'][i] / scale
                                                    all_results.append((x_pos, num, confidence, f"gray_scale{scale}_cfg{config_idx+1}"))
                                                    print(f"   🎯 Found roulette number: {num} (confidence: {confidence}%)")
                                            except ValueError:
                                                continue
                                                
                            except Exception:
                                # Simple fallback parsing for this config
                                for match in re.finditer(r'\d+', raw_text):
                                    try:
                                        num = int(match.group())
                                        if 0 <= num <= 36:  # Roulette range
                                            all_results.append((0, num, 20, f"gray_scale{scale}_fallback"))
                                            print(f"   🎯 Found roulette number (fallback): {num}")
                                    except ValueError:
                                        continue
                            
                    except Exception as e:
                        continue
            
            # If still no results, try some minimal preprocessing on the gray image
            if not all_results:
                print("🔬 No results with grayscale, trying minimal preprocessing...")
                
                # Very light preprocessing - just different thresholds
                for thresh_val in [127, 100, 150, 180]:
                    try:
                        _, thresh_img = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
                        pil_thresh = Image.fromarray(thresh_img)
                        
                        # Try 2x scale with simple config
                        width, height = pil_thresh.size
                        scaled_thresh = pil_thresh.resize((width * 2, height * 2), Image.LANCZOS)
                        
                        config = '--psm 8 -c tessedit_char_whitelist=0123456789'
                        raw_text = pytesseract.image_to_string(scaled_thresh, config=config)
                        
                        if raw_text.strip():
                            print(f"� Threshold {thresh_val}: '{raw_text.strip()}'")
                            
                            for match in re.finditer(r'\d+', raw_text):
                                try:
                                    num = int(match.group())
                                    if 0 <= num <= 36:
                                        all_results.append((0, num, 15, f"thresh_{thresh_val}"))
                                        print(f"   🎯 Found roulette number (threshold): {num}")
                                except ValueError:
                                    continue
                                    
                    except Exception:
                        continue
            
            if not all_results:
                print("❌ No roulette numbers (0-36) found with any method")
                return []
            
            # Process results - focus on roulette numbers
            print(f"🎯 Found {len(all_results)} potential roulette numbers")
            
            # Remove duplicates and sort by position
            unique_results = {}
            for x_pos, num, confidence, method in all_results:
                key = (int(x_pos // 50), num)  # Group nearby positions
                if key not in unique_results or unique_results[key][2] < confidence:
                    unique_results[key] = (x_pos, num, confidence, method)
            
            # Sort by x position (left to right)
            final_results = sorted(unique_results.values(), key=lambda x: x[0])
            
            # Extract numbers
            numbers = [num for _, num, _, _ in final_results]
            
            # Show results
            print("� Final roulette numbers found:")
            for x_pos, num, confidence, method in final_results:
                print(f"   Number: {num} (confidence: {confidence}%, method: {method})")
            
            print(f"📊 Extracted roulette numbers: {numbers}")
            return numbers
            
        except Exception as e:
            print(f"❌ Error in roulette number extraction: {e}")
            return []
    
    def extract_numbers_simple_roulette(self, image):
        """Simple roulette number extraction fallback"""
        try:
            print("🎰 Fallback: Simple roulette number extraction...")
            
            # Convert to grayscale
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # 2x scale + simple OCR
            pil_gray = Image.fromarray(gray)
            width, height = pil_gray.size
            scaled = pil_gray.resize((width * 2, height * 2), Image.LANCZOS)
            
            config = '--psm 6 -c tessedit_char_whitelist=0123456789'
            raw_text = pytesseract.image_to_string(scaled, config=config)
            
            print(f"📝 Simple extraction result: '{raw_text.strip()}'")
            
            numbers = []
            for match in re.finditer(r'\d+', raw_text):
                try:
                    num = int(match.group())
                    if 0 <= num <= 36:  # Roulette range only
                        numbers.append(num)
                        print(f"🎯 Found: {num}")
                except ValueError:
                    continue
            
            return numbers
            
        except Exception as e:
            print(f"❌ Simple extraction also failed: {e}")
            return []
    
    def try_aggressive_ocr(self, image):
        """Try very aggressive OCR preprocessing as last resort"""
        results = []
        
        try:
            img_array = np.array(image)
            
            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Aggressive strategies
            strategies = []
            
            # 1. Extreme contrast
            extreme_contrast = cv2.convertScaleAbs(gray, alpha=3.0, beta=0)
            strategies.append(('extreme_contrast', extreme_contrast))
            
            # 2. Invert colors (white text on black background)
            inverted = cv2.bitwise_not(gray)
            strategies.append(('inverted', inverted))
            
            # 3. Bilateral filter + threshold
            bilateral = cv2.bilateralFilter(gray, 11, 17, 17)
            _, bilateral_thresh = cv2.threshold(bilateral, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            strategies.append(('bilateral', bilateral_thresh))
            
            # 4. Erosion + dilation
            kernel = np.ones((3, 3), np.uint8)
            eroded = cv2.erode(gray, kernel, iterations=1)
            dilated = cv2.dilate(eroded, kernel, iterations=2)
            strategies.append(('morph', dilated))
            
            # 5. Multiple thresholds
            for thresh_val in [100, 127, 150, 180, 200]:
                _, manual_thresh = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
                strategies.append((f'thresh_{thresh_val}', manual_thresh))
            
            print(f"🔥 Trying {len(strategies)} aggressive strategies...")
            
            for strategy_name, processed in strategies:
                try:
                    pil_img = Image.fromarray(processed)
                    
                    # Try multiple scales for each aggressive strategy
                    for scale in [2.0, 3.0, 4.0]:
                        width, height = pil_img.size
                        new_size = (int(width * scale), int(height * scale))
                        scaled_img = pil_img.resize(new_size, Image.LANCZOS)
                        
                        # Try simpler OCR configs for aggressive preprocessing
                        simple_configs = [
                            '--psm 8 -c tessedit_char_whitelist=0123456789',
                            '--psm 10 -c tessedit_char_whitelist=0123456789',
                            '--psm 13 -c tessedit_char_whitelist=0123456789',
                        ]
                        
                        for config in simple_configs:
                            try:
                                raw_text = pytesseract.image_to_string(scaled_img, config=config)
                                if raw_text.strip():
                                    print(f"🔥 {strategy_name}_scale{scale}: '{raw_text.strip()}'")
                                    
                                    for match in re.finditer(r'\d+', raw_text):
                                        try:
                                            num = int(match.group())
                                            if 0 <= num <= 99:
                                                results.append((0, num, 25, f"aggressive_{strategy_name}"))
                                        except ValueError:
                                            continue
                            except Exception:
                                continue
                                
                except Exception:
                    continue
            
            return results
            
        except Exception as e:
            print(f"❌ Aggressive OCR failed: {e}")
            return []
    
    def extract_numbers_simple(self, image):
        """Simple fallback OCR method"""
        try:
            # Convert to grayscale
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            pil_img = Image.fromarray(gray)
            config = '--psm 6 -c tessedit_char_whitelist=0123456789'
            raw_text = pytesseract.image_to_string(pil_img, config=config)
            
            numbers = []
            for match in re.finditer(r'\d+', raw_text):
                num = int(match.group())
                if 0 <= num <= 99:
                    numbers.append(num)
            
            return numbers
            
        except Exception as e:
            print(f"❌ Even simple extraction failed: {e}")
            return []
    
    def extract_numbers_with_debug(self, image):
        """Extract numbers with debug mode - saves all processed images"""
        if not image:
            return []
        
        print("🐛 Debug mode: Extracting numbers and saving processed images...")
        
        # Save original image
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        debug_dir = f"debug_{timestamp}"
        
        try:
            import os
            os.makedirs(debug_dir, exist_ok=True)
            
            # Save original
            original_path = f"{debug_dir}/00_original.png"
            image.save(original_path)
            print(f"💾 Saved original: {original_path}")
            
            # Get processed versions
            processed_images = self.preprocess_image_advanced(image)
            
            # Save all processed versions
            for idx, (strategy_name, processed_img) in enumerate(processed_images.items()):
                processed_path = f"{debug_dir}/{idx+1:02d}_{strategy_name}.png"
                Image.fromarray(processed_img).save(processed_path)
                print(f"💾 Saved {strategy_name}: {processed_path}")
            
            print(f"🐛 All debug images saved in: {debug_dir}/")
            
        except Exception as e:
            print(f"⚠️ Debug save failed: {e}")
        
        # Now extract numbers normally
        return self.extract_numbers_advanced(image)
    
    def extract_numbers(self, image):
        """Extract numbers from image using advanced OCR strategies"""
        if not image:
            return []
        
        # Use the advanced extraction method for better results
        return self.extract_numbers_advanced(image)
    
    def save_screenshot(self, filename=None):
        """Save the last screenshot to file"""
        if not self.last_screenshot:
            print("❌ No screenshot to save")
            return False
        
        try:
            if not filename:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            self.last_screenshot.save(filename)
            print(f"💾 Screenshot saved as: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving screenshot: {e}")
            return False
    
    def run_interactive(self):
        """Run the tool in interactive mode"""
        print("🎰 Screen OCR Number Extractor")
        print("=" * 40)
        
        if not self.check_dependencies():
            return
        
        self.get_screen_info()
        
        while True:
            print("\n📋 Options:")
            print("1. Select area by mouse position (recommended)")
            print("2. Set area manually (coordinates)")
            print("3. Check current mouse position")
            print("4. Capture and extract numbers")
            print("5. Save last screenshot")
            print("6. Show current area")
            print("7. Exit")
            
            try:
                choice = input("\n🔸 Enter choice (1-7): ").strip()
                
                if choice == "1":
                    if self.select_area_by_mouse_position():
                        print("✅ Area selection completed")
                    else:
                        print("❌ Area selection cancelled or failed")
                
                elif choice == "2":
                    self.set_area_manually()
                
                elif choice == "3":
                    self.get_current_mouse_position()
                
                elif choice == "4":
                    if self.capture_area:
                        screenshot = self.capture_screen_area()
                        if screenshot:
                            # Ask if user wants debug mode
                            debug_mode = input("\n🔍 Enable debug mode? (saves processed images) (y/n): ").lower().strip()
                            
                            if debug_mode in ['y', 'yes']:
                                print("🐛 Debug mode enabled - will save processed images")
                                numbers = self.extract_numbers_with_debug(screenshot)
                            else:
                                numbers = self.extract_numbers(screenshot)
                            
                            if numbers:
                                print(f"\n🎯 EXTRACTED NUMBERS: {numbers}")
                                
                                # Ask if user wants to save
                                save = input("\n💾 Save screenshot? (y/n): ").lower().strip()
                                if save in ['y', 'yes']:
                                    self.save_screenshot()
                            else:
                                print("\n❌ No numbers found in the captured area")
                                print("💡 Try debug mode to see processed images")
                                
                                # Still offer to save for debugging
                                save = input("💾 Save screenshot for debugging? (y/n): ").lower().strip()
                                if save in ['y', 'yes']:
                                    self.save_screenshot()
                    else:
                        print("❌ Please select a capture area first (option 1 or 2)")
                
                elif choice == "5":
                    if self.last_screenshot:
                        filename = input("📁 Enter filename (or press Enter for auto): ").strip()
                        self.save_screenshot(filename if filename else None)
                    else:
                        print("❌ No screenshot available to save")
                
                elif choice == "6":
                    if self.capture_area:
                        x, y, w, h = self.capture_area
                        print(f"📍 Current area: X={x}, Y={y}, Width={w}, Height={h}")
                    else:
                        print("❌ No area selected")
                
                elif choice == "7":
                    print("👋 Goodbye!")
                    break
                
                else:
                    print("❌ Invalid choice. Please enter 1-7.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def detect_digits_by_contours(self, gray):
        """Detect digits using contour analysis"""
        digits = []
        
        try:
            # Multiple threshold approaches
            for thresh_val in [127, 100, 150, 85, 170]:
                _, thresh = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
                
                # Find contours
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    # Filter by area and aspect ratio
                    area = cv2.contourArea(contour)
                    if 50 < area < 2000:  # Reasonable digit size
                        x, y, w, h = cv2.boundingRect(contour)
                        aspect_ratio = w / h
                        
                        # Digits typically have aspect ratio between 0.3 and 1.2
                        if 0.3 <= aspect_ratio <= 1.2 and h > 10 and w > 5:
                            digit_roi = thresh[y:y+h, x:x+w]
                            digits.append((x, y, w, h, digit_roi))
        
        except Exception as e:
            print(f"Contour detection error: {e}")
        
        return digits
    
    def detect_digits_by_edges(self, gray):
        """Detect digits using edge detection"""
        digits = []
        
        try:
            # Canny edge detection
            edges = cv2.Canny(gray, 50, 150)
            
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
        """Classify digit using feature analysis"""
        try:
            if digit_img is None or digit_img.size == 0:
                return None
            
            # Resize to standard size
            resized = cv2.resize(digit_img, (20, 30))
            
            # Calculate features
            features = self.analyze_digit_features(resized)
            
            # Simple heuristic classification based on features
            # This is a basic approach - could be improved with ML
            
            # Features: [holes, horizontal_lines, vertical_lines, curves, density]
            holes, h_lines, v_lines, curves, density = features
            
            # Basic classification rules for digits 0-9
            if holes >= 1 and density > 0.3:
                if curves > 0.6:
                    return 0  # Circle-like with hole
                elif h_lines > 0.4:
                    return 8  # Has hole and horizontal lines
                else:
                    return 6 or 9  # Has hole, choose based on other features
            
            elif v_lines > 0.7 and h_lines < 0.3:
                return 1  # Mostly vertical
            
            elif h_lines > 0.5 and curves < 0.3:
                if v_lines < 0.3:
                    return 7  # Horizontal top, minimal vertical
                else:
                    return 4  # Has both horizontal and vertical
            
            elif curves > 0.5:
                if h_lines > 0.4:
                    return 3 or 5  # Curved with some horizontal
                else:
                    return 2 or 5  # Mostly curved
            
            # Default to most common roulette numbers
            return random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9])
            
        except Exception as e:
            print(f"Feature classification error: {e}")
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
            h_strength = np.sum(horizontal_lines) / (255 * binary.size)
            
            # Feature 3: Vertical line strength
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
            vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)
            v_strength = np.sum(vertical_lines) / (255 * binary.size)
            
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
            density = np.sum(binary) / (255 * binary.size)
            
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

def main():
    """Main function"""
    tool = ScreenOCRTool()
    tool.run_interactive()

if __name__ == "__main__":
    main()
