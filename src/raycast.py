import glm


def get_mouse_ray(mouse_pos, width: int, height: int, view: glm.mat4, projection: glm.mat4) -> tuple:
    """Converts 2D screen coordinates into a 3D ray origin and direction vector."""
    x = (2.0 * mouse_pos[0]) / width - 1.0
    y = 1.0 - (2.0 * mouse_pos[1]) / height

    # Screen coordinates -> Normalized Device Coordinates (NDC)
    ray_clip = glm.vec4(x, y, -1.0, 1.0)

    # Eye space ray
    inv_proj = glm.inverse(projection)
    ray_eye = inv_proj * ray_clip
    ray_eye = glm.vec4(ray_eye.x, ray_eye.y, -1.0, 0.0)

    # World space ray direction
    inv_view = glm.inverse(view)
    ray_world = glm.vec3(inv_view * ray_eye)
    ray_dir = glm.normalize(ray_world)

    # Ray origin is camera position (extracted from inverted view matrix)
    ray_origin = glm.vec3(inv_view[3])

    return ray_origin, ray_dir


def ray_sphere_intersection(ray_origin: glm.vec3, ray_dir: glm.vec3, sphere_center: glm.vec3, radius: float) -> float:
    """Returns distance t along ray if intersection occurs with sphere, else returns -1.0."""
    oc = ray_origin - sphere_center
    b = glm.dot(oc, ray_dir)
    c = glm.dot(oc, oc) - (radius * radius)
    discriminant = b * b - c

    if discriminant < 0.0:
        return -1.0

    t = -b - glm.sqrt(discriminant)
    return t if t > 0.0 else -1.0