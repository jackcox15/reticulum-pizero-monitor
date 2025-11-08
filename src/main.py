#!/usr/bin/env python3

import time
import psutil
import platform
from datetime import datetime
from display import DisplayManager
from services_monitor import check_rnsd, check_lora, check_wifi
from diag import check_rnsd, check_lora, get_rnstatus, parse_traffic, check_wifi, get_active_interfaces, get_interface_traffic
from buttons import button_a, button_b, button_x, button_y

def get_stats():
    return {
        'cpu': psutil.cpu_percent(interval=0.1),
        'memory': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('/').percent,
    }

def draw_graph(draw, x, y, width, height, data, color, max_value=100):
   
    if len(data) < 2:
        return
    
    x_step = width / (len(data) - 1)
    
    for i in range(len(data) - 1):
        val1 = data[i]
        x1 = x + (i * x_step)
        y1 = y + height - ((val1 / max_value) * height)
        
        val2 = data[i + 1]
        x2 = x + ((i + 1) * x_step)
        y2 = y + height - ((val2 / max_value) * height)
        
        draw.line([(x1, y1), (x2, y2)], fill=color, width=2)

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
        
        #network monitor
        self.lora_tx_history = []
        self.lora_rx_history = []
        self.ip_tx_history = []
        self.ip_rx_history = []
        self.prev_ip_bytes_sent = 0
        self.prev_ip_bytes_recv = 0
        self.active_interface = None
        
        print("DEBUGGING: Init complete, all attributes set")
        
        
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
        
        
#####################################################################################
        
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
        
###########################################################################
        
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
            draw.text((18, 58), "Status: RUNNING",
                      font=theme.font_small, fill=theme.colors["success"])
        else:
            draw.text((18, 58), "Status: STOPPED", font=theme.font_small, fill=theme.colors["fail"])
            
        #check LoRa USB connection
        draw_panel_pil(draw, 10, 80, 220, 47, "LoRa Radio", theme)
        if lora_connected:
            draw.text((18, 108), "Status: CONNECTED",
                      font=theme.font_small, fill=theme.colors["success"])
        else:
            draw.text((18, 108), "Status: NOT FOUND", font=theme.font_small,
                      fill=theme.colors["fail"])
            
        #check WiFi AP status
        draw_panel_pil(draw, 10, 130, 220, 47, "Wifi Access Point", theme)
        if wifi_active:
            draw.text((20, 155), "Status: ACTIVE", font=theme.font_small, fill=theme.colors["success"])

###############################################################################

    def draw_network_screen(self, draw, theme, stats, timestamp):
        rnstatus_output = get_rnstatus()
        traffic_data = parse_traffic(rnstatus_output)
        
        #LoRa traffic monitoring
        if traffic_data is not None:
            tx_bps = traffic_data['tx_bps']
            rx_bps = traffic_data['rx_bps']
        else:
            tx_bps = 0
            rx_bps = 0
            
        self.lora_tx_history.append(tx_bps)
        self.lora_rx_history.append(rx_bps)
        
        if len(self.lora_tx_history) > 30:
            self.lora_tx_history.pop(0)
        if len(self.lora_rx_history) > 30:
            self.lora_rx_history.pop(0)
        
        #IP traffic monitoring
        active_interfaces = get_active_interfaces()
        
        print(f"DEBUG: Active interfaces: {active_interfaces}")  # ADD THIS
        print(f"DEBUG: Current active_interface: {self.active_interface}")  # ADD THIS

        
        if active_interfaces:
            if self.active_interface is None or self.active_interface not in active_interfaces:
                self.active_interface = active_interfaces[0]
                print(f"DEBUG: Set active_interface to: {self.active_interface}") 
                
            traffic = get_interface_traffic(self.active_interface)
            
            if traffic is not None:
                ip_tx_bps = (traffic['bytes_sent'] - self.prev_ip_bytes_sent) * 8
                ip_rx_bps = (traffic['bytes_recv'] - self.prev_ip_bytes_recv) * 8
                
                if ip_tx_bps < 0:
                    ip_tx_bps = 0
                if ip_rx_bps < 0:
                    ip_rx_bps = 0
                
                self.prev_ip_bytes_sent = traffic['bytes_sent']
                self.prev_ip_bytes_recv = traffic['bytes_recv']
                
                self.ip_tx_history.append(ip_tx_bps)
                self.ip_rx_history.append(ip_rx_bps)
                
                if len(self.ip_tx_history) > 30:
                    self.ip_tx_history.pop(0)
                if len(self.ip_rx_history) > 30:
                    self.ip_rx_history.pop(0)
            else:
                ip_tx_bps = 0
                ip_rx_bps = 0
        else:
            ip_tx_bps = 0
            ip_rx_bps = 0
            self.active_interface = None
            
        
        #draw LoRa and IP monitoring graphs + text
        draw.text((120, 10), "Network Monitoring", font=theme.font_medium, fill=theme.colors["primary"], anchor="mm")
        
        draw_panel_pil(draw, 10, 30, 220, 70, "LoRa Network", theme)
        draw.text((18, 58), f"TX: {tx_bps} bps / RX: {rx_bps} bps", font=theme.font_small, fill=theme.colors["text"])
        
        draw_graph(draw, 15, 65, 210, 30, self.lora_tx_history, theme.colors["success"], max_value=1000)
               
        draw_panel_pil(draw, 10, 110, 220, 70, "IP Monitoring", theme)
                
        if self.active_interface:
            # Convert to Kbps for readability
            tx_kbps = ip_tx_bps / 1000
            rx_kbps = ip_rx_bps / 1000
            
            # Text starts after title bar (Y=135) + padding
            draw.text((18, 140), f"{self.active_interface}", 
                      font=theme.font_small, fill=theme.colors["text"])
            draw.text((18, 152), f"TX: {tx_kbps:.1f}K", 
                      font=theme.font_small, fill=theme.colors["success"])
            draw.text((18, 164), f"RX: {rx_kbps:.1f}K",
                      font=theme.font_small, fill=theme.colors["warning"])
            
            # Graph positioned properly inside panel
            # Panel content starts at Y=135, give 40px for text, then graph
            draw_graph(draw, 15, 178, 210, 35, self.ip_tx_history, 
                       theme.colors["warning"], max_value=100000)
        else:
            draw.text((18, 145), "No active interface", 
                      font=theme.font_small, fill=theme.colors["fail"])
                        
                
        

    
#################################################################################
        
    def draw_setup_screen(self, draw, theme, stats, timestamp):
        draw.text((120, 120), "Setup",
                  font=theme.font_large, fill=theme.colors["primary"], anchor="mm")
     
    
#################################################################################
        
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
