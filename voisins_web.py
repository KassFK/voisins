#!/usr/bin/env python3
"""
Roulette Voisins Tracker - Web Version with Screen Capture

A web-based interface for tracking roulette numbers using a simple HTML interface
with OCR screen capture functionality.
"""

import webbrowser
import http.server
import socketserver
import json
import urllib.parse
from pathlib import Path
import threading
import time
import base64
import io
import re

# Screen capture and OCR imports
try:
    import pyautogui
    import pytesseract
    from PIL import Image, ImageEnhance
    import cv2
    import numpy as np
    SCREEN_CAPTURE_AVAILABLE = True
except ImportError as e:
    SCREEN_CAPTURE_AVAILABLE = False
    print(f"Screen capture not available: {e}")

# Configure pyautogui for macOS
if SCREEN_CAPTURE_AVAILABLE:
    pyautogui.FAILSAFE = True
    # Set tesseract path for macOS (installed via brew)
    try:
        pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
    except:
        pass

class ScreenCaptureOCR:
    def __init__(self):
        self.capture_area = None
        
    def get_screen_info(self):
        """Get information about all available screens"""
        if not SCREEN_CAPTURE_AVAILABLE:
            return {"success": False, "error": "Screen capture not available"}
        
        try:
            # Get all monitors
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # Hide the window
            
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            
            # For macOS, we can get multiple screen info
            screens = []
            try:
                # Try to get multiple monitor info
                from AppKit import NSScreen
                ns_screens = NSScreen.screens()
                for i, screen in enumerate(ns_screens):
                    frame = screen.frame()
                    screens.append({
                        'id': i,
                        'x': int(frame.origin.x),
                        'y': int(frame.origin.y),
                        'width': int(frame.size.width),
                        'height': int(frame.size.height),
                        'primary': i == 0
                    })
            except ImportError:
                # Fallback to single screen
                screens = [{
                    'id': 0,
                    'x': 0,
                    'y': 0,
                    'width': screen_width,
                    'height': screen_height,
                    'primary': True
                }]
            
            root.destroy()
            
            return {
                "success": True,
                "screens": screens,
                "total_width": screen_width,
                "total_height": screen_height
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def start_area_selection(self):
        """Start interactive area selection using a simple two-click method"""
        if not SCREEN_CAPTURE_AVAILABLE:
            return {"success": False, "error": "Screen capture not available"}
        
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            # Create a simple overlay window
            root = tk.Tk()
            root.withdraw()  # Hide main window
            
            # Get screen dimensions
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            
            # Create overlay window
            overlay = tk.Toplevel(root)
            overlay.title("Select Area - Click Two Points")
            overlay.attributes('-alpha', 0.1)  # Very transparent
            overlay.attributes('-topmost', True)
            overlay.configure(bg='red')
            overlay.geometry(f"{screen_width}x{screen_height}+0+0")
            overlay.overrideredirect(True)  # Remove window decorations
            
            # Variables for selection
            self.click_count = 0
            self.point1 = None
            self.point2 = None
            
            # Create canvas
            canvas = tk.Canvas(overlay, bg='red', highlightthickness=0)
            canvas.pack(fill=tk.BOTH, expand=True)
            
            # Instructions label
            instruction_text = "STEP 1: Click the TOP-LEFT corner of the area"
            instructions = tk.Label(
                canvas,
                text=instruction_text,
                font=('Arial', 20, 'bold'),
                bg='yellow',
                fg='black',
                pady=10,
                padx=20
            )
            instructions.place(x=50, y=50)
            
            def on_click(event):
                x, y = event.x_root, event.y_root
                
                # Print to console for debugging
                print(f"Click {self.click_count + 1}: ({x}, {y})")
                
                if self.click_count == 0:
                    # First click - top-left corner
                    self.point1 = (x, y)
                    self.click_count = 1
                    
                    # Update instructions
                    instructions.configure(
                        text=f"✅ Point 1 set: ({x}, {y})\nSTEP 2: Click BOTTOM-RIGHT corner",
                        bg='green',
                        fg='white'
                    )
                    
                    # Draw a marker at the first point
                    canvas_x = x
                    canvas_y = y
                    canvas.create_oval(
                        canvas_x-5, canvas_y-5, canvas_x+5, canvas_y+5,
                        fill='blue', outline='white', width=2
                    )
                    
                elif self.click_count == 1:
                    # Second click - bottom-right corner
                    self.point2 = (x, y)
                    
                    # Calculate area
                    x1, y1 = self.point1
                    x2, y2 = self.point2
                    
                    left = min(x1, x2)
                    top = min(y1, y2)
                    right = max(x1, x2)
                    bottom = max(y1, y2)
                    
                    width = right - left
                    height = bottom - top
                    
                    if width > 10 and height > 10:
                        self.capture_area = (left, top, width, height)
                        
                        instructions.configure(
                            text=f"✅ Area selected: {width}x{height} pixels\nClosing in 2 seconds...",
                            bg='darkgreen',
                            fg='white'
                        )
                        
                        # Close after showing success for 2 seconds
                        overlay.after(2000, lambda: [overlay.destroy(), root.destroy()])
                        
                        # Show success message
                        success_root = tk.Tk()
                        success_root.withdraw()
                        messagebox.showinfo(
                            "Area Selected", 
                            f"Capture area set successfully!\n\nCoordinates: {left}, {top}\nSize: {width} x {height}"
                        )
                        success_root.destroy()
                    else:
                        # Area too small, reset
                        instructions.configure(
                            text=f"❌ Area too small ({width}x{height})!\nSTEP 1: Click TOP-LEFT again",
                            bg='red',
                            fg='white'
                        )
                        
                        self.click_count = 0
                        self.point1 = None
                        canvas.delete("all")
                        
                        # Reset after 2 seconds
                        overlay.after(2000, lambda: instructions.configure(
                            text="STEP 1: Click the TOP-LEFT corner of the area",
                            bg='yellow',
                            fg='black'
                        ))
            
            def on_escape(event):
                overlay.destroy()
                root.destroy()
            
            # Bind events
            canvas.bind("<Button-1>", on_click)
            overlay.bind("<Escape>", on_escape)
            overlay.focus_set()
            
            # Start the selection loop
            overlay.mainloop()
            
            return {"success": True, "message": "Area selection completed"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        
    def set_capture_area(self, x, y, width, height):
        """Set the area to capture for OCR"""
        self.capture_area = (x, y, width, height)
        
    def capture_and_extract_numbers(self):
        """Capture screen area and extract numbers using OCR"""
        if not SCREEN_CAPTURE_AVAILABLE:
            return {"success": False, "error": "Screen capture not available"}
            
        if not self.capture_area:
            return {"success": False, "error": "No capture area set"}
            
        try:
            # Capture the specified area
            x, y, width, height = self.capture_area
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            
            # Convert to numpy array for OpenCV processing
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Preprocess image for better OCR
            processed_img = self.preprocess_image(img)
            
            # Extract text using OCR with better configuration for numbers
            config = '--psm 6 -c tessedit_char_whitelist=0123456789 '
            text = pytesseract.image_to_string(processed_img, config=config)
            
            # Parse numbers from text (left to right order)
            numbers = self.parse_numbers_from_text_ordered(text, processed_img)
            
            # Convert image to base64 for preview
            img_buffer = io.BytesIO()
            screenshot.save(img_buffer, format='PNG')
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            return {
                "success": True,
                "numbers": numbers,
                "text_raw": text,
                "image_preview": img_base64,
                "capture_area": self.capture_area
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def preprocess_image(self, img):
        """Preprocess image for better OCR results"""
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Dilate to make text thicker
        kernel = np.ones((2, 2), np.uint8)
        processed = cv2.dilate(thresh, kernel, iterations=1)
        
        return processed
    
    def parse_numbers_from_text_ordered(self, text, processed_img):
        """Parse numbers from OCR text maintaining left-to-right order"""
        try:
            # Use OCR with bounding boxes to get position information
            data = pytesseract.image_to_data(processed_img, output_type=pytesseract.Output.DICT)
            
            # Extract numbers with their positions
            number_positions = []
            for i in range(len(data['text'])):
                text_item = data['text'][i].strip()
                if text_item and text_item.isdigit():
                    num = int(text_item)
                    if 0 <= num <= 36:  # Valid roulette numbers
                        x = data['left'][i]
                        number_positions.append((x, num))
            
            # Sort by x position (left to right, but we want right to left for chronological order)
            number_positions.sort(key=lambda item: item[0], reverse=True)
            
            # Return numbers in chronological order (rightmost is most recent)
            return [num for _, num in number_positions]
            
        except Exception:
            # Fallback to simple text parsing
            cleaned_text = re.sub(r'[^0-9\s]', ' ', text)
            numbers = []
            for match in re.finditer(r'\d+', cleaned_text):
                num = int(match.group())
                if 0 <= num <= 36:
                    numbers.append(num)
            return numbers

# Global instances
ocr_engine = ScreenCaptureOCR()

class RouletteVoisinsTracker:
    def __init__(self):
        self.voisins_numbers = {22, 18, 29, 7, 28, 12, 35, 3, 26, 0, 32, 15, 19, 4, 21, 2, 25}
        self.rounds_without_voisins = 0
        self.total_rounds = 0
        self.history = []
        
    def is_voisins(self, number):
        return number in self.voisins_numbers
    
    def add_number(self, number):
        if not (0 <= number <= 36):
            raise ValueError("Roulette number must be between 0 and 36")
        
        self.history.append(number)
        self.total_rounds += 1
        
        if self.is_voisins(number):
            self.rounds_without_voisins = 0
            return True
        else:
            self.rounds_without_voisins += 1
            return False
    
    def get_status(self):
        return {
            'rounds_without_voisins': self.rounds_without_voisins,
            'total_rounds': self.total_rounds,
            'last_number': self.history[-1] if self.history else None,
            'voisins_numbers': sorted(list(self.voisins_numbers))
        }
    
    def reset(self):
        self.rounds_without_voisins = 0
        self.total_rounds = 0
        self.history = []

# Global tracker instance
tracker = RouletteVoisinsTracker()

class RouletteHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html().encode())
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(tracker.get_status()).encode())
        elif self.path == '/screen_capture':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            if not SCREEN_CAPTURE_AVAILABLE:
                response = {
                    'success': False,
                    'error': 'Screen capture not available. Please install required packages.'
                }
            else:
                response = ocr_engine.capture_and_extract_numbers()
            
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/get_mouse_position':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            if SCREEN_CAPTURE_AVAILABLE:
                x, y = pyautogui.position()
                response = {'success': True, 'x': x, 'y': y}
            else:
                response = {'success': False, 'error': 'Screen capture not available'}
            
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/get_screen_info':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = ocr_engine.get_screen_info()
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/start_area_selection':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = ocr_engine.start_area_selection()
            self.wfile.write(json.dumps(response).encode())
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/add_number':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = urllib.parse.parse_qs(post_data.decode())
            
            try:
                number = int(data['number'][0])
                is_voisins = tracker.add_number(number)
                
                response = {
                    'success': True,
                    'is_voisins': is_voisins,
                    'number': number,
                    'status': tracker.get_status()
                }
            except (ValueError, KeyError) as e:
                response = {
                    'success': False,
                    'error': str(e)
                }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/reset':
            tracker.reset()
            response = {
                'success': True,
                'status': tracker.get_status()
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/set_capture_area':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            try:
                x = int(data['x'])
                y = int(data['y'])
                width = int(data['width'])
                height = int(data['height'])
                
                ocr_engine.set_capture_area(x, y, width, height)
                
                response = {
                    'success': True,
                    'capture_area': {'x': x, 'y': y, 'width': width, 'height': height}
                }
            except (ValueError, KeyError) as e:
                response = {
                    'success': False,
                    'error': str(e)
                }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/analyze_numbers':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            try:
                numbers = data['numbers']  # Numbers are already in chronological order (rightmost first)
                non_voisins_count = 0
                voisins_numbers = tracker.voisins_numbers
                analysis_details = []
                
                # Count from the most recent (rightmost) number until we hit a voisins
                for i, num in enumerate(numbers):
                    round_number = i + 1
                    is_voisins = num in voisins_numbers
                    
                    analysis_details.append({
                        'round': round_number,
                        'number': num,
                        'is_voisins': is_voisins,
                        'position': 'rightmost' if i == 0 else f'{i+1} from right'
                    })
                    
                    if is_voisins:
                        break  # Stop counting when we hit a voisins number
                    else:
                        non_voisins_count += 1
                
                # If no voisins found, all numbers are non-voisins
                if non_voisins_count == 0 and len(numbers) > 0 and numbers[0] not in voisins_numbers:
                    non_voisins_count = len(numbers)
                
                response = {
                    'success': True,
                    'numbers': numbers,
                    'non_voisins_count': non_voisins_count,
                    'analysis_details': analysis_details,
                    'voisins_numbers': sorted(list(voisins_numbers)),
                    'total_numbers_found': len(numbers)
                }
            except (ValueError, KeyError) as e:
                response = {
                    'success': False,
                    'error': str(e)
                }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
    
    def get_html(self):
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎰 Roulette Voisins Tracker</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #2c3e50, #3498db);
            color: white;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(0,0,0,0.3);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        h1 {
            text-align: center;
            color: #e74c3c;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        .status-panel {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        .rounds-counter {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .input-section {
            text-align: center;
            margin-bottom: 30px;
        }
        input[type="number"] {
            font-size: 1.5em;
            padding: 10px;
            width: 100px;
            text-align: center;
            border: none;
            border-radius: 5px;
            margin: 10px;
        }
        .btn {
            font-size: 1.2em;
            padding: 12px 25px;
            margin: 5px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-primary {
            background: #e74c3c;
            color: white;
        }
        .btn-secondary {
            background: #95a5a6;
            color: white;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        .number-grid {
            display: grid;
            grid-template-columns: repeat(10, 1fr);
            gap: 5px;
            margin: 20px 0;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }
        .number-btn {
            padding: 10px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.2s;
        }
        .number-btn:hover {
            transform: scale(1.1);
        }
        .number-zero {
            background: #27ae60;
            color: white;
        }
        .number-voisins {
            background: #3498db;
            color: white;
        }
        .number-other {
            background: #7f8c8d;
            color: white;
        }
        .result {
            text-align: center;
            font-size: 1.3em;
            font-weight: bold;
            margin: 20px 0;
            padding: 15px;
            border-radius: 8px;
        }
        .result-success {
            background: rgba(39, 174, 96, 0.3);
            color: #27ae60;
        }
        .result-miss {
            background: rgba(231, 76, 60, 0.3);
            color: #e74c3c;
        }
        .voisins-info {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            text-align: center;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎰 Roulette Voisins Tracker</h1>
        
        <div class="status-panel">
            <div class="rounds-counter" id="roundsCounter">Rounds without Voisins: 0</div>
            <div>Total Rounds: <span id="totalRounds">0</span></div>
            <div>Last Number: <span id="lastNumber">-</span></div>
        </div>
        
        <div class="input-section">
            <div>
                <input type="number" id="numberInput" min="0" max="36" placeholder="0-36">
            </div>
            <button class="btn btn-primary" onclick="addNumber()">Add Number</button>
            <button class="btn btn-secondary" onclick="reset()">Reset</button>
        </div>
        
        <!-- Screen Capture Section -->
        <div class="screen-capture-section">
            <h3 style="color: #e74c3c; text-align: center; margin-bottom: 15px;">📸 Screen Capture OCR</h3>
            <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                
                <!-- Method 1: Interactive Area Selection -->
                <div style="text-align: center; margin-bottom: 20px; padding: 15px; background: rgba(52, 152, 219, 0.1); border-radius: 8px;">
                    <h4 style="color: #3498db; margin: 0 0 10px 0;">🎯 Interactive Selection (Recommended)</h4>
                    <p style="color: #bdc3c7; margin: 5px 0; font-size: 0.9em;">Two-click method: Click top-left corner, then bottom-right corner</p>
                    <button class="btn btn-primary" onclick="startAreaSelection()" style="font-size: 1.1em;">🖱️ Select Area (2-Click Method)</button>
                </div>
                
                <!-- Method 2: Manual Coordinates -->
                <div style="text-align: center; margin-bottom: 15px; padding: 15px; background: rgba(149, 165, 166, 0.1); border-radius: 8px;">
                    <h4 style="color: #95a5a6; margin: 0 0 10px 0;">⚙️ Manual Coordinates</h4>
                    <p style="color: #bdc3c7; margin: 5px 0; font-size: 0.9em;">Manually set capture area coordinates:</p>
                    <div style="display: flex; gap: 10px; justify-content: center; align-items: center; flex-wrap: wrap; margin: 10px 0;">
                        <input type="number" id="captureX" placeholder="X" style="width: 80px; padding: 5px;">
                        <input type="number" id="captureY" placeholder="Y" style="width: 80px; padding: 5px;">
                        <input type="number" id="captureWidth" placeholder="Width" style="width: 80px; padding: 5px;">
                        <input type="number" id="captureHeight" placeholder="Height" style="width: 80px; padding: 5px;">
                    </div>
                    <div style="margin: 10px 0;">
                        <button class="btn btn-secondary" onclick="getCurrentMousePosition()" style="font-size: 0.9em;">Get Mouse Position</button>
                        <button class="btn btn-secondary" onclick="setCaptureArea()" style="font-size: 0.9em;">Set Area</button>
                    </div>
                </div>
                
                <!-- Capture and Analyze -->
                <div style="text-align: center; margin-bottom: 15px; padding: 15px; background: rgba(231, 76, 60, 0.1); border-radius: 8px;">
                    <h4 style="color: #e74c3c; margin: 0 0 10px 0;">📸 Capture & Analyze</h4>
                    <p style="color: #bdc3c7; margin: 5px 0; font-size: 0.9em;">Numbers read from right to left (chronological order)</p>
                    <button class="btn btn-primary" onclick="captureAndAnalyze()" style="font-size: 1.2em;">📸 Capture & Count Non-Voisins</button>
                </div>
                
                <div id="captureResult" style="display: none; margin-top: 15px;">
                    <!-- Results will be shown here -->
                </div>
                
                <div id="capturePreview" style="display: none; margin-top: 15px; text-align: center;">
                    <!-- Image preview will be shown here -->
                </div>
            </div>
        </div>
        
        <div style="text-align: center; margin-bottom: 10px;">
            <strong>Click a number:</strong>
        </div>
        
        <div class="number-grid" id="numberGrid">
            <!-- Numbers will be generated by JavaScript -->
        </div>
        
        <div class="result" id="result" style="display: none;"></div>
        
        <div class="voisins-info">
            <strong>Voisins du Zéro:</strong> 0, 2, 3, 4, 7, 12, 15, 18, 19, 21, 22, 25, 26, 28, 29, 32, 35
        </div>
    </div>
    
    <script>
        const voisinsNumbers = [0, 2, 3, 4, 7, 12, 15, 18, 19, 21, 22, 25, 26, 28, 29, 32, 35];
        
        // Create number grid
        function createNumberGrid() {
            const grid = document.getElementById('numberGrid');
            for (let i = 0; i <= 36; i++) {
                const btn = document.createElement('button');
                btn.textContent = i;
                btn.className = 'number-btn';
                
                if (i === 0) {
                    btn.className += ' number-zero';
                } else if (voisinsNumbers.includes(i)) {
                    btn.className += ' number-voisins';
                } else {
                    btn.className += ' number-other';
                }
                
                btn.onclick = () => {
                    document.getElementById('numberInput').value = i;
                    addNumber();
                };
                
                grid.appendChild(btn);
            }
        }
        
        // Add number function
        async function addNumber() {
            const input = document.getElementById('numberInput');
            const number = parseInt(input.value);
            
            if (isNaN(number) || number < 0 || number > 36) {
                alert('Please enter a valid number between 0 and 36!');
                return;
            }
            
            try {
                const response = await fetch('/add_number', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `number=${number}`
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const result = document.getElementById('result');
                    result.style.display = 'block';
                    
                    if (data.is_voisins) {
                        result.className = 'result result-success';
                        result.textContent = `🎯 ${number} is VOISINS! Counter reset to 0`;
                    } else {
                        result.className = 'result result-miss';
                        result.textContent = `❌ ${number} is NOT voisins. Continue tracking...`;
                    }
                    
                    updateStatus(data.status);
                    input.value = '';
                    input.focus();
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Network error: ' + error.message);
            }
        }
        
        // Reset function
        async function reset() {
            try {
                const response = await fetch('/reset', {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const result = document.getElementById('result');
                    result.style.display = 'block';
                    result.className = 'result';
                    result.style.background = 'rgba(52, 152, 219, 0.3)';
                    result.style.color = '#3498db';
                    result.textContent = '✅ Tracker reset!';
                    
                    updateStatus(data.status);
                    document.getElementById('numberInput').focus();
                }
            } catch (error) {
                alert('Network error: ' + error.message);
            }
        }
        
        // Update status display
        function updateStatus(status) {
            const roundsCounter = document.getElementById('roundsCounter');
            const rounds = status.rounds_without_voisins;
            
            roundsCounter.textContent = `Rounds without Voisins: ${rounds}`;
            
            // Color coding
            if (rounds === 0) {
                roundsCounter.style.color = '#27ae60';
            } else if (rounds < 10) {
                roundsCounter.style.color = '#f39c12';
            } else if (rounds < 20) {
                roundsCounter.style.color = '#e67e22';
            } else {
                roundsCounter.style.color = '#e74c3c';
            }
            
            document.getElementById('totalRounds').textContent = status.total_rounds;
            document.getElementById('lastNumber').textContent = status.last_number || '-';
        }
        
        // Handle Enter key
        document.getElementById('numberInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                addNumber();
            }
        });
        
        // Initialize
        createNumberGrid();
        document.getElementById('numberInput').focus();
        
        // Screen Capture Functions
        async function startAreaSelection() {
            try {
                const response = await fetch('/start_area_selection');
                const data = await response.json();
                
                if (data.success) {
                    alert('📍 AREA SELECTION STARTED!\n\n' +
                          '🔸 STEP 1: Click the TOP-LEFT corner of the area containing roulette numbers\n' +
                          '🔸 STEP 2: Click the BOTTOM-RIGHT corner of the same area\n\n' +
                          '💡 Tip: Make sure to select an area that clearly contains the numbers\n' +
                          '❌ Press ESC to cancel anytime');
                } else {
                    alert('Error starting area selection: ' + data.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
        
        async function getCurrentMousePosition() {
            try {
                const response = await fetch('/get_mouse_position');
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('captureX').value = data.x;
                    document.getElementById('captureY').value = data.y;
                    // Set default width and height if not set
                    if (!document.getElementById('captureWidth').value) {
                        document.getElementById('captureWidth').value = 300;
                    }
                    if (!document.getElementById('captureHeight').value) {
                        document.getElementById('captureHeight').value = 100;
                    }
                } else {
                    alert('Error getting mouse position: ' + data.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
        
        async function setCaptureArea() {
            const x = parseInt(document.getElementById('captureX').value);
            const y = parseInt(document.getElementById('captureY').value);
            const width = parseInt(document.getElementById('captureWidth').value);
            const height = parseInt(document.getElementById('captureHeight').value);
            
            if (isNaN(x) || isNaN(y) || isNaN(width) || isNaN(height)) {
                alert('Please enter valid coordinates and dimensions!');
                return;
            }
            
            try {
                const response = await fetch('/set_capture_area', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        x: x,
                        y: y,
                        width: width,
                        height: height
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert('Capture area set successfully!');
                } else {
                    alert('Error setting capture area: ' + data.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
        
        async function captureAndAnalyze() {
            try {
                // First capture the screen
                const captureResponse = await fetch('/screen_capture');
                const captureData = await captureResponse.json();
                
                if (!captureData.success) {
                    alert('Capture failed: ' + captureData.error);
                    return;
                }
                
                const numbers = captureData.numbers;
                
                if (numbers.length === 0) {
                    alert('No valid numbers found in the captured area. Try adjusting the capture area or check the image quality.');
                    showCapturePreview(captureData);
                    return;
                }
                
                // Analyze the numbers for non-voisins count
                const analyzeResponse = await fetch('/analyze_numbers', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        numbers: numbers
                    })
                });
                
                const analyzeData = await analyzeResponse.json();
                
                if (analyzeData.success) {
                    showCaptureResult(analyzeData, captureData);
                } else {
                    alert('Analysis failed: ' + analyzeData.error);
                }
                
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
        
        function showCaptureResult(analyzeData, captureData) {
            const resultDiv = document.getElementById('captureResult');
            const nonVoisinsCount = analyzeData.non_voisins_count;
            const numbers = analyzeData.numbers;
            const details = analyzeData.analysis_details || [];
            
            let resultColor = '#27ae60'; // Green
            let resultMessage = '';
            
            if (nonVoisinsCount === 0 && numbers.length > 0) {
                resultMessage = '🎯 First number (rightmost) is VOISINS!';
                resultColor = '#27ae60';
            } else if (nonVoisinsCount === numbers.length) {
                resultMessage = `❌ All ${nonVoisinsCount} numbers are non-voisins (no voisins found)`;
                resultColor = '#e74c3c';
            } else {
                resultMessage = `📊 ${nonVoisinsCount} rounds without voisins before hitting a voisins number`;
                if (nonVoisinsCount < 5) {
                    resultColor = '#f39c12'; // Yellow
                } else if (nonVoisinsCount < 10) {
                    resultColor = '#e67e22'; // Orange
                } else {
                    resultColor = '#e74c3c'; // Red
                }
            }
            
            // Create detailed breakdown
            let detailsHtml = '';
            if (details.length > 0) {
                detailsHtml = '<div style="margin-top: 10px; font-size: 0.9em;">';
                detailsHtml += '<strong>Round-by-round analysis (right to left):</strong><br>';
                details.forEach(detail => {
                    const color = detail.is_voisins ? '#27ae60' : '#e74c3c';
                    const symbol = detail.is_voisins ? '🎯' : '❌';
                    detailsHtml += `${symbol} Round ${detail.round}: <span style="color: ${color}">${detail.number}</span> (${detail.position})<br>`;
                });
                detailsHtml += '</div>';
            }
            
            resultDiv.innerHTML = `
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px;">
                    <h4 style="color: ${resultColor}; margin: 0 0 10px 0;">${resultMessage}</h4>
                    <p style="color: #bdc3c7; margin: 5px 0;"><strong>Numbers found (chronological order):</strong> ${numbers.join(' → ')}</p>
                    <p style="color: #bdc3c7; margin: 5px 0; font-size: 0.9em;"><strong>Raw OCR text:</strong> "${captureData.text_raw.trim()}"</p>
                    ${detailsHtml}
                </div>
            `;
            resultDiv.style.display = 'block';
            
            // Show preview
            showCapturePreview(captureData);
        }
        
        function showCapturePreview(captureData) {
            const previewDiv = document.getElementById('capturePreview');
            
            if (captureData.image_preview) {
                previewDiv.innerHTML = `
                    <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px;">
                        <p style="color: #bdc3c7; margin: 5px 0;">Captured Image:</p>
                        <img src="data:image/png;base64,${captureData.image_preview}" 
                             style="max-width: 100%; max-height: 200px; border: 2px solid #34495e; border-radius: 5px;">
                        <p style="color: #95a5a6; margin: 5px 0; font-size: 0.8em;">Area: ${captureData.capture_area[0]}, ${captureData.capture_area[1]}, ${captureData.capture_area[2]}x${captureData.capture_area[3]}</p>
                    </div>
                `;
                previewDiv.style.display = 'block';
            }
        }
    </script>
</body>
</html>
        '''

def start_server():
    PORT = 8000
    
    try:
        with socketserver.TCPServer(("", PORT), RouletteHandler) as httpd:
            print(f"🎰 Roulette Voisins Tracker Web Server")
            print(f"Server running at: http://localhost:{PORT}")
            print("Press Ctrl+C to stop the server")
            
            # Open browser automatically
            threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\\nServer stopped.")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {PORT} is already in use. Trying port {PORT + 1}...")
            PORT += 1
            start_server()
        else:
            print(f"Error starting server: {e}")

if __name__ == "__main__":
    start_server()
