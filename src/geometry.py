import math
import numpy as np


def generate_uv_sphere(radius=1.0, rings=32, sectors=32):
    vertices = []
    indices = []

    for r in range(rings + 1):
        lat = math.pi * (r / rings - 0.5)
        v = r / rings
        for s in range(sectors + 1):
            lon = 2 * math.pi * (s / sectors)
            u = s / sectors

            nx = math.cos(lat) * math.cos(lon)
            ny = math.sin(lat)
            nz = math.cos(lat) * math.sin(lon)

            vertices.extend([nx * radius, ny * radius, nz * radius, u, v, nx, ny, nz])

    for r in range(rings):
        for s in range(sectors):
            first = r * (sectors + 1) + s
            second = first + sectors + 1
            indices.extend([first, second, first + 1, second, second + 1, first + 1])

    return (
        np.array(vertices, dtype='f4').tobytes(),
        np.array(indices, dtype='u4').tobytes(),
        len(indices)
    )


def generate_ring_disc(inner_radius=1.3, outer_radius=2.6, sectors=180):
    """Generates smooth realistic ring geometry with concentric UV mapping for texture banding."""
    vertices = []
    indices = []
    for s in range(sectors + 1):
        angle = 2.0 * math.pi * (s / sectors)
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        u = s / sectors

        vertices.extend([cos_a * inner_radius, 0.0, sin_a * inner_radius, u, 0.0, 0.0, 1.0, 0.0])
        vertices.extend([cos_a * outer_radius, 0.0, sin_a * outer_radius, u, 1.0, 0.0, 1.0, 0.0])

    for s in range(sectors):
        inner_idx = s * 2
        outer_idx = inner_idx + 1
        indices.extend([inner_idx, outer_idx, inner_idx + 2, outer_idx, outer_idx + 3, inner_idx + 2])

    return (
        np.array(vertices, dtype='f4').tobytes(),
        np.array(indices, dtype='u4').tobytes(),
        len(indices)
    )


def generate_orbit_line(semi_major_axis: float, eccentricity: float = 0.0, segments: int = 512):
    vertices = []
    b = semi_major_axis * math.sqrt(max(0.0001, 1.0 - eccentricity**2))
    c = semi_major_axis * eccentricity

    for s in range(segments):
        theta = 2.0 * math.pi * (s / segments)
        x = semi_major_axis * math.cos(theta) - c
        z = b * math.sin(theta)
        vertices.extend([x, 0.0, z, 0.0, 0.0, 0.0, 1.0, 0.0])

    return np.array(vertices, dtype='f4').tobytes(), segments


def generate_asteroid_belt(count=2000, inner_r=19.2, outer_r=21.4):
    vertices = []
    np.random.seed(42)
    for _ in range(count):
        r = np.random.uniform(inner_r, outer_r)
        angle = np.random.uniform(0, 2 * math.pi)
        y_offset = np.random.uniform(-0.5, 0.5)

        x = math.cos(angle) * r
        z = math.sin(angle) * r
        vertices.extend([x, y_offset, z, 0.0, 0.0, 0.0, 1.0, 0.0])

    return np.array(vertices, dtype='f4').tobytes(), count


def generate_starfield(count=25000, radius=380.0):
    """Generates a dense array of white background star positions."""
    vertices = []
    np.random.seed(101)
    for _ in range(count):
        theta = np.random.uniform(0, 2 * math.pi)
        phi = np.random.uniform(-math.pi / 2, math.pi / 2)

        x = radius * math.cos(phi) * math.cos(theta)
        y = radius * math.sin(phi)
        z = radius * math.cos(phi) * math.sin(theta)
        vertices.extend([x, y, z, 0.0, 0.0, 0.0, 1.0, 0.0])

    return np.array(vertices, dtype='f4').tobytes(), count


def generate_quad():
    vertices = [
        -1.0, -1.0, 0.0,  0.0, 0.0,  0.0, 0.0, 1.0,
         1.0, -1.0, 0.0,  1.0, 0.0,  0.0, 0.0, 1.0,
         1.0,  1.0, 0.0,  1.0, 1.0,  0.0, 0.0, 1.0,
        -1.0,  1.0, 0.0,  0.0, 1.0,  0.0, 0.0, 1.0,
    ]
    indices = [0, 1, 2, 0, 2, 3]

    return (
        np.array(vertices, dtype='f4').tobytes(),
        np.array(indices, dtype='u4').tobytes(),
        len(indices)
    )