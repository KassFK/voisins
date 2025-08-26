#!/usr/bin/env python3
"""
Roulette Voisins Tracker - Web Version

A web-based interface for tracking roulette numbers using a simple HTML interface.
"""

import webbrowser
import http.server
import socketserver
import json
import urllib.parse
from pathlib import Path
import threading
import time

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
