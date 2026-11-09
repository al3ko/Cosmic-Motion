import sys
import pygame
import moderngl
import glm

from imgui_bundle import imgui
from imgui_bundle.python_backends.pygame_backend import PygameRenderer

from src.geometry import (
    generate_uv_sphere,
    generate_ring_disc,
    generate_orbit_line,
    generate_asteroid_belt,
    generate_starfield,
    generate_quad
)
from src.texture import load_texture, generate_ring_texture
from src.camera import OrbitCamera
from src.planet import CelestialBody
from src.raycast import get_mouse_ray, ray_sphere_intersection
from src.planet_info import CELESTIAL_FACTS


def setup_modern_imgui_theme():
    """Configures modern luxury NOVA slate glassmorphic theme."""
    style = imgui.get_style()

    style.window_rounding = 14.0
    style.child_rounding = 10.0
    style.frame_rounding = 16.0       # Capsule pill controls
    style.popup_rounding = 10.0
    style.grab_rounding = 12.0
    style.scrollbar_rounding = 8.0

    style.window_border_size = 1.0
    style.frame_border_size = 1.0
    style.child_border_size = 1.0

    style.window_padding = (16.0, 14.0)
    style.frame_padding = (10.0, 6.0)
    style.item_spacing = (10.0, 8.0)

    def set_color(col_idx, color_tuple):
        style.set_color_(col_idx, imgui.ImVec4(*color_tuple))

    # Dark Obsidian Slate & Holographic Cyan/Green Accents
    set_color(imgui.Col_.window_bg, (0.05, 0.06, 0.09, 0.88))
    set_color(imgui.Col_.child_bg, (0.07, 0.09, 0.13, 0.70))
    set_color(imgui.Col_.popup_bg, (0.04, 0.05, 0.08, 0.94))
    set_color(imgui.Col_.border, (0.00, 0.78, 1.00, 0.35))
    set_color(imgui.Col_.title_bg, (0.06, 0.07, 0.10, 0.90))
    set_color(imgui.Col_.title_bg_active, (0.00, 0.50, 0.80, 0.90))

    set_color(imgui.Col_.frame_bg, (0.10, 0.12, 0.18, 0.60))
    set_color(imgui.Col_.frame_bg_hovered, (0.15, 0.22, 0.35, 0.80))
    set_color(imgui.Col_.frame_bg_active, (0.00, 0.60, 0.90, 0.85))

    set_color(imgui.Col_.button, (0.00, 0.45, 0.70, 0.50))
    set_color(imgui.Col_.button_hovered, (0.00, 0.70, 1.00, 0.80))
    set_color(imgui.Col_.button_active, (0.00, 0.85, 1.00, 1.00))

    set_color(imgui.Col_.header, (0.12, 0.18, 0.28, 0.55))
    set_color(imgui.Col_.header_hovered, (0.20, 0.30, 0.45, 0.75))
    set_color(imgui.Col_.header_active, (0.00, 0.60, 0.90, 0.85))

    set_color(imgui.Col_.slider_grab, (0.00, 0.78, 1.00, 0.90))
    set_color(imgui.Col_.slider_grab_active, (0.20, 0.85, 0.55, 1.00))
    set_color(imgui.Col_.check_mark, (0.20, 0.85, 0.55, 1.00))

    set_color(imgui.Col_.text, (0.95, 0.96, 0.98, 1.00))
    set_color(imgui.Col_.text_disabled, (0.50, 0.55, 0.65, 1.00))
    set_color(imgui.Col_.separator, (0.00, 0.78, 1.00, 0.20))


class CosmicMotionApp:
    def __init__(self):
        pygame.init()
        self.width, self.height = 1280, 720

        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
        pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption("Cosmic Motion - 3D Solar System (BICS Project)")

        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.BLEND)
        self.ctx.enable(moderngl.PROGRAM_POINT_SIZE) # Bright star point scaling

        imgui.create_context()
        setup_modern_imgui_theme()

        io = imgui.get_io()
        io.display_size = (self.width, self.height)
        self.imgui_renderer = PygameRenderer()

        # Shaders
        with open("shaders/vertex.glsl", "r") as f:
            vert_code = f.read()
        with open("shaders/fragment.glsl", "r") as f:
            frag_code = f.read()
        self.prog = self.ctx.program(vertex_shader=vert_code, fragment_shader=frag_code)

        with open("shaders/halo_vertex.glsl", "r") as f:
            h_vert = f.read()
        with open("shaders/halo_fragment.glsl", "r") as f:
            h_frag = f.read()
        self.halo_prog = self.ctx.program(vertex_shader=h_vert, fragment_shader=h_frag)

        # Geometry VAOs
        sphere_vbo, sphere_ibo, self.sphere_indices = generate_uv_sphere(radius=1.0)
        self.sphere_vao = self.ctx.vertex_array(
            self.prog,
            [(self.ctx.buffer(sphere_vbo), '3f 2f 3f', 'in_position', 'in_texcoord', 'in_normal')],
            index_buffer=self.ctx.buffer(sphere_ibo)
        )

        ring_vbo, ring_ibo, self.ring_indices = generate_ring_disc(inner_radius=1.3, outer_radius=2.6)
        self.ring_vao = self.ctx.vertex_array(
            self.prog,
            [(self.ctx.buffer(ring_vbo), '3f 2f 3f', 'in_position', 'in_texcoord', 'in_normal')],
            index_buffer=self.ctx.buffer(ring_ibo)
        )

        quad_vbo, quad_ibo, _ = generate_quad()
        self.quad_vao = self.ctx.vertex_array(
            self.halo_prog,
            [(self.ctx.buffer(quad_vbo), '3f 2f 12x', 'in_position', 'in_texcoord')],
            index_buffer=self.ctx.buffer(quad_ibo)
        )

        # Camera
        self.camera = OrbitCamera(target=glm.vec3(0.0), distance=65.0, yaw=0.0, pitch=25.0)

        # Celestial Entities
        self.sun = CelestialBody("Sun", radius=3.5, orbit_radius=0.0, orbit_speed=0.0, spin_speed=0.2, is_sun=True)
        self.planets = [
            CelestialBody("Mercury", 0.4, 6.0,  1.6,  0.5, axial_tilt=0.03,  eccentricity=0.205),
            CelestialBody("Venus",   0.7, 9.0,  1.2, -0.3, axial_tilt=177.3, eccentricity=0.007),
            CelestialBody("Earth",   0.8, 13.0, 1.0,  2.0, axial_tilt=23.44, eccentricity=0.017),
            CelestialBody("Mars",    0.5, 17.0, 0.8,  1.8, axial_tilt=25.19, eccentricity=0.094),
            CelestialBody("Jupiter", 1.8, 23.0, 0.4,  4.0, axial_tilt=3.13,  eccentricity=0.049),
            CelestialBody("Saturn",  1.5, 30.0, 0.3,  3.5, axial_tilt=26.73, eccentricity=0.057),
            CelestialBody("Uranus",  1.1, 37.0, 0.2, -2.5, axial_tilt=97.77, eccentricity=0.046),
            CelestialBody("Neptune", 1.0, 44.0, 0.1,  2.2, axial_tilt=28.32, eccentricity=0.011),
        ]

        # Moons
        earth, jupiter, saturn = self.planets[2], self.planets[4], self.planets[5]
        self.moons = [
            CelestialBody("Moon",     0.22, 1.8, 3.5, 1.0, 6.68, parent=earth),
            CelestialBody("Io",       0.12, 2.4, 5.0, 1.0, 0.0, parent=jupiter),
            CelestialBody("Europa",   0.11, 3.0, 4.0, 1.0, 0.0, parent=jupiter),
            CelestialBody("Ganymede", 0.18, 3.8, 3.0, 1.0, 0.0, parent=jupiter),
            CelestialBody("Callisto", 0.16, 4.6, 2.2, 1.0, 0.0, parent=jupiter),
            CelestialBody("Titan",    0.17, 3.2, 2.8, 1.0, 0.3, parent=saturn),
        ]

        # Textures
        self.sun.texture = load_texture(self.ctx, "assets/textures/sun.jpg", "sun")
        for planet in self.planets:
            planet.texture = load_texture(self.ctx, f"assets/textures/{planet.name.lower()}.jpg", planet.name)
        for moon in self.moons:
            moon.texture = load_texture(self.ctx, f"assets/textures/{moon.name.lower()}.jpg", moon.name)

        # Realistic Ring Textures
        self.ring_textures = {
            "Saturn": generate_ring_texture(self.ctx, "Saturn"),
            "Uranus": generate_ring_texture(self.ctx, "Uranus"),
            "Neptune": generate_ring_texture(self.ctx, "Neptune")
        }

        # Background Objects
        ast_data, self.asteroid_count = generate_asteroid_belt(count=2000, inner_r=19.2, outer_r=21.4)
        self.asteroid_vao = self.ctx.vertex_array(
            self.prog,
            [(self.ctx.buffer(ast_data), '3f 2f 3f', 'in_position', 'in_texcoord', 'in_normal')]
        )

        star_data, self.star_count = generate_starfield(count=25000, radius=380.0)
        self.starfield_vao = self.ctx.vertex_array(
            self.prog,
            [(self.ctx.buffer(star_data), '3f 2f 3f', 'in_position', 'in_texcoord', 'in_normal')]
        )

        # Application Controls
        self.clock = pygame.time.Clock()
        self.sim_time = 0.0
        self.speed_multiplier = 1.0
        self.is_paused = False
        self.is_reversed = False
        self.use_true_scale = False
        self.wireframe_mode = False
        self.show_labels = True

        self.selected_body = None
        self.show_info_card = False
        self.clicked_body = None

        self.rebuild_orbit_lines()

    def rebuild_orbit_lines(self):
        self.orbit_vaos = []
        mult = 3.5 if self.use_true_scale else 1.0
        for planet in self.planets:
            line_data, count = generate_orbit_line(planet.orbit_radius * mult, planet.eccentricity, segments=512)
            vao = self.ctx.vertex_array(
                self.prog,
                [(self.ctx.buffer(line_data), '3f 2f 3f', 'in_position', 'in_texcoord', 'in_normal')]
            )
            self.orbit_vaos.append((vao, count))

    def world_to_screen(self, world_pos: glm.vec3) -> tuple:
        view = self.camera.get_view_matrix()
        proj = self.camera.get_projection_matrix(self.width, self.height)
        clip_space = proj * view * glm.vec4(world_pos, 1.0)

        if clip_space.w <= 0.0:
            return None

        ndc = glm.vec3(clip_space) / clip_space.w
        screen_x = int((ndc.x + 1.0) * 0.5 * self.width)
        screen_y = int((1.0 - ndc.y) * 0.5 * self.height)

        return (screen_x, screen_y)

    def handle_raycast_selection(self, mouse_pos):
        view = self.camera.get_view_matrix()
        proj = self.camera.get_projection_matrix(self.width, self.height)
        ray_origin, ray_dir = get_mouse_ray(mouse_pos, self.width, self.height, view, proj)

        closest_t = 1e9
        picked_body = None

        all_bodies = [self.sun] + self.planets + self.moons
        for body in all_bodies:
            hit_t = ray_sphere_intersection(ray_origin, ray_dir, body.position, body.radius * 1.5)
            if hit_t > 0.0 and hit_t < closest_t:
                closest_t = hit_t
                picked_body = body

        if picked_body:
            self.selected_body = picked_body
            self.clicked_body = picked_body
            self.show_info_card = True
            self.camera.focus_body(picked_body.position, picked_body.radius)
        else:
            self.selected_body = None
            self.show_info_card = False

    def draw_halo(self, position: glm.vec3, radius: float, color: tuple):
        view = self.camera.get_view_matrix()
        proj = self.camera.get_projection_matrix(self.width, self.height)

        cam_right = glm.vec3(view[0][0], view[1][0], view[2][0])
        cam_up = glm.vec3(view[0][1], view[1][1], view[2][1])

        scale = radius * 2.8
        model = glm.mat4(
            glm.vec4(cam_right * scale, 0.0),
            glm.vec4(cam_up * scale, 0.0),
            glm.vec4(0.0, 0.0, 1.0, 0.0),
            glm.vec4(position, 1.0)
        )

        self.halo_prog['model'].write(model)
        self.halo_prog['view'].write(view)
        self.halo_prog['projection'].write(proj)
        self.halo_prog['u_halo_color'].value = color

        self.quad_vao.render()

    def draw_body(self, body: CelestialBody):
        model = body.get_model_matrix(self.sim_time, self.use_true_scale)
        self.prog['model'].write(model)
        self.prog['u_is_sun'].value = body.is_sun
        self.prog['u_is_orbit'].value = False

        if body.texture:
            body.texture.use(location=0)
        self.sphere_vao.render()

    def render_gui(self):
        io = imgui.get_io()

        # -------------------------------------------------------------
        # 1. PROMINENT CENTERED HEADER (COSMOTION TITLE & STATUS)
        # -------------------------------------------------------------
        header_width = 340
        header_height = 84
        imgui.set_next_window_pos((self.width * 0.5 - header_width * 0.5, 15), imgui.Cond_.always)
        imgui.set_next_window_size((header_width, header_height), imgui.Cond_.always)
        imgui.begin(
            "##CenteredTopHeader",
            None,
            imgui.WindowFlags_.no_title_bar
            | imgui.WindowFlags_.no_resize
            | imgui.WindowFlags_.no_move
            | imgui.WindowFlags_.no_scrollbar
        )

        # Embedded dark title banner box with metallic border
        draw_l = imgui.get_window_draw_list()
        win_pos = imgui.get_window_pos()
        draw_l.add_rect_filled(
            (win_pos.x + 8, win_pos.y + 6),
            (win_pos.x + header_width - 8, win_pos.y + 40),
            imgui.get_color_u32((0.08, 0.10, 0.15, 0.95)),
            8.0
        )
        draw_l.add_rect(
            (win_pos.x + 8, win_pos.y + 6),
            (win_pos.x + header_width - 8, win_pos.y + 40),
            imgui.get_color_u32((0.00, 0.78, 1.00, 0.40)),
            8.0,
            thickness=1.0
        )

        # Centered COSMOTION Title
        title_text = "C O S M O T I O N"
        text_size = imgui.calc_text_size(title_text)
        imgui.set_cursor_pos(((header_width - text_size.x) * 0.5, 14))
        imgui.text_colored((0.95, 0.96, 0.98, 1.0), title_text)

        # Status & Controls Row
        imgui.set_cursor_pos((18, 48))
        
        status_color = (0.20, 0.85, 0.55, 1.0) if not self.is_paused else (0.95, 0.30, 0.30, 1.0)
        status_text = "ONLINE" if not self.is_paused else "OFFLINE"

        cur_pos = imgui.get_cursor_screen_pos()
        draw_l.add_circle_filled((cur_pos.x + 4, cur_pos.y + 7), 3.5, imgui.get_color_u32(status_color))
        imgui.dummy((10, 0))
        imgui.same_line()
        imgui.text_colored(status_color, status_text)

        imgui.same_line(175)
        pause_label = "PLAY" if self.is_paused else "PAUSE"
        if imgui.button(pause_label, (65, 24)):
            self.is_paused = not self.is_paused

        imgui.same_line(250)
        if imgui.button("RESET", (65, 24)):
            self.selected_body = None
            self.show_info_card = False
            self.camera.set_target(glm.vec3(0.0))

        imgui.end()

        # -------------------------------------------------------------
        # 2. TOP-LEFT CONTROL PANEL (Speed ratio range 0.0x to 5.0x)
        # -------------------------------------------------------------
        imgui.set_next_window_pos((20, 20), imgui.Cond_.always)
        imgui.set_next_window_size((310, 245), imgui.Cond_.always)
        imgui.begin("CONTROL PANEL", None, imgui.WindowFlags_.no_move | imgui.WindowFlags_.no_resize)

        imgui.text_disabled("TARGET NAVIGATION FOCUS:")
        imgui.push_item_width(-1)
        current_name = self.selected_body.name if self.selected_body else "Free Camera (Unlocked)"
        if imgui.begin_combo("##DirectTargetCombo", current_name):
            if imgui.selectable("🌐 Free Camera (Unlocked)", self.selected_body is None)[0]:
                self.selected_body = None
                self.show_info_card = False

            all_bodies = [self.sun] + self.planets + self.moons
            for body in all_bodies:
                is_selected = (self.selected_body == body)
                if imgui.selectable(f"  {body.name}", is_selected)[0]:
                    self.selected_body = body
                    self.clicked_body = body
                    self.show_info_card = True
                    self.camera.focus_body(body.position, body.radius)
                if is_selected:
                    imgui.set_item_default_focus()
            imgui.end_combo()
        imgui.pop_item_width()

        imgui.spacing()
        imgui.separator()
        imgui.spacing()

        # Speed Ratio Slider bounded between 0.0x and 5.0x
        _, self.speed_multiplier = imgui.slider_float("Speed", self.speed_multiplier, 0.0, 5.0, "%.1fx")
        imgui.spacing()

        changed_scale, self.use_true_scale = imgui.checkbox("True Astronomical Scale", self.use_true_scale)
        if changed_scale:
            self.rebuild_orbit_lines()

        imgui.same_line()
        _, self.wireframe_mode = imgui.checkbox("Wireframe [W]", self.wireframe_mode)

        _, self.show_labels = imgui.checkbox("Callout Badges", self.show_labels)

        imgui.end()

        # -------------------------------------------------------------
        # 3. BOTTOM-RIGHT TELEMETRY BAR
        # -------------------------------------------------------------
        imgui.set_next_window_pos((self.width - 660, self.height - 45), imgui.Cond_.always)
        imgui.set_next_window_size((645, 35), imgui.Cond_.always)
        imgui.begin(
            "##TelemetryOverlay",
            None,
            imgui.WindowFlags_.no_title_bar
            | imgui.WindowFlags_.no_resize
            | imgui.WindowFlags_.no_move
            | imgui.WindowFlags_.no_scrollbar
        )

        if self.selected_body:
            pos = self.selected_body.position
            imgui.text_colored((0.0, 0.78, 1.0, 1.0), f"TARGET: {self.selected_body.name.upper()}")
            imgui.same_line(110)
            imgui.text_disabled("|")
            imgui.same_line(125)
            imgui.text(f"R: {self.selected_body.orbit_radius:.2f} AU")
            imgui.same_line(210)
            imgui.text_disabled("|")
            imgui.same_line(225)
            imgui.text(f"V: {self.selected_body.orbit_speed * 29.78:.1f} km/s")
            imgui.same_line(320)
            imgui.text_disabled("|")
            imgui.same_line(335)
            imgui.text(f"Tilt: {self.selected_body.axial_tilt:.2f}°")
            imgui.same_line(420)
            imgui.text_disabled("|")
            imgui.same_line(435)
            imgui.text_colored((0.70, 0.85, 1.0, 0.90), f"POS: ({pos.x:+.1f}, {pos.y:+.1f}, {pos.z:+.1f})")
        else:
            imgui.text_colored((0.95, 0.96, 0.98, 0.8), "SYSTEM NAVIGATION: FREE CAMERA MODE (NO ACTIVE TARGET LOCK)")

        imgui.end()

        # -------------------------------------------------------------
        # 4. SPLIT-VIEW EDUCATIONAL CATALOG POPUP
        # -------------------------------------------------------------
        if self.show_info_card and self.clicked_body:
            body_name = self.clicked_body.name
            screen_pos = self.world_to_screen(self.clicked_body.position)

            if screen_pos:
                px = min(self.width - 660, max(20, screen_pos[0] + 35))
                py = min(self.height - 350, max(20, screen_pos[1] - 140))
                imgui.set_next_window_pos((px, py), imgui.Cond_.always)

            imgui.set_next_window_size((640, 290), imgui.Cond_.always)
            opened, self.show_info_card = imgui.begin(
                f"ASTRONOMICAL CATALOG // {body_name.upper()}###InfoCard",
                True,
                imgui.WindowFlags_.no_collapse | imgui.WindowFlags_.no_resize
            )

            info = CELESTIAL_FACTS.get(body_name, {
                "type": "Celestial Body",
                "diameter": "Unknown",
                "mass": "N/A",
                "temp": "N/A",
                "moons": "N/A",
                "atmos": "N/A",
                "fact": "Orbiting inside the Solar System."
            })

            imgui.columns(2, "split", True)
            imgui.set_column_width(0, 240)

            imgui.text_disabled("CLASSIFICATION:")
            imgui.text_colored((0.20, 0.85, 0.55, 1.0), info['type'])
            imgui.spacing()

            imgui.text_disabled("EQUATORIAL DIA:")
            imgui.text(info['diameter'])
            imgui.spacing()

            imgui.text_disabled("TOTAL MASS:")
            imgui.text(info['mass'])
            imgui.spacing()

            imgui.text_disabled("SURFACE TEMP:")
            imgui.text(info['temp'])
            imgui.spacing()

            imgui.text_disabled("KNOWN MOONS:")
            imgui.text(info['moons'])
            imgui.spacing()

            imgui.text_disabled("ATMOSPHERE:")
            imgui.text_wrapped(info['atmos'])

            imgui.next_column()

            imgui.text_disabled("ASTRONOMICAL PROFILE & FACTS")
            imgui.separator()
            imgui.spacing()
            imgui.text_wrapped(info['fact'])

            imgui.columns(1)
            imgui.end()

        # -------------------------------------------------------------
        # 5. RETICLE TARGETING & BRAND CALLOUT TAGS
        # -------------------------------------------------------------
        if self.show_labels:
            draw_list = imgui.get_foreground_draw_list()
            all_bodies = [self.sun] + self.planets
            for body in all_bodies:
                screen_pos = self.world_to_screen(body.position)
                if screen_pos:
                    x, y = screen_pos
                    draw_list.add_circle_filled((x, y), 3.0, imgui.get_color_u32((1.0, 1.0, 1.0, 0.9)))
                    draw_list.add_circle((x, y), 6.5, imgui.get_color_u32((0.0, 0.78, 1.0, 0.5)), num_segments=16, thickness=1.2)
                    
                    label_str = body.name.upper()
                    draw_list.add_rect_filled((x + 12, y - 8), (x + 18 + len(label_str) * 7, y + 8), imgui.get_color_u32((0.05, 0.06, 0.09, 0.80)), 6.0)
                    draw_list.add_rect((x + 12, y - 8), (x + 18 + len(label_str) * 7, y + 8), imgui.get_color_u32((0.00, 0.78, 1.0, 0.35)), 6.0, thickness=1.0)
                    draw_list.add_text((x + 15, y - 6), imgui.get_color_u32((0.95, 0.96, 0.98, 0.95)), label_str)

        return io.want_capture_mouse

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0

            io = imgui.get_io()
            io.display_size = (self.width, self.height)

            for event in pygame.event.get():
                if hasattr(self.imgui_renderer, "process_event"):
                    self.imgui_renderer.process_event(event)

                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                    self.wireframe_mode = not self.wireframe_mode
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not io.want_capture_mouse:
                        self.handle_raycast_selection(event.pos)

                self.camera.handle_event(event, io.want_capture_mouse)

            imgui.new_frame()
            self.render_gui()

            time_dir = -1.0 if self.is_reversed else 1.0
            if not self.is_paused:
                self.sim_time += dt * self.speed_multiplier * time_dir

            if self.selected_body:
                self.camera.set_target(self.selected_body.position)

            self.camera.update(dt)

            self.ctx.clear(0.02, 0.02, 0.05)
            self.ctx.wireframe = self.wireframe_mode

            view = self.camera.get_view_matrix()
            proj = self.camera.get_projection_matrix(self.width, self.height)
            self.prog['view'].write(view)
            self.prog['projection'].write(proj)
            self.prog['u_light_pos'].value = (0.0, 0.0, 0.0)
            self.prog['u_view_pos'].value = tuple(self.camera.position)

            # 1. Starfield Skybox (25,000 Dense White Stars)
            self.prog['model'].write(glm.mat4(1.0))
            self.prog['u_is_sun'].value = False
            self.prog['u_is_orbit'].value = False

            if 'u_is_star' in self.prog:
                self.prog['u_is_star'].value = True

            self.starfield_vao.render(mode=moderngl.POINTS)

            if 'u_is_star' in self.prog:
                self.prog['u_is_star'].value = False

            # 2. Crisp Orbit Lines
            self.prog['u_is_sun'].value = False
            self.prog['u_is_orbit'].value = True
            for vao, count in self.orbit_vaos:
                vao.render(mode=moderngl.LINE_LOOP, vertices=count)

            # 3. Asteroid Belt
            self.prog['u_is_sun'].value = False
            self.prog['u_is_orbit'].value = False
            self.asteroid_vao.render(mode=moderngl.POINTS, vertices=self.asteroid_count)

            # 4. Sun & Planets
            self.draw_body(self.sun)
            for planet in self.planets:
                self.draw_body(planet)

            # 5. Moons
            for moon in self.moons:
                self.draw_body(moon)

            # 6. Realistic Alpha Ring Rendering
            for p_idx in [5, 6, 7]:
                planet = self.planets[p_idx]
                self.prog['model'].write(planet.get_model_matrix(self.sim_time, self.use_true_scale))
                self.prog['u_is_sun'].value = False
                self.prog['u_is_orbit'].value = False
                
                ring_tex = self.ring_textures.get(planet.name)
                if ring_tex:
                    ring_tex.use(location=0)
                self.ring_vao.render()

            # 7. Atmospheric Glowing Halos
            if not self.wireframe_mode:
                self.draw_halo(self.sun.position, self.sun.radius, (1.0, 0.75, 0.2))
                self.draw_halo(self.planets[2].position, self.planets[2].radius, (0.3, 0.6, 1.0))

            self.ctx.wireframe = False
            imgui.render()
            self.imgui_renderer.render(imgui.get_draw_data())

            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = CosmicMotionApp()
    app.run()