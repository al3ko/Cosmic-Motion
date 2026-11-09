import math
import glm
import moderngl


class CelestialBody:
    def __init__(
        self,
        name: str,
        radius: float,
        orbit_radius: float,
        orbit_speed: float,
        spin_speed: float,
        axial_tilt: float = 0.0,
        eccentricity: float = 0.0,
        parent=None,
        is_sun: bool = False
    ):
        self.name = name
        self.radius = radius
        self.orbit_radius = orbit_radius  # Semi-major axis (a)
        self.orbit_speed = orbit_speed
        self.spin_speed = spin_speed
        self.axial_tilt = axial_tilt
        self.eccentricity = eccentricity
        self.parent = parent
        self.is_sun = is_sun

        self.texture: moderngl.Texture = None
        self.position = glm.vec3(0.0)

    def get_model_matrix(self, time: float, use_true_scale: bool = False) -> glm.mat4:
        model = glm.mat4(1.0)

        # 1. Handle Parent Offset (Moons)
        if self.parent:
            parent_matrix = self.parent.get_model_matrix(time, use_true_scale)
            parent_pos = glm.vec3(parent_matrix[3])

            moon_angle = time * self.orbit_speed
            rel_x = math.cos(moon_angle) * self.orbit_radius
            rel_z = math.sin(moon_angle) * self.orbit_radius

            model = glm.translate(glm.mat4(1.0), parent_pos + glm.vec3(rel_x, 0.0, rel_z))
            self.position = glm.vec3(model[3])

            model = glm.rotate(model, time * self.spin_speed, glm.vec3(0.0, 1.0, 0.0))
            return glm.scale(model, glm.vec3(self.radius))

        # 2. Keplerian Elliptical Orbit for Planets
        if self.orbit_radius > 0.0:
            scale_mult = 3.5 if use_true_scale else 1.0
            a = self.orbit_radius * scale_mult
            e = self.eccentricity
            b = a * math.sqrt(max(0.0001, 1.0 - e**2))
            c = a * e

            # Mean anomaly / Orbital angle
            angle = time * self.orbit_speed
            # Elliptical coordinates relative to focal origin
            x = a * math.cos(angle) - c
            z = b * math.sin(angle)

            model = glm.translate(model, glm.vec3(x, 0.0, z))

        self.position = glm.vec3(model[3])

        if self.is_sun:
            return glm.scale(model, glm.vec3(self.radius))

        # 3. Axial Tilt & Rotation
        if self.axial_tilt != 0.0:
            model = glm.rotate(model, glm.radians(self.axial_tilt), glm.vec3(0.0, 0.0, 1.0))

        model = glm.rotate(model, time * self.spin_speed, glm.vec3(0.0, 1.0, 0.0))
        model = glm.scale(model, glm.vec3(self.radius))

        return model