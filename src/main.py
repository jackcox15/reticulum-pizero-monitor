#!/usr/bin/env python3
"""
Pi Zero Display for Reticulum
"""
import time
import psutil
import platform
from datetime import datetime
from display import DisplayManager
from services_monitor import check_rnsd, check_lora, check_wifi
from buttons import button_a, button_b, button_x, button_y

def get_stats():
    return {
        'cpu': psutil.cpu_percent(interval=0.1),
        'memory': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('/').percent,
    }

def draw_panel_pil(draw, x, y, width, height, title, theme):
    draw.rectangle([x, y, x + width, y + height], 
                   fill=theme.colors["background"], 
                   outline=theme.colors["primary"], 
                   width=2)
    if title:
        draw.rectangle([x, y, x + width, y + 25], 
                       fill=theme.colors["primary"])
        draw.text((x + 10, y + 8), title, 
                  font=theme.font_small, 
                  fill=theme.colors["background"])

class Pi_Monitor:
    def __init__(self):
        self.display = DisplayManager()
    
        self.current_screen = 0
        self.screen = ["systat", "services", "network", "setup"]
        self.max_screen = len(self.screen)
        button_a.when_pressed = self.next_screen
        button_b.when_pressed = self.previous_screen
        
    def get_status_color(self, value, theme, warning_threshold, error_threshold):
        if value < warning_threshold:
            return theme.colors["success"]
        elif value < error_threshold:
            return theme.colors["warning"]
        else:
            return theme.colors["fail"]
    
    def next_screen(self):
        self.current_screen = (self.current_screen + 1) % self.max_screen
        print(f"Next Screen: {self.screen[self.current_screen]}")
        
    def previous_screen(self):
        self.current_screen = (self.current_screen -1) % self.max_screen
        print(f"Previous Screen: {self.screen[self.current_screen]}")
        
        
        
    def draw_status_screen(self, draw, theme, stats, timestamp):
         
        # Title
        draw.text((120, 10), "Reticulum Monitor", 
                  font=theme.font_medium, 
                  fill=theme.colors["primary"], 
                  anchor="mm")
        
        # Time panel
        draw_panel_pil(draw, 10, 25, 220, 50, "Time", theme)
        draw.text((20, 55), timestamp, 
                  font=theme.font_medium, 
                  fill=theme.colors["text"])
        
        # System stats panel
        draw_panel_pil(draw, 10, 80, 220, 80, "System Status", theme)
        
        # CPU
        cpu_color = self.get_status_color(stats['cpu'], theme, 50, 80)
        draw.text((20, 105), f"CPU: {stats['cpu']:.1f}%", 
                  font=theme.font_small, fill=cpu_color)
        
        # Memory
        mem_color = self.get_status_color(stats['memory'], theme, 70, 85)
        draw.text((20, 125), f"RAM: {stats['memory']:.1f}%", 
                  font=theme.font_small, fill=mem_color)
        
        # Disk
        disk_color = self.get_status_color(stats['disk'], theme, 80, 90)
        draw.text((20, 145), f"Disk: {stats['disk']:.1f}%", 
                  font=theme.font_small, fill=disk_color)
        
        # Platform info
        draw_panel_pil(draw, 10, 170, 220, 60, "Platform", theme)
        draw.text((20, 195), f"OS: {platform.system()}", 
                  font=theme.font_small, fill=theme.colors["text"])
        draw.text((20, 215), f"Arch: {platform.machine()}", 
                  font=theme.font_small, fill=theme.colors["text"])
    
    def draw_services_screen(self, draw, theme, stats, timestamp):
        rnsd_running = check_rnsd()
        lora_connected = check_lora()
        wifi_active = check_wifi()
        
        #Status screen title
        draw.text((120, 10), "Services Monitor",
                  font=theme.font_medium, fill=theme.colors["primary"],
                  anchor="mm")
        
        #checking RNSD status
        draw_panel_pil(draw, 10, 30, 220, 47, "Reticulum Daemon", theme)
        if rnsd_running:
            draw.text((18, 55), "Status: RUNNING",
                      font=theme.font_small, fill=theme.colors["success"])
        else:
            draw.text((18, 55), "Status: STOPPED", font=theme.font_small, fill=theme.colors["fail"])
            
        #check LoRa USB connection
        draw_panel_pil(draw, 10, 80, 220, 47, "LoRa Radio", theme)
        if lora_connected:
            draw.text((18, 105), "Status: CONNECTED",
                      font=theme.font_small, fill=theme.colors["success"])
        else:
            draw.text((18, 105), "Status: NOT FOUND", font=theme.font_small,
                      fill=theme.colors["fail"])
            
        #check WiFi AP status
        draw_panel_pil(draw, 10, 130, 220, 47, "Wifi Access Point", theme)
        if wifi_active:
            draw.text((20, 155), "Status: ACTIVE", font=theme.font_small, fill=theme.colors["success"])
                

    def draw_network_screen(self, draw, theme, stats, timestamp):
        draw.text((120, 120), "Network Monitoring",
                  font=theme.font_large, fill=theme.colors["primary"], anchor="mm")
        
    def draw_setup_screen(self, draw, theme, stats, timestamp):
        draw.text((120, 120), "Setup",
                  font=theme.font_large, fill=theme.colors["primary"], anchor="mm")
     
    def render_current_screen(self, draw, theme, stats, timestamp):
        if self.current_screen == 0:
            self.draw_status_screen(draw, theme, stats, timestamp)
        elif self.current_screen == 1:  
            self.draw_services_screen(draw, theme, stats, timestamp)
        elif self.current_screen == 2:
            self.draw_network_screen(draw, theme, stats, timestamp)
        elif self.current_screen == 3: 
            self.draw_setup_screen(draw, theme, stats, timestamp)
        
    def run(self):
        print("Reticulum Pi Monitor")
        print("Press Ctrl+C to exit\n")
        
        try:
            while True:
                stats = get_stats()
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Render to hardware display
                self.display.render(lambda draw, theme:
                                    self.render_current_screen(draw, theme, stats, timestamp))
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("Monitor stopped")

if __name__ == '__main__':
    app = Pi_Monitor()
    app.run()
