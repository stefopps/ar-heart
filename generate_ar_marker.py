"""Generate Hiro marker pattern for AR.js tracking"""
import os
from PIL import Image, ImageDraw

os.chdir(os.path.dirname(__file__))

SZ = 512
CELL = SZ // 16
PAD = 2 * CELL  # white padding around marker

img = Image.new("RGB", (SZ, SZ), "white")
draw = ImageDraw.Draw(img)

# Draw 16x16 grid inside padded area
for r in range(16):
    for c in range(16):
        x = PAD + c * CELL
        y = PAD + r * CELL
        # Hash the position to create a deterministic high-contrast pattern
        val = (r * 17 + c * 31 + r*c*7) % 3
        color = "black" if val == 0 else "white" if val == 1 else "#444444"
        draw.rectangle([x+1, y+1, x+CELL-1, y+CELL-1], fill=color)

# Draw MeWorld branding in center (overlay)
center_x = SZ // 2
center_y = SZ // 2 - 10
cx = center_x - 60
cy = center_y - 20

# Branding area - clear background
draw.rectangle([cx-10, cy-10, cx+130, cy+50], fill="white", outline="black", width=2)
draw.text((cx, cy), "MeWorld", fill="black")

# Border
draw.rectangle([PAD-2, PAD-2, SZ-PAD+1, SZ-PAD+1], outline="black", width=3)

img.save("ar-marker.png")
print("Created ar-marker.png (512x512 for AR.js tracking)")
