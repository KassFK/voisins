#!/usr/bin/env python3
"""
Roulette Voisins Tracker - Simple Web Version

A clean web-based interface for tracking roulette numbers without OCR/screen capture.
Focus on manual number input with a beautiful, easy-to-use interface.
"""

import webbrowser
import http.server
import socketserver
import json
import urllib.parse
import threading
import time

class RouletteVoisinsTracker:
    def __init__(self):
        self.voisins_numbers = {22, 18, 29, 7, 28, 12, 35, 3, 26, 0, 32, 15, 19, 4, 21, 2, 25}
        self.rounds_without_voisins = 0
        self.rounds_with_voisins = 0
        self.consecutive_voisins_streak = 0
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
            self.rounds_with_voisins += 1
            self.consecutive_voisins_streak += 1
            return True
        else:
            self.rounds_without_voisins += 1
            self.consecutive_voisins_streak = 0  # Reset streak when non-voisins hit
            return False
    
    def get_status(self):
        return {
            'rounds_without_voisins': self.rounds_without_voisins,
            'rounds_with_voisins': self.rounds_with_voisins,
            'consecutive_voisins_streak': self.consecutive_voisins_streak,
            'total_rounds': self.total_rounds,
            'last_number': self.history[-1] if self.history else None,
            'voisins_numbers': sorted(list(self.voisins_numbers)),
            'history': self.history[-10:] if len(self.history) > 10 else self.history  # Last 10 numbers
        }
    
    def reset(self):
        self.rounds_without_voisins = 0
        self.rounds_with_voisins = 0
        self.consecutive_voisins_streak = 0
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
    <title>🎰 Roulette Voisins Tracker - Simple</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        h1 {
            text-align: center;
            color: #fff;
            margin-bottom: 30px;
            font-size: 2.8em;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        .status-panel {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1));
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        .rounds-counter {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 15px;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .stat-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .input-section {
            text-align: center;
            margin-bottom: 40px;
        }
        input[type="number"] {
            font-size: 1.8em;
            padding: 15px;
            width: 120px;
            text-align: center;
            border: none;
            border-radius: 10px;
            margin: 10px;
            background: rgba(255, 255, 255, 0.9);
            color: #333;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        input[type="number"]:focus {
            outline: none;
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
            transform: scale(1.05);
            transition: all 0.3s;
        }
        .btn {
            font-size: 1.3em;
            padding: 15px 30px;
            margin: 10px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            text-transform: uppercase;
            font-weight: bold;
            letter-spacing: 1px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .btn-secondary {
            background: linear-gradient(135deg, #f093fb, #f5576c);
            color: white;
            box-shadow: 0 5px 15px rgba(245, 87, 108, 0.4);
        }
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        }
        .btn:active {
            transform: translateY(-1px);
        }
        .number-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(50px, 1fr));
            gap: 8px;
            margin: 30px 0;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }
        .number-btn {
            padding: 15px 10px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            font-size: 1.1em;
            transition: all 0.2s;
            position: relative;
            overflow: hidden;
        }
        .number-btn:hover {
            transform: scale(1.1);
            z-index: 1;
        }
        .number-zero {
            background: linear-gradient(135deg, #4ecdc4, #44a08d);
            color: white;
            box-shadow: 0 4px 15px rgba(78, 205, 196, 0.3);
        }
        .number-voisins {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        .number-other {
            background: linear-gradient(135deg, #bdc3c7, #95a5a6);
            color: white;
            box-shadow: 0 4px 15px rgba(149, 165, 166, 0.3);
        }
        .result {
            text-align: center;
            font-size: 1.4em;
            font-weight: bold;
            margin: 25px 0;
            padding: 20px;
            border-radius: 12px;
            animation: slideIn 0.5s ease-out;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .result-success {
            background: linear-gradient(135deg, rgba(39, 174, 96, 0.8), rgba(46, 204, 113, 0.8));
            border: 2px solid #27ae60;
        }
        .result-miss {
            background: linear-gradient(135deg, rgba(231, 76, 60, 0.8), rgba(192, 57, 43, 0.8));
            border: 2px solid #e74c3c;
        }
        .voisins-info {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1));
            padding: 20px;
            border-radius: 12px;
            margin-top: 30px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        .history-section {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05));
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .history-numbers {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            margin-top: 15px;
        }
        .history-number {
            padding: 8px 12px;
            border-radius: 8px;
            font-weight: bold;
            min-width: 35px;
            text-align: center;
        }
        .history-voisins {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        .history-other {
            background: linear-gradient(135deg, #bdc3c7, #95a5a6);
            color: white;
        }
        .grid-legend {
            text-align: center;
            margin-bottom: 15px;
            font-size: 1.1em;
        }
        .legend-item {
            display: inline-block;
            margin: 0 15px;
            padding: 8px 15px;
            border-radius: 8px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎰 Roulette Voisins Tracker</h1>
        
        <div class="status-panel">
            <div class="rounds-counter" id="roundsCounter">Rounds without Voisins: 0</div>
            <div class="rounds-counter" id="streakCounter" style="font-size: 2.2em; color: #2ecc71; margin-top: 10px;">Consecutive Voisins Streak: 0</div>
            <div class="stats-grid">
                <div class="stat-item">
                    <strong>Total Rounds:</strong> <span id="totalRounds">0</span>
                </div>
                <div class="stat-item">
                    <strong>Total Voisins Hits:</strong> <span id="roundsWithVoisins">0</span>
                </div>
                <div class="stat-item">
                    <strong>Last Number:</strong> <span id="lastNumber">-</span>
                </div>
            </div>
        </div>
        
        <div class="input-section">
            <div>
                <input type="number" id="numberInput" min="0" max="36" placeholder="0-36" autofocus>
            </div>
            <button class="btn btn-primary" onclick="addNumber()">Add Number</button>
            <button class="btn btn-secondary" onclick="reset()">Reset Tracker</button>
        </div>
        
        <div class="grid-legend">
            <div class="legend-item number-zero">0 (Green)</div>
            <div class="legend-item number-voisins">Voisins (Blue)</div>
            <div class="legend-item number-other">Others (Gray)</div>
        </div>
        
        <div class="number-grid" id="numberGrid">
            <!-- Numbers will be generated by JavaScript -->
        </div>
        
        <div class="result" id="result" style="display: none;"></div>
        
        <div class="history-section" id="historySection" style="display: none;">
            <h3 style="text-align: center; margin-top: 0;">📊 Recent Numbers</h3>
            <div class="history-numbers" id="historyNumbers">
                <!-- History will be displayed here -->
            </div>
        </div>
        
        <div class="voisins-info">
            <h3 style="margin-top: 0;">🎯 Voisins du Zéro Numbers</h3>
            <p style="font-size: 1.2em; font-weight: bold;">0, 2, 3, 4, 7, 12, 15, 18, 19, 21, 22, 25, 26, 28, 29, 32, 35</p>
            <div style="margin-top: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 15px; text-align: left;">
                <div style="background: rgba(231, 76, 60, 0.2); padding: 15px; border-radius: 8px; border: 1px solid rgba(231, 76, 60, 0.3);">
                    <strong>📊 Rounds without Voisins:</strong><br>
                    <small>Counts how many rounds pass without hitting any voisins number</small>
                </div>
                <div style="background: rgba(46, 204, 113, 0.2); padding: 15px; border-radius: 8px; border: 1px solid rgba(46, 204, 113, 0.3);">
                    <strong>🔥 Consecutive Voisins Streak:</strong><br>
                    <small>Counts how many voisins numbers hit in a row</small>
                </div>
            </div>
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
                input.focus();
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
                        const streak = data.status.consecutive_voisins_streak;
                        if (streak > 1) {
                            result.innerHTML = `🎯 <strong>${number}</strong> is VOISINS!<br>🔥 Streak: ${streak} consecutive voisins! | Total hits: ${data.status.rounds_with_voisins}`;
                        } else {
                            result.innerHTML = `🎯 <strong>${number}</strong> is VOISINS!<br>Streak started! | Total hits: ${data.status.rounds_with_voisins}`;
                        }
                    } else {
                        result.className = 'result result-miss';
                        result.innerHTML = `❌ <strong>${number}</strong> is NOT voisins<br>Streak broken! | Rounds without voisins: ${data.status.rounds_without_voisins}`;
                    }
                    
                    updateStatus(data.status);
                    updateHistory(data.status.history);
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
            if (!confirm('Are you sure you want to reset the tracker? This will clear all data.')) {
                return;
            }
            
            try {
                const response = await fetch('/reset', {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const result = document.getElementById('result');
                    result.style.display = 'block';
                    result.className = 'result';
                    result.style.background = 'linear-gradient(135deg, rgba(52, 152, 219, 0.8), rgba(41, 128, 185, 0.8))';
                    result.style.border = '2px solid #3498db';
                    result.style.color = 'white';
                    result.innerHTML = '✅ <strong>Tracker Reset!</strong><br>Ready to start tracking';
                    
                    updateStatus(data.status);
                    updateHistory([]);
                    document.getElementById('numberInput').focus();
                }
            } catch (error) {
                alert('Network error: ' + error.message);
            }
        }
        
        // Update status display
        function updateStatus(status) {
            const roundsCounter = document.getElementById('roundsCounter');
            const streakCounter = document.getElementById('streakCounter');
            const rounds = status.rounds_without_voisins;
            const streak = status.consecutive_voisins_streak;
            
            roundsCounter.textContent = `Rounds without Voisins: ${rounds}`;
            streakCounter.textContent = `Consecutive Voisins Streak: ${streak}`;
            
            // Color coding based on rounds without voisins
            if (rounds === 0) {
                roundsCounter.style.color = '#2ecc71';
                roundsCounter.style.textShadow = '0 0 10px rgba(46, 204, 113, 0.5)';
            } else if (rounds < 5) {
                roundsCounter.style.color = '#f39c12';
                roundsCounter.style.textShadow = '0 0 10px rgba(243, 156, 18, 0.5)';
            } else if (rounds < 10) {
                roundsCounter.style.color = '#e67e22';
                roundsCounter.style.textShadow = '0 0 10px rgba(230, 126, 34, 0.5)';
            } else {
                roundsCounter.style.color = '#e74c3c';
                roundsCounter.style.textShadow = '0 0 10px rgba(231, 76, 60, 0.5)';
            }
            
            // Color coding for consecutive voisins streak
            if (streak === 0) {
                streakCounter.style.color = '#95a5a6';
                streakCounter.style.textShadow = '0 0 10px rgba(149, 165, 166, 0.5)';
            } else if (streak < 3) {
                streakCounter.style.color = '#2ecc71';
                streakCounter.style.textShadow = '0 0 10px rgba(46, 204, 113, 0.5)';
            } else if (streak < 5) {
                streakCounter.style.color = '#f39c12';
                streakCounter.style.textShadow = '0 0 10px rgba(243, 156, 18, 0.5)';
            } else {
                streakCounter.style.color = '#e67e22';
                streakCounter.style.textShadow = '0 0 10px rgba(230, 126, 34, 0.5)';
            }
            
            document.getElementById('totalRounds').textContent = status.total_rounds;
            document.getElementById('roundsWithVoisins').textContent = status.rounds_with_voisins || 0;
            document.getElementById('lastNumber').textContent = status.last_number || '-';
        }
        
        // Update history display
        function updateHistory(history) {
            const historySection = document.getElementById('historySection');
            const historyNumbers = document.getElementById('historyNumbers');
            
            if (history && history.length > 0) {
                historySection.style.display = 'block';
                historyNumbers.innerHTML = '';
                
                // Reverse the history array to show newest numbers first (from left)
                const reversedHistory = [...history].reverse();
                
                reversedHistory.forEach(number => {
                    const span = document.createElement('span');
                    span.textContent = number;
                    span.className = 'history-number';
                    
                    if (voisinsNumbers.includes(number)) {
                        span.className += ' history-voisins';
                    } else {
                        span.className += ' history-other';
                    }
                    
                    historyNumbers.appendChild(span);
                });
            } else {
                historySection.style.display = 'none';
            }
        }
        
        // Handle Enter key
        document.getElementById('numberInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                addNumber();
            }
        });
        
        // Handle keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Press 'R' to reset
            if (e.key === 'r' || e.key === 'R') {
                if (!document.getElementById('numberInput').matches(':focus')) {
                    reset();
                }
            }
            
            // Press 'F' to focus input
            if (e.key === 'f' || e.key === 'F') {
                document.getElementById('numberInput').focus();
                e.preventDefault();
            }
        });
        
        // Initialize the page
        function initialize() {
            createNumberGrid();
            
            // Load initial status
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    updateStatus(data);
                    updateHistory(data.history || []);
                })
                .catch(error => console.log('Error loading initial status:', error));
        }
        
        // Start the application
        initialize();
    </script>
</body>
</html>
        '''

def start_server():
    PORT = 8001  # Different port to avoid conflicts
    
    try:
        with socketserver.TCPServer(("", PORT), RouletteHandler) as httpd:
            print(f"🎰 Roulette Voisins Tracker - Simple Version")
            print(f"Server running at: http://localhost:{PORT}")
            print(f"Features: Manual number input, clean UI, number grid")
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
