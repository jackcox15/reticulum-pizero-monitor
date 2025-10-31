# ST7789 Display program
from PIL import Image, ImageDraw
import st7789
from theme import Theme

class DisplayManager:
    def __init__(self):
        self.theme = Theme()
        self.disp = st7789.ST7789(
            height=240, width=240, rotation=90,
            port=0, cs=1, dc=9, backlight=13, spi_speed_hz=80000000
        )

    def render(self, render_fn):
        img = Image.new("RGB", (240, 240), color=self.theme.colors["background"])
        draw = ImageDraw.Draw(img)
        try:
            render_fn(draw, self.theme)
        except Exception as e:
            # Draw a small error notice but keep app alive
            msg = self.theme.sanitize(f"UI error:\n{e}")
            draw.text((10, 10), msg, font=self.theme.font_small, fill=self.theme.colors["fail"])
        self.disp.display(img)
