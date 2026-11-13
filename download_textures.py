import os
import numpy as np
from PIL import Image, ImageFilter

os.makedirs("assets/textures", exist_ok=True)


def spherical_fbm(nx: np.ndarray, ny: np.ndarray, nz: np.ndarray, octaves: int = 5, seed: int = 42) -> np.ndarray:
    """Computes seamless 3D spherical noise with zero wrapping seams."""
    rng = np.random.default_rng(seed)
    total = np.zeros_like(nx, dtype=np.float32)
    amp = 0.5
    freq = 2.2

    for _ in range(octaves):
        # Random 3D rotation/phase per octave for organic multi-scale detail
        p = rng.uniform(-10.0, 10.0, size=3).astype(np.float32)
        rot = rng.normal(0.0, 1.0, size=(3, 3)).astype(np.float32)
        q, _ = np.linalg.qr(rot)

        rx = (q[0, 0] * nx + q[0, 1] * ny + q[0, 2] * nz) * freq + p[0]
        ry = (q[1, 0] * nx + q[1, 1] * ny + q[1, 2] * nz) * freq + p[1]
        rz = (q[2, 0] * nx + q[2, 1] * ny + q[2, 2] * nz) * freq + p[2]

        # Smooth trigonometric lattice interference
        wave = (
            np.sin(rx + 0.6 * np.sin(ry * 1.3))
            * np.cos(ry + 0.6 * np.sin(rz * 1.3))
            + 0.5 * np.sin(rz * 1.7 + rx * 0.9)
        )
        total += amp * wave
        freq *= 2.05
        amp *= 0.5

    # Normalize to [0, 1]
    t_min, t_max = total.min(), total.max()
    return (total - t_min) / (t_max - t_min + 1e-6)


def generate_craters(nx: np.ndarray, ny: np.ndarray, nz: np.ndarray, count: int = 180, seed: int = 99) -> np.ndarray:
    """Generates realistic raised-rim impact craters across a 3D sphere."""
    rng = np.random.default_rng(seed)
    crater_map = np.zeros_like(nx, dtype=np.float32)

    # Random points uniformly distributed on the unit sphere
    vecs = rng.normal(0.0, 1.0, size=(count, 3)).astype(np.float32)
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
    radii = rng.uniform(0.025, 0.14, size=count).astype(np.float32) ** 1.4

    for (cx, cy, cz), r in zip(vecs, radii):
        # Great-circle chord distance squared
        d2 = (nx - cx) ** 2 + (ny - cy) ** 2 + (nz - cz) ** 2
        r2 = r * r
        mask = d2 < (r2 * 2.2)
        if not np.any(mask):
            continue
        dist = np.sqrt(d2[mask]) / r
        # Bowl depression inside (dist < 1), raised ejecta rim at (dist ~ 1.0)
        profile = np.where(
            dist < 1.0,
            -0.65 * (1.0 - dist * dist),
            0.35 * np.exp(-((dist - 1.05) ** 2) / 0.04)
        )
        crater_map[mask] += profile

    return np.clip(crater_map, -1.0, 1.0)


def lerp_color(t: np.ndarray, c1: tuple, c2: tuple) -> np.ndarray:
    t3 = t[..., None]
    return np.array(c1, dtype=np.float32) * (1.0 - t3) + np.array(c2, dtype=np.float32) * t3


def build_all_textures(width: int = 1024, height: int = 512):
    y, x = np.mgrid[0:height, 0:width].astype(np.float32)
    u = (x / width) * 2.0 * np.pi
    v = (y / height) * np.pi

    nx = np.sin(v) * np.cos(u)
    ny = np.cos(v)
    nz = np.sin(v) * np.sin(u)

    bodies = [
        "sun", "mercury", "venus", "earth", "mars",
        "jupiter", "saturn", "uranus", "neptune",
        "moon", "io", "europa", "ganymede", "callisto", "titan"
    ]

    for idx, name in enumerate(bodies):
        dest = os.path.join("assets", "textures", f"{name}.jpg")
        print(f"Synthesizing 2:1 equirectangular texture: {name}.jpg...")

        n_base = spherical_fbm(nx, ny, nz, octaves=6, seed=100 + idx * 17)
        n_fine = spherical_fbm(nx * 2.5, ny * 2.5, nz * 2.5, octaves=4, seed=500 + idx * 31)

        if name == "sun":
            # Granulated solar photosphere & active flare filaments
            granules = np.power(n_base * 0.65 + n_fine * 0.35, 1.3)
            img_arr = lerp_color(granules, (195, 45, 5), (255, 225, 70))

        elif name == "mercury":
            # Silicate grey-taupe crust with dense impact craters
            craters = generate_craters(nx, ny, nz, count=240, seed=11)
            val = np.clip(n_base * 0.6 + n_fine * 0.4 + craters * 0.25, 0.0, 1.0)
            img_arr = lerp_color(val, (88, 84, 80), (195, 190, 182))

        elif name == "venus":
            # Creamy golden-ochre & pale blue-white sulfuric cloud bands
            swirl = np.sin(ny * 7.0 + (n_base - 0.5) * 3.5)
            bands = np.clip(0.5 + 0.35 * swirl + 0.25 * (n_fine - 0.5), 0.0, 1.0)
            img_arr = lerp_color(bands, (175, 138, 98), (242, 232, 212))

        elif name == "earth":
            # Deep ocean blues, lush continents, desert belts, polar ice, and swirling clouds
            continent = n_base * 0.78 + n_fine * 0.22
            ocean_mask = continent < 0.52

            # Ocean depth shading
            ocean_t = np.clip(continent / 0.52, 0.0, 1.0)
            ocean_col = lerp_color(ocean_t, (10, 38, 95), (28, 95, 165))

            # Land biome (green forests -> tan deserts -> mountain peaks)
            land_t = np.clip((continent - 0.52) / 0.48, 0.0, 1.0)
            aridity = np.clip(1.0 - np.abs(ny) * 1.8 + (n_fine - 0.5) * 0.5, 0.0, 1.0)
            forest_col = lerp_color(land_t, (34, 98, 42), (110, 125, 75))
            desert_col = lerp_color(land_t, (175, 148, 95), (210, 190, 150))
            land_col = forest_col * (1.0 - aridity[..., None]) + desert_col * aridity[..., None]

            img_arr = np.where(ocean_mask[..., None], ocean_col, land_col)

            # Polar ice caps
            ice_mask = (np.abs(ny) + (n_fine - 0.5) * 0.12) > 0.86
            img_arr = np.where(ice_mask[..., None], np.array([242, 246, 252], dtype=np.float32), img_arr)

            # Wispy global cloud layer
            cloud_noise = spherical_fbm(nx + 0.4 * np.sin(ny * 4.0), ny, nz, octaves=5, seed=777)
            clouds = np.clip((cloud_noise - 0.54) * 2.6, 0.0, 0.88)[..., None]
            img_arr = img_arr * (1.0 - clouds) + np.array([250, 252, 255], dtype=np.float32) * clouds

        elif name == "mars":
            # Iron-oxide rust plains, dark basaltic regions, canyons, and white north polar cap
            craters = generate_craters(nx, ny, nz, count=140, seed=44)
            terrain = np.clip(n_base * 0.72 + n_fine * 0.28 + craters * 0.18, 0.0, 1.0)
            img_arr = lerp_color(terrain, (92, 42, 24), (214, 118, 62))
            polar_cap = (ny + (n_fine - 0.5) * 0.08) > 0.90
            img_arr = np.where(polar_cap[..., None], np.array([245, 240, 238], dtype=np.float32), img_arr)

        elif name == "jupiter":
            # Turbulent zonal belts, cream zones, terracotta bands, and the Great Red Spot
            turb = (n_base - 0.5) * 0.28 + (n_fine - 0.5) * 0.12
            lat = ny + turb
            zonal = 0.5 + 0.5 * np.cos(lat * 22.0)
            img_arr = lerp_color(zonal, (148, 96, 62), (235, 224, 205))
            # Add warm ochre sub-bands
            ochre = np.clip(np.sin(lat * 11.0), 0.0, 1.0)[..., None]
            img_arr = img_arr * (1.0 - 0.35 * ochre) + np.array([196, 132, 74], dtype=np.float32) * (0.35 * ochre)

            # Great Red Spot in southern hemisphere
            spot_d2 = ((nx - 0.45) / 0.26) ** 2 + ((ny + 0.36) / 0.14) ** 2 + ((nz - 0.78) / 0.26) ** 2
            spot_mask = np.clip(1.0 - spot_d2, 0.0, 1.0)[..., None]
            img_arr = img_arr * (1.0 - spot_mask * 0.85) + np.array([205, 88, 46], dtype=np.float32) * (spot_mask * 0.85)

        elif name == "saturn":
            # Smooth pale gold & butterscotch atmospheric bands
            lat = ny + (n_base - 0.5) * 0.08
            bands = 0.5 + 0.5 * np.cos(lat * 26.0)
            val = np.clip(bands * 0.7 + n_fine * 0.3, 0.0, 1.0)
            img_arr = lerp_color(val, (176, 152, 108), (234, 218, 178))

        elif name == "uranus":
            # Smooth pale cyan-aquamarine methane atmosphere with subtle polar brightening
            bands = 0.5 + 0.5 * np.cos(ny * 8.0)
            val = np.clip(bands * 0.5 + n_base * 0.5, 0.0, 1.0)
            img_arr = lerp_color(val, (152, 216, 226), (198, 240, 245))

        elif name == "neptune":
            # Deep cobalt-azure atmosphere with high-altitude white methane streaks & Great Dark Spot
            lat = ny + (n_base - 0.5) * 0.14
            bands = 0.5 + 0.5 * np.cos(lat * 18.0)
            img_arr = lerp_color(bands, (28, 68, 185), (65, 130, 242))
            streaks = np.clip((n_fine - 0.68) * 3.2, 0.0, 0.75)[..., None]
            img_arr = img_arr * (1.0 - streaks) + np.array([195, 225, 255], dtype=np.float32) * streaks

        elif name == "moon":
            # Dark basaltic lunar maria + bright cratered highlands
            craters = generate_craters(nx, ny, nz, count=260, seed=71)
            maria = n_base * 0.8 + n_fine * 0.2
            val = np.clip(maria + craters * 0.28, 0.0, 1.0)
            img_arr = lerp_color(val, (68, 70, 74), (205, 208, 212))

        elif name == "io":
            # Sulfurous yellow-orange volcanic surface
            val = np.clip(n_base * 0.65 + n_fine * 0.35, 0.0, 1.0)
            img_arr = lerp_color(val, (185, 110, 25), (248, 222, 65))

        elif name == "europa":
            # Fractured icy shell with reddish-brown lineae
            ridges = np.abs(np.sin((nx * 6.0 + ny * 4.0 + n_base * 3.0) * 3.0))
            val = np.clip(ridges * 0.65 + n_fine * 0.35, 0.0, 1.0)
            img_arr = lerp_color(val, (155, 125, 102), (235, 232, 226))

        elif name == "ganymede":
            craters = generate_craters(nx, ny, nz, count=150, seed=82)
            val = np.clip(n_base * 0.7 + n_fine * 0.3 + craters * 0.2, 0.0, 1.0)
            img_arr = lerp_color(val, (95, 88, 82), (185, 178, 168))

        elif name == "callisto":
            craters = generate_craters(nx, ny, nz, count=220, seed=93)
            val = np.clip(n_base * 0.6 + n_fine * 0.4 + craters * 0.3, 0.0, 1.0)
            img_arr = lerp_color(val, (62, 58, 55), (165, 160, 152))

        else:  # titan
            # Thick golden-orange nitrogen-methane haze
            val = np.clip(n_base * 0.6 + n_fine * 0.4, 0.0, 1.0)
            img_arr = lerp_color(val, (175, 122, 48), (228, 178, 88))

        img = Image.fromarray(np.clip(img_arr, 0, 255).astype(np.uint8), "RGB")
        img = img.filter(ImageFilter.SMOOTH_MORE)
        img.save(dest, "JPEG", quality=92)
        print(f"  [OK] Saved {dest}")


if __name__ == "__main__":
    build_all_textures()