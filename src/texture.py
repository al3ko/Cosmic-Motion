import os
import math
import moderngl
import numpy as np
from PIL import Image, ImageDraw


def generate_ring_texture(ctx: moderngl.Context, planet_name: str) -> moderngl.Texture:
    """Create a radial ring map: image V is radius and image U is azimuth."""
    width, height = 256, 1024
    name = planet_name.lower()
    base_col = {
        "saturn": (205, 177, 126),
        "uranus": (130, 157, 164),
        "neptune": (139, 133, 120),
    }.get(name, (180, 170, 150))

    rng = np.random.default_rng(sum(ord(c) for c in name))
    pixels = np.zeros((height, width, 4), dtype=np.uint8)
    angle = np.linspace(0.0, 2.0 * math.pi, width, endpoint=False)
    azimuth = 0.78 + 0.22 * (0.5 + 0.5 * np.sin(angle * 7.0 + 0.8))

    for y in range(height):
        r = y / (height - 1)
        grain = math.sin(r * 680.0) * 0.10 + math.sin(r * 1730.0) * 0.045

        if name == "saturn":
            # C, B and A rings with the Cassini and Encke divisions.
            if r < 0.08 or r > 0.99 or 0.72 <= r <= 0.765 or 0.895 <= r <= 0.902:
                opacity = 0
            elif r < 0.24:
                opacity = 72 + 20 * math.sin(r * 155.0)  # translucent C ring
            elif r < 0.565:
                opacity = 218 + 24 * math.sin(r * 390.0)  # dense B ring
            else:
                opacity = 156 + 35 * math.sin(r * 305.0)  # A ring
        elif name == "uranus":
            # Narrow, dark rings with many thin gaps.
            bands = 0.5 + 0.5 * math.sin(r * 520.0)
            opacity = 18 + 88 * bands if 0.12 < r < 0.94 else 0
            if any(abs(r - gap) < 0.012 for gap in (0.31, 0.57, 0.79)):
                opacity = 0
        else:
            # Neptune's faint dusty rings and incomplete arc-like clumps.
            bands = 0.5 + 0.5 * math.sin(r * 330.0)
            opacity = (15 + 48 * bands) if 0.16 < r < 0.95 else 0
            azimuth = 0.12 + 0.88 * np.clip((np.sin(angle * 2.0 + r * 8.0) + 0.25) * 1.5, 0.0, 1.0)

        opacity = max(0, min(255, int(opacity * max(0.65, min(1.15, 1.0 + grain)))))
        color_noise = rng.integers(-8, 9, size=width)
        for channel, base in enumerate(base_col):
            pixels[y, :, channel] = np.clip((base + color_noise) * azimuth, 0, 255).astype(np.uint8)
        pixels[y, :, 3] = np.clip(opacity * azimuth, 0, 255).astype(np.uint8)

    img = Image.fromarray(pixels, "RGBA")
    texture = ctx.texture(img.size, 4, img.tobytes(), alignment=1)
    texture.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
    texture.build_mipmaps()
    texture.repeat_x = True
    texture.repeat_y = False
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
    """Load a 2:1 equirectangular surface map, falling back to a generated map."""
    if not os.path.isfile(path):
        return generate_procedural_texture(ctx, body_name)

    with Image.open(path) as source:
        image = source.convert("RGB").transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        texture = ctx.texture(image.size, 3, image.tobytes(), alignment=1)

    texture.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
    texture.build_mipmaps()
    texture.repeat_x = True
    texture.repeat_y = False
    return texture
