#!/usr/bin/env python3
"""
Roulette Voisins Tracker - GUI Version

A visual interface for tracking roulette numbers and counting rounds
without hitting a "voisins du zéro" number.
"""

import tkinter as tk
from tkinter import messagebox

class RouletteVoisinsTracker:
    def __init__(self):
        # Voisins du zéro numbers (neighbors of zero in European roulette)
        self.voisins_numbers = {22, 18, 29, 7, 28, 12, 35, 3, 26, 0, 32, 15, 19, 4, 21, 2, 25}
        self.rounds_without_voisins = 0
        self.total_rounds = 0
        self.history = []
        
    def is_voisins(self, number):
        """Check if a number is a voisins number"""
        return number in self.voisins_numbers
    
    def add_number(self, number):
        """Add a new roulette number and update counters"""
        if not (0 <= number <= 36):
            raise ValueError("Roulette number must be between 0 and 36")
        
        self.history.append(number)
        self.total_rounds += 1
        
        if self.is_voisins(number):
            self.rounds_without_voisins = 0
            return True  # Hit a voisins number
        else:
            self.rounds_without_voisins += 1
            return False  # Not a voisins number
    
    def get_status(self):
        """Get current status"""
        return {
            'rounds_without_voisins': self.rounds_without_voisins,
            'total_rounds': self.total_rounds,
            'last_number': self.history[-1] if self.history else None,
            'last_voisins_hit': self.get_last_voisins_number()
        }
    
    def get_last_voisins_number(self):
        """Get the last voisins number that was hit"""
        for number in reversed(self.history):
            if self.is_voisins(number):
                return number
        return None
    
    def reset(self):
        """Reset the tracker"""
        self.rounds_without_voisins = 0
        self.total_rounds = 0
        self.history = []

class RouletteGUI:
    def __init__(self, root):
        self.root = root
        self.tracker = RouletteVoisinsTracker()
        self.setup_ui()
        self.update_display()
        
    def setup_ui(self):
        self.root.title("🎰 Roulette Voisins Tracker")
        self.root.geometry("600x500")
        self.root.configure(bg='#2c3e50')
        
        # Make sure the window appears on top
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#2c3e50', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="🎰 Roulette Voisins Tracker", 
            font=('Arial', 20, 'bold'),
            fg='#e74c3c',
            bg='#2c3e50'
        )
        title_label.pack(pady=(0, 20))
        
        # Status frame
        status_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Status labels
        self.status_label = tk.Label(
            status_frame,
            text="Rounds without Voisins: 0",
            font=('Arial', 16, 'bold'),
            fg='#ecf0f1',
            bg='#34495e',
            pady=10
        )
        self.status_label.pack()
        
        self.total_rounds_label = tk.Label(
            status_frame,
            text="Total Rounds: 0",
            font=('Arial', 12),
            fg='#bdc3c7',
            bg='#34495e'
        )
        self.total_rounds_label.pack()
        
        self.last_number_label = tk.Label(
            status_frame,
            text="Last Number: -",
            font=('Arial', 12),
            fg='#bdc3c7',
            bg='#34495e'
        )
        self.last_number_label.pack()
        
        # Number input frame
        input_frame = tk.Frame(main_frame, bg='#2c3e50')
        input_frame.pack(pady=(0, 20))
        
        tk.Label(
            input_frame,
            text="Enter Roulette Number (0-36):",
            font=('Arial', 14),
            fg='#e74c3c',
            bg='#2c3e50'
        ).pack()
        
        self.number_entry = tk.Entry(
            input_frame,
            font=('Arial', 16),
            width=10,
            justify=tk.CENTER,
            bg='white',
            fg='black'
        )
        self.number_entry.pack(pady=10)
        self.number_entry.bind('<Return>', self.on_enter_pressed)
        self.number_entry.focus()
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg='#2c3e50')
        buttons_frame.pack(pady=(0, 20))
        
        self.add_button = tk.Button(
            buttons_frame,
            text="Add Number",
            command=self.add_number,
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=10
        )
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = tk.Button(
            buttons_frame,
            text="Reset",
            command=self.reset_tracker,
            font=('Arial', 12),
            bg='#95a5a6',
            fg='white',
            padx=20,
            pady=10
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # Roulette numbers grid
        self.create_number_grid(main_frame)
        
        # Voisins info
        voisins_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=1)
        voisins_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Label(
            voisins_frame,
            text="Voisins du Zéro: 0, 2, 3, 4, 7, 12, 15, 18, 19, 21, 22, 25, 26, 28, 29, 32, 35",
            font=('Arial', 10),
            fg='#bdc3c7',
            bg='#34495e',
            pady=5,
            wraplength=550
        ).pack()
        
        # Result display
        self.result_label = tk.Label(
            main_frame,
            text="Ready to track roulette numbers!",
            font=('Arial', 12, 'bold'),
            bg='#2c3e50',
            fg='#3498db',
            pady=10
        )
        self.result_label.pack()
        
    def create_number_grid(self, parent):
        # Create a simpler grid of clickable numbers
        grid_frame = tk.Frame(parent, bg='#2c3e50')
        grid_frame.pack(pady=10)
        
        tk.Label(
            grid_frame,
            text="Click a number:",
            font=('Arial', 12),
            fg='#e74c3c',
            bg='#2c3e50'
        ).pack(pady=(0, 10))
        
        # Create buttons for numbers 0-36 in a grid
        button_frame = tk.Frame(grid_frame, bg='#2c3e50')
        button_frame.pack()
        
        for i in range(37):  # 0 to 36
            row = i // 10
            col = i % 10
            
            color = self.get_number_color(i)
            
            btn = tk.Button(
                button_frame,
                text=str(i),
                command=lambda n=i: self.add_number_from_grid(n),
                width=3,
                height=1,
                font=('Arial', 10, 'bold'),
                bg=color,
                fg='white' if color != '#f39c12' else 'black'
            )
            btn.grid(row=row, column=col, padx=1, pady=1)
    
    def get_number_color(self, num):
        if num == 0:
            return '#27ae60'  # Green for 0
        elif num in self.tracker.voisins_numbers:
            return '#3498db'  # Blue for voisins
        else:
            return '#7f8c8d'  # Gray for others
    
    def add_number_from_grid(self, number):
        self.number_entry.delete(0, tk.END)
        self.number_entry.insert(0, str(number))
        self.add_number()
    
    def get_number_color(self, num):
        if num == 0:
            return '#32CD32'  # Green for 0
        elif num in self.tracker.voisins_numbers:
            return '#4169E1'  # Blue for voisins
        elif num in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]:
            return '#DC143C'  # Red
        else:
            return '#000000'  # Black
    
    def on_enter_pressed(self, event):
        self.add_number()
    
    def add_number_from_table(self, number):
        self.number_entry.delete(0, tk.END)
        self.number_entry.insert(0, str(number))
        self.add_number()
    
    def add_number(self):
        try:
            number_text = self.number_entry.get().strip()
            if not number_text:
                messagebox.showwarning("Warning", "Please enter a number!")
                return
                
            number = int(number_text)
            
            if not (0 <= number <= 36):
                messagebox.showerror("Error", "Number must be between 0 and 36!")
                return
            
            is_voisins_hit = self.tracker.add_number(number)
            
            # Clear the entry
            self.number_entry.delete(0, tk.END)
            self.number_entry.focus()
            
            # Show result
            if is_voisins_hit:
                self.result_label.configure(
                    text=f"🎯 {number} is VOISINS! Counter reset to 0",
                    fg='#27ae60'
                )
            else:
                self.result_label.configure(
                    text=f"❌ {number} is NOT voisins. Continue tracking...",
                    fg='#e74c3c'
                )
            
            self.update_display()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number!")
    
    def reset_tracker(self):
        self.tracker.reset()
        self.result_label.configure(text="✅ Tracker reset!", fg='#3498db')
        self.update_display()
        self.number_entry.focus()
    
    def update_display(self):
        status = self.tracker.get_status()
        
        # Update status display with color coding
        rounds_without = status['rounds_without_voisins']
        if rounds_without == 0:
            color = '#27ae60'  # Green
        elif rounds_without < 10:
            color = '#f39c12'  # Yellow
        elif rounds_without < 20:
            color = '#e67e22'  # Orange
        else:
            color = '#e74c3c'  # Red
            
        self.status_label.configure(
            text=f"Rounds without Voisins: {rounds_without}",
            fg=color
        )
        
        self.total_rounds_label.configure(
            text=f"Total Rounds: {status['total_rounds']}"
        )
        
        last_num = status['last_number'] if status['last_number'] is not None else "-"
        self.last_number_label.configure(
            text=f"Last Number: {last_num}"
        )

def main():
    root = tk.Tk()
    app = RouletteGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
