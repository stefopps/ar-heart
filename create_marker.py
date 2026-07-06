import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

os.chdir(os.path.dirname(__file__))

# Create a high-contrast tracking marker (512x512)
# MindAR needs: asymmetric, high contrast, detail across the image
size = 512
img = Image.new("RGB", (size, size), "white")
draw = ImageDraw.Draw(img)

# Draw asymmetric high-contrast pattern
# Outer border for edge detection
draw.rectangle([12, 12, size-13, size-13], outline="black", width=4)

# Top-left: large dark square
draw.rectangle([30, 30, 180, 180], fill="black")
draw.rectangle([45, 45, 165, 165], fill="white")
draw.ellipse([65, 65, 145, 145], fill="black")

# Top-right: diagonal stripes
for i in range(6):
    x0 = 320 + i * 28
    y0 = 30
    x1 = x0 + 16
    y1 = 180
    color = "black" if i % 2 == 0 else "#333333"
    draw.rectangle([x0, y0, x1, y1], fill=color)

# Middle: cross pattern (asymmetric)
draw.rectangle([140, 200, 370, 210], fill="black")
draw.rectangle([140, 210, 155, 340], fill="black")
draw.rectangle([200, 270, 370, 285], fill="#555555")
draw.rectangle([355, 210, 370, 340], fill="#555555")

# Bottom-left: concentric circles
for r in range(70, 10, -15):
    color = "black" if r % 30 == 0 else "#444444"
    draw.ellipse([60, 350, 60+r*2, 350+r*2], outline=color, width=3)

# Bottom-right: checkerboard grid
cell = 28
for row in range(4):
    for col in range(4):
        x = 300 + col * cell
        y = 350 + row * cell
        if (row + col) % 2 == 0:
            draw.rectangle([x, y, x+cell, y+cell], fill="black")

# Center: distinctive "MeWorld" icon
draw.rectangle([200, 210, 310, 315], fill="white", outline="black", width=3)
draw.ellipse([220, 230, 290, 295], fill="black")
# Circle inside
draw.ellipse([235, 245, 275, 280], fill="white")

img.save("marker.png")
print("Created marker.png (512x512)")
