import os
import math
import moderngl
import numpy as np
from PIL import Image, ImageDraw


def generate_ring_texture(ctx: moderngl.Context, planet_name: str) -> moderngl.Texture:
    """Generates procedural high-resolution alpha ring textures with realistic Cassini/Encke gaps."""
    width, height = 512, 64
    img = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    name = planet_name.lower()
    if name == "saturn":
        base_col = (215, 185, 130)
    elif name == "uranus":
        base_col = (160, 220, 230)
    else:  # Neptune
        base_col = (100, 140, 230)

    for x in range(width):
        t = x / float(width)  # 0.0 (inner) to 1.0 (outer)
        
        # Cassini division gap & outer ring falloffs
        if 0.55 < t < 0.62 or t < 0.05 or t > 0.95:
            alpha = 0
        elif 0.3 < t < 0.33:  # Encke gap
            alpha = 20
        else:
            # Concentric ring bands variance
            band = math.sin(t * 120.0) * 40 + math.sin(t * 40.0) * 30
            alpha = max(40, min(220, int(160 + band)))

        r = max(0, min(255, int(base_col[0] + np.random.uniform(-10, 10))))
        g = max(0, min(255, int(base_col[1] + np.random.uniform(-10, 10))))
        b = max(0, min(255, int(base_col[2] + np.random.uniform(-10, 10))))

        draw.line([(x, 0), (x, height)], fill=(r, g, b, alpha))

    texture = ctx.texture(img.size, 4, img.tobytes())
    texture.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
    texture.build_mipmaps()
    return texture


def generate_procedural_texture(ctx: moderngl.Context, name: str) -> moderngl.Texture:
    width, height = 1024, 512
    img = Image.new('RGBA', (width, height), color=(200, 200, 200, 255))
    draw = ImageDraw.Draw(img)

    body_key = name.lower()
    np.random.seed(sum(ord(c) for c in body_key))

    colors = {
        "sun": (255, 190, 20),
        "mercury": (150, 145, 140),
        "venus": (220, 180, 110),
        "earth": (25, 95, 210),
        "mars": (195, 65, 35),
        "jupiter": (205, 140, 85),
        "saturn": (215, 185, 130),
        "uranus": (120, 205, 215),
        "neptune": (50, 80, 210),
        "moon": (160, 160, 160),
    }
    base = colors.get(body_key, (180, 180, 180))

    for y in range(height):
        if body_key in ["jupiter", "saturn", "uranus", "neptune"]:
            band_wave = math.sin(y / 12.0) * 35.0 + math.sin(y / 4.0) * 15.0
            r = max(0, min(255, int(base[0] + band_wave)))
            g = max(0, min(255, int(base[1] + band_wave * 0.8)))
            b = max(0, min(255, int(base[2] + band_wave * 0.6)))
        elif body_key == "sun":
            flare = math.sin(y / 6.0) * 20.0
            r, g, b = 255, max(0, min(255, int(base[1] + flare))), max(0, min(255, int(base[2] + flare * 0.5)))
        else:
            r, g, b = base
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    if body_key == "earth":
        for _ in range(35):
            cx, cy = np.random.randint(0, width), np.random.randint(60, height - 60)
            rx, ry = np.random.randint(30, 90), np.random.randint(20, 60)
            draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(45, 140, 55, 255))
        draw.rectangle([0, 0, width, 35], fill=(240, 245, 255, 255))
        draw.rectangle([0, height - 35, width, height], fill=(240, 245, 255, 255))

    elif body_key == "jupiter":
        spot_x, spot_y = int(width * 0.6), int(height * 0.65)
        draw.ellipse([spot_x - 45, spot_y - 25, spot_x + 45, spot_y + 25], fill=(180, 50, 30, 255))

    elif body_key == "mars":
        draw.rectangle([0, 0, width, 25], fill=(245, 245, 250, 255))
        draw.rectangle([0, height - 25, width, height], fill=(245, 245, 250, 255))

    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    texture = ctx.texture(img.size, 4, img.tobytes())
    texture.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
    texture.build_mipmaps()
    return texture


def load_texture(ctx: moderngl.Context, path: str, body_name: str = "default") -> moderngl.Texture:
    return generate_procedural_texture(ctx, body_name)