#!/usr/bin/env python3
"""
Theme configuration for the display
Defines colors, fonts, and visual styling
"""

from PIL import ImageFont

class Theme:
    def __init__(self):
        # Color palette - using hex color codes
        # Format: "#RRGGBB" where RR=red, GG=green, BB=blue in hexadecimal
        self.colors = {
            "background": "#000000",  # Black
            "primary": "#f8f8ff",      # Ghost White
            "secondary": "#a9a9a9",    # Dark Grey
            "success": "#06ffa5",      # Bright green - for "online" status
            "fail": "#ff006e",         # Pink/red - for "offline" or errors
            "warning": "#ffbe0b",      # Yellow
            "text": "#e0e0e0",         # Light gray - readable text
        }
        
        # Load fonts
        # PIL (Python Imaging Library) uses TrueType fonts
        # We try to load custom fonts, but fall back to default if not found
        try:
            # DejaVu is a common font family on Linux systems
            self.font_large = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24
            )
            self.font_medium = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18
            )
            self.font_small = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14
            )
        except OSError:
            # If custom fonts aren't found, use PIL's basic font
            print("Warning: Could not load custom fonts, using default")
            self.font_large = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
    
    def sanitize(self, text):
        # Encode to ASCII, ignoring characters that don't fit
        # Then decode back to string
        return text.encode('ascii', 'ignore').decode('ascii')
