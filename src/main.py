#!/usr/bin/env python3
"""
Simple Pi Zero Display for Reticulum
"""
import time
import psutil
import platform
from datetime import datetime
import tkinter as tk
from theme import Theme

def get_stats():
    return {
        'cpu': psutil.cpu_percent(interval=0.1),
        'memory': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('/').percent,
    }

def draw_panel(canvas, x, y, width, height, title, theme):
    canvas.create_rectangle(x, y, x + width, y + height, 
                           fill=theme.colors["background"], 
                           outline=theme.colors["primary"], width=2)
    if title:
        canvas.create_rectangle(x, y, x + width, y + 25, 
                               fill=theme.colors["primary"], outline="")
        canvas.create_text(x + 10, y + 12, text=title, 
                          fill=theme.colors["background"], 
                          anchor='w', font=("Courier", 10, "bold"))

class SimpleDisplay:
    def __init__(self):
        self.theme = Theme()
        self.root = tk.Tk()
        self.root.title("Reticulum Monitor")
        self.root.geometry("480x480")
        self.root.configure(bg='black')
        
        self.canvas = tk.Canvas(self.root, width=480, height=480, bg='black')
        self.canvas.pack()
        
        print("Display ready")
    
    def get_status_color(self, value, warning_threshold, error_threshold):
        """Return color based on status value"""
        if value < warning_threshold:
            return self.theme.colors["success"]
        elif value < error_threshold:
            return self.theme.colors["warning"]
        else:
            return self.theme.colors["fail"]
        
    def display_organized(self, stats, timestamp):
        self.canvas.delete("all")
        
        # Title text
        self.canvas.create_text(240, 20, text="Reticulum Monitor", 
                               fill=self.theme.colors["primary"], 
                               font=("Courier", 16, "bold"))
        
        # Time panel
        draw_panel(self.canvas, 20, 40, 440, 50, "Current Time:", self.theme)
        self.canvas.create_text(30, 80, text=timestamp, 
                               fill=self.theme.colors["text"], 
                               anchor="w", font=("Courier", 12))
        
        # System stats panel
        draw_panel(self.canvas, 20, 90, 440, 120, "System Status", self.theme)
        
        # CPU with color coding
        cpu_color = self.get_status_color(stats['cpu'], 50, 80)
        self.canvas.create_text(30, 140, text=f"CPU Usage: {stats['cpu']:.1f}%", 
                               fill=cpu_color, anchor='w', font=('Courier', 11))
        
        # Memory with color coding
        mem_color = self.get_status_color(stats['memory'], 70, 85)
        self.canvas.create_text(30, 160, text=f"Memory Usage: {stats['memory']:.1f}%", 
                               fill=mem_color, anchor='w', font=('Courier', 11))
        
        # Disk with color coding
        disk_color = self.get_status_color(stats['disk'], 80, 90)
        self.canvas.create_text(30, 180, text=f"Disk Usage: {stats['disk']:.1f}%", 
                               fill=disk_color, anchor='w', font=('Courier', 11))
        
        # Platform info panel
        draw_panel(self.canvas, 20, 240, 440, 80, "Platform Info", self.theme)
        self.canvas.create_text(30, 280, text=f"OS: {platform.system()}", 
                               fill=self.theme.colors["text"], anchor='w', font=('Courier', 11))
        self.canvas.create_text(30, 300, text=f"Architecture: {platform.machine()}", 
                               fill=self.theme.colors["text"], anchor='w', font=('Courier', 11))
        
        self.root.update()


#Main function execution
class SimpleApp:
    def __init__(self):
        self.display = SimpleDisplay()
    
    def run(self):
        print("Reticulum Pi Zero Monitor")
        print("Press Ctrl+C to exit\n")
        
        try:
            while True:
                stats = get_stats()
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                self.display.display_organized(stats, timestamp)
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("Monitor stopped")

if __name__ == '__main__':
    app = SimpleApp()
    app.run()

