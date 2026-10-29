#!/usr/bin/env python3
"""Animate the existing GitHub portrait cards without rebuilding or changing the face."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

ROOT = Path(__file__).resolve().parent
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

def animate(theme):
    # Use the original full-resolution PNG; never reconstruct the photograph.
    src = Image.open(ROOT / f"{theme}_mode.png").convert("RGB")
    # GIF dimensions remain 1135px across, matching the original card proportions.
    base = src.resize((1135, 640), Image.Resampling.LANCZOS).convert("RGBA")
    font = ImageFont.truetype(FONT, 13)
    frames = []
    for step in range(20):
        layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for col in range(0, 1135, 25):
            seed = col // 25
            y_head = (step * (3 + seed % 4) * 6 + seed * 37) % 860 - 130
            for k in range(5):
                y = y_head - k * 21
                if not 2 <= y < 634:
                    continue
                bit = "1" if (seed * 11 + step // 3 + k) % 2 else "0"
                # Very faint digits over the photo/card to preserve readability.
                alpha = int((118 - 12*k) * (0.80 if theme == "light" else 1))
                # Keep the face clear while allowing the binary to show over card margins.
                if 35 <= col <= 435 and 110 <= y <= 563:
                    alpha = int(alpha * 0.12)
                rgb = (17, 111, 77) if theme == "light" else (63, 185, 80)
                d.text((col + 4, y), bit, font=font, fill=(*rgb, alpha))
        frame = Image.alpha_composite(base, layer).convert("RGB")
        frames.append(frame.quantize(colors=256, method=Image.Quantize.FASTOCTREE))
    dest = ROOT / f"{theme}_animated.gif"
    frames[0].save(dest, save_all=True, append_images=frames[1:], duration=130,
                   loop=0, optimize=True, disposal=2)
    print(f"Generated {dest.name}: {dest.stat().st_size} bytes")

for theme in ("dark", "light"):
    animate(theme)
