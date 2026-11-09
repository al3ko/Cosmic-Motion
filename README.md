# 🌌 COSMOTION: 3D Interactive Solar System Simulator

**Cosmotion** is a high-performance, real-time 3D Solar System simulator and space navigation interface.

Originally prototyped as a C++ software-rasterized ray tracer/exporter, the application has evolved into a hardware-accelerated, interactive 3D platform built with **Python 3.12**, **ModernGL (OpenGL 3.3+)**, **Pygame 2.6**, and **Dear ImGui (`imgui_bundle`)**. It features dynamic camera focus controls, realistic ring rendering with transparency gaps, procedural starfield skyboxes, screen-space target callouts, and an educational catalog popup system tailored in a futuristic **NOVA slate glassmorphic HUD** style.

---

## 👥 Team Members & Project Roles

* **Alex Murimi Ngigi (162437)** — *Lead Core Engine & UI/UX Developer*
  * Designed the real-time graphics pipeline, ModernGL shader integration, camera controllers, 3D raycast picking algorithms, and the NOVA ImGui HUD design architecture.
* **Timothy Muigai (150320)** — *Graphics & Shading Specialist*
  * Designed shader programs, point lighting, specular reflection models, atmospheric glowing halos, and emissive star material textures.
* **Dennis Kyalo (158270)** — *Rasterization & Trajectory Engineer*
  * Developed mathematical parametric orbit equations, true astronomical scaling math, and procedural coordinate transformation helpers.
* **Joseph Manene Kamau (169648)** — *3D Geometry & Mesh Developer*
  * Engineered sphere mesh generation (UV sphere algorithms), concentric disc geometry for planetary rings, and asteroid belt point distributions.
* **Larry Seme (169002)** — *Software Testing & Educational Content Specialist*
  * Authored the educational planetary data catalog (`CELESTIAL_FACTS`), benchmarked frame timings, and handled multi-platform compatibility validation.

---

## 🛠️ Computer Graphics Techniques Implemented

* **Phong Reflection Shading Model**: Combines ambient, diffuse, and specular components computed in world-space fragment shaders to simulate dynamic sunlight falloff across spherical surfaces[cite: 8].
* **Hierarchical Matrix Stack Transformations**: Implements parent-child transformation chains ($\text{World} = \mathbf{M}_{\text{parent}} \times \mathbf{M}_{\text{orbit}} \times \mathbf{M}_{\text{spin}}$) to enable nested satellite motion (e.g., Moon orbiting Earth while Earth orbits the Sun)[cite: 8].
* **3D Screen-Space Raycasting**: Converts 2D mouse cursor coordinates into a 3D world-space ray vector using inverse projection and view matrices ($\mathbf{d} = (\mathbf{P} \cdot \mathbf{V})^{-1} \cdot \mathbf{v}_{\text{ndc}}$) to test for ray-sphere intersections[cite: 8].
* **Procedural Alpha-Bended Ring Texturing**: Generates concentric UV-mapped planar discs for Saturn, Uranus, and Neptune using procedural band variance with Cassini and Encke opacity divisions[cite: 8].
* **Camera-Facing Billboard Rendering**: Renders atmospheric halos on 2D quads that automatically rotate to align with the camera's right and up vectors, avoiding heavy volumetric scattering math[cite: 8].
* **Point-Sized Emissive Rendering**: Utilizes `GL_PROGRAM_POINT_SIZE` and OpenGL primitive points to draw thousands of background stars efficiently.

---

## 📋 Implementation of In-Scope Document Features

All planned features outlined in the project development scope have been fully realized[cite: 8]:

* **Core Primitives & Lighting**: Custom parametric UV sphere mesh generation, texture binding, dark space skybox, and Sun-centered point lighting[cite: 8].
* **Nested Kinematic Matrix Architecture**: Hierarchical rotation/revolution system for nested planetary and lunar orbits[cite: 8].
* **Expanded Moons & Rings**: Major Galilean moons (Io, Europa, Ganymede, Callisto), Titan, and Earth's Moon, plus alpha-blended procedural rings for Saturn, Uranus, and Neptune[cite: 8].
* **Astronomical Distance Toggle**: Live UI switch toggling between visual compressed space and True Astronomical Scale ratios ($3.5\times$ distance scaling)[cite: 8].
* **Interactive 3D Raycasting**: Click-to-select camera target locking on any celestial body[cite: 8].
* **Smooth Camera Interpolation**: Smooth GLM vector lerping and focus transitions when targeting bodies[cite: 8].
* **HUD Controls & Performance Options**: Time controls (`PLAY`, `PAUSE`, `RESET`), speed ratio sliders ($0.0\times$ to $5.0\times$), callout badges, and a toggleable Wireframe render mode (`[W]`)[cite: 8].

---

## ✨ Additional Implemented Features (Beyond Scope)

Beyond the initial development breakdown, the following advanced features were designed and implemented[cite: 8]:

1. **Ultra-Dense 25,000 Background Starfield**: Expanded background star generator from basic point clusters to 25,000 randomized white/blue-white emissive point stars.
2. **Futuristic NOVA HUD Design System**: Complete glassmorphic UI overlay using custom Dear ImGui themes, slate obsidian panels, glowing cyber-cyan borders (`#00C8FF`), and emerald status dots.
3. **Dynamic ONLINE / OFFLINE Status Indicator**: Embedded live status header that automatically switches from a glowing green `ONLINE` dot to a red `OFFLINE` dot when the simulation is paused.
4. **Bottom-Right Telemetry Bar**: Pinned non-intrusive HUD capsule displaying real-time astronomical telemetry (Orbital Radius $R$, Orbital Velocity $V$, Axial Tilt, and 3D position vectors).
5. **Horizontal Split-View Educational Catalog**: Interactive popup cards displaying physical statistics (mass, diameter, atmosphere composition) alongside rich geological narratives.
6. **Free-Camera Unfocus Mechanics**: Selecting "Unfocus Target" or clicking empty space seamlessly releases target locks, allowing unrestricted 3D orbit, pan, and zoom navigation around origin `(0, 0, 0)`.

---

## ⚡ Technical Challenges Faced & Solutions

* **Challenge 1: C++ Binding Mismatches in `imgui_bundle`**
  * *Issue*: Standard C++ ImGui calls like `SetWindowFontScale` or `collapsing_header` with `None` parameters raised Python `AttributeError` and `TypeError` exceptions.
  * *Solution*: Replaced dynamic font scale mutations with standard canvas draw lists (`add_rect_filled`, `add_rect`), and adapted `collapsing_header` signatures directly to PyImGui's overloaded wrappers.
* **Challenge 2: Alpha Blending & Transparency Sorting**
  * *Issue*: Semi-transparent planetary rings and atmospheric glowing halos caused depth-fighting artifacts when rendered prior to solid celestial bodies.
  * *Solution*: Structured the render pipeline into distinct passes: solid meshes $\rightarrow$ alpha-textured rings $\rightarrow$ camera-facing billboard halos $\rightarrow$ 2D ImGui HUD draw call execution.
* **Challenge 3: Background Star Visibility in ModernGL**
  * *Issue*: Untextured background star points rendered dim or invisible due to missing UV coordinates in the fragment shader.
  * *Solution*: Enabled `moderngl.PROGRAM_POINT_SIZE`, added a dedicated `u_is_star` uniform flag in `fragment.glsl`, and bypassed texture sampling to emit pure white light vectors.

---

## 🛠️ Tech Stack & Dependencies

* **Language**: Python 3.12+
* **Windowing & Input**: Pygame 2.6+ / SDL2
* **Graphics API**: ModernGL 5.12+ (OpenGL 3.3 Core Profile)
* **GUI Framework**: `imgui_bundle` (Dear ImGui C++ bindings)
* **Math Library**: `PyGLM` (OpenGL Mathematics for Python)
* **Image Processing**: Pillow (PIL)
* **Data Structures**: NumPy

---

## 📐 Project Structure

```text
graphics/
├── assets/
│   └── textures/          # High-resolution celestial body surface maps
├── shaders/
│   ├── vertex.glsl        # Core mesh transformation shader
│   ├── fragment.glsl      # Phong shading, star emission, and ring alpha shader
│   ├── halo_vertex.glsl   # Camera-facing billboard vertex shader
│   └── halo_fragment.glsl # Radial atmospheric glow shader
├── src/
│   ├── camera.py          # Orbit camera matrix controller & GLM lerping
│   ├── geometry.py        # UV spheres, ring discs, starfields, asteroid belt
│   ├── planet.py          # Celestial body matrix transformations & kinematic state
│   ├── planet_info.py     # Educational database dictionary (CELESTIAL_FACTS)
│   ├── raycast.py         # 3D Mouse ray-sphere intersection picking math
│   └── texture.py         # Procedural texture generator & alpha ring gap shaders
├── main.py                # Main application loop, render pipeline & ImGui HUD
└── README.md