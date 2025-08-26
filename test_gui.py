#!/usr/bin/env python3
"""
Simple test for tkinter GUI functionality
"""

import tkinter as tk
from tkinter import messagebox

def test_gui():
    root = tk.Tk()
    root.title("GUI Test")
    root.geometry("300x200")
    
    label = tk.Label(root, text="GUI is working!", font=('Arial', 16))
    label.pack(pady=50)
    
    def show_message():
        messagebox.showinfo("Test", "GUI is working correctly!")
    
    button = tk.Button(root, text="Test Button", command=show_message, font=('Arial', 12))
    button.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    test_gui()
