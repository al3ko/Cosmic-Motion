import math
import glm
import pygame


class OrbitCamera:
    def __init__(self, target=glm.vec3(0.0), distance=65.0, yaw=0.0, pitch=25.0):
        self.target = glm.vec3(target)
        self.desired_target = glm.vec3(target)
        self.distance = distance
        self.desired_distance = distance
        self.yaw = yaw
        self.pitch = pitch

        self.min_distance = 1.5
        self.max_distance = 600.0
        self.min_pitch = -89.0
        self.max_pitch = 89.0

        self.position = glm.vec3(0.0)
        self.is_dragging = False
        self.last_mouse_pos = (0, 0)

        self.update_position()

    def set_target(self, new_target: glm.vec3):
        """Updates the tracking target position without resetting the user's zoom level."""
        self.desired_target = glm.vec3(new_target)

    def focus_body(self, new_target: glm.vec3, target_radius: float):
        """Focuses on a newly selected body and adjusts zoom only upon initial selection."""
        self.desired_target = glm.vec3(new_target)
        self.desired_distance = max(4.0, target_radius * 4.5)

    def update(self, dt: float):
        """Smoothly lerps camera position and distance every frame."""
        lerp_factor = min(1.0, dt * 8.0)
        self.target = glm.mix(self.target, self.desired_target, lerp_factor)
        self.distance = glm.mix(self.distance, self.desired_distance, lerp_factor)
        self.update_position()

    def update_position(self):
        self.pitch = max(self.min_pitch, min(self.max_pitch, self.pitch))
        self.distance = max(self.min_distance, min(self.max_distance, self.distance))

        rad_yaw = math.radians(self.yaw)
        rad_pitch = math.radians(self.pitch)

        x = self.target.x + self.distance * math.cos(rad_pitch) * math.sin(rad_yaw)
        y = self.target.y + self.distance * math.sin(rad_pitch)
        z = self.target.z + self.distance * math.cos(rad_pitch) * math.cos(rad_yaw)

        self.position = glm.vec3(x, y, z)

    def handle_event(self, event: pygame.event.Event, imgui_want_mouse: bool = False):
        if imgui_want_mouse:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.is_dragging = True
                self.last_mouse_pos = event.pos
            elif event.button == 4:  # Zoom In
                self.desired_distance = max(self.min_distance, self.desired_distance - 3.5)
            elif event.button == 5:  # Zoom Out
                self.desired_distance = min(self.max_distance, self.desired_distance + 3.5)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False

        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            dx = event.pos[0] - self.last_mouse_pos[0]
            dy = event.pos[1] - self.last_mouse_pos[1]
            self.last_mouse_pos = event.pos

            sensitivity = 0.25
            self.yaw -= dx * sensitivity
            self.pitch += dy * sensitivity
            self.update_position()

    def get_view_matrix(self) -> glm.mat4:
        return glm.lookAt(self.position, self.target, glm.vec3(0.0, 1.0, 0.0))

    def get_projection_matrix(self, width: int, height: int, fov_deg=45.0) -> glm.mat4:
        aspect_ratio = width / max(1, height)
        return glm.perspective(glm.radians(fov_deg), aspect_ratio, 0.1, 800.0)