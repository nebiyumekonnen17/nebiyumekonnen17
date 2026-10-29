#!/usr/bin/env python3
"""Animate the existing GitHub portrait cards without rebuilding or changing the face."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
CARD_W, CARD_H = 1135, 640
FACE_BOX = (35, 110, 435, 563)

def inside_face(x, y):
    x1, y1, x2, y2 = FACE_BOX
    return x1 <= x <= x2 and y1 <= y <= y2

def animate(theme):
    src = Image.open(ROOT / f"{theme}_mode.png").convert("RGB")
    base = src.resize((CARD_W, CARD_H), Image.Resampling.LANCZOS).convert("RGBA")
    font = ImageFont.truetype(FONT, 13)
    frames = []

    for step in range(24):
        layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for col in range(0, CARD_W, 22):
            seed = col // 22
            speed = 3 + (seed % 4)
            y_head = (step * speed * 7 + seed * 41) % (CARD_H + 220) - 140
            for k in range(8):
                y = y_head - k * 19
                if y < 0 or y >= CARD_H:
                    continue
                bit = "1" if (seed * 11 + step + k) % 2 else "0"
                if theme == "dark":
                    rgb_head, rgb_tail = (50, 235, 112), (30, 165, 81)
                    alpha = max(38, 185 - k * 18)
                else:
                    rgb_head, rgb_tail = (12, 122, 73), (14, 99, 61)
                    alpha = max(35, 175 - k * 17)
                if inside_face(col + 5, y):
                    alpha = int(alpha * 0.08)
                if col >= 450:
                    alpha = int(alpha * 0.76)
                if y >= 545:
                    alpha = int(alpha * 0.95)
                rgb = rgb_head if k == 0 else rgb_tail
                d.text((col + 4, y), bit, font=font, fill=(*rgb, alpha))
        frame = Image.alpha_composite(base, layer).convert("RGB")
        frames.append(frame.quantize(colors=128, method=Image.Quantize.FASTOCTREE))

    dest = ROOT / f"{theme}_animated.gif"
    frames[0].save(dest, save_all=True, append_images=frames[1:],
                   duration=120, loop=0, optimize=True, disposal=2)
    print(f"Generated {dest.name}: {dest.stat().st_size} bytes")

for theme in ("dark", "light"):
    animate(theme)
