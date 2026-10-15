Cosmic Motion

Description

Cosmic Motion is a software-rendered 3D solar system simulation written from scratch in C++. The program renders a 3D solar system scene featuring the Sun, eight planets, Earth's moon, planetary orbit rings, Saturn's ring system, a procedural starfield backdrop, and a 3D camera trajectory curve. The application runs purely through custom software rasterization and mathematics without depending on external graphics APIs or frameworks.

Team Members and Responsibilities

162437 Ngigi Alex: Lead Core Engine Developer, responsible for 3D Perspective Projection, Pipeline Design, and Z-Buffer Architecture.

150320 Muigai Timothy: Graphics and Shading Specialist, responsible for Lighting and Shading Algorithms (Lambertian Reflectance Model) and Sun/Planetary Surface Shading.

158270 Dennis Kyalo: Rasterization Engineer, responsible for Line and Curve Rasterization Algorithms (Bresenham's Line Algorithm and 3D Cubic Bézier Splines).

169648 Kamau Joseph Manene: 3D Geometry Developer, responsible for Geometric Modeling and Celestial Objects (3D Sphere Geometry, Saturn Rings, and Moon Orbit).

169002 Larry Seme: Software and Testing Engineer, responsible for Framebuffer Management, Starfield Generation, PPM Exporter, and Testing.

Technologies and Tools Used

Programming Language: C++17

Compiler: MinGW-w64 (g++), GCC, or MSVC

Build and Execution Tools: PowerShell / Command Line

Output Image Format: Portable Pixmap (.ppm - P6 binary format)

Libraries: Standard C++ Library (cmath, vector, fstream, random, algorithm, cstdint, limits)

Graphics Techniques and Algorithms Implemented

3D World-to-Screen Perspective Projection: Converts 3D world coordinates (X, Y, Z) to 2D screen space coordinates using camera pitch rotation matrices and perspective division (X_screen = (X * fov) / Z, Y_screen = (-Y * fov) / Z).

Screen-Space Depth Buffering (Z-Buffer): Uses a 2D floating-point depth array matching canvas resolution to correctly handle depth testing and object occlusion (ensuring objects closer to the camera obscure those behind them).

3D Bresenham Line Algorithm: Implements discrete line drawing with continuous depth interpolation along paths, used for planetary orbit paths and Saturn's rings.

Directional Lighting and Shading (Lambertian Reflectance): Calculates surface normals across 3D spheres to compute diffuse light intensity using dot products between surface normals and light direction vectors.

3D Cubic Bézier Spline Interpolation: Calculates smooth parametric camera path curves between celestial objects using control points in 3D space.

Procedural Noise Generation: Renders random star positions across background depth layers using Mersenne Twister pseudo-random number generation.

How to Compile and Run

Open a terminal or PowerShell prompt in the project root folder.

Compile the source code using C++17:
g++ -std=c++17 main.cpp -o checkpoint1_demo

Execute the binary:
.\checkpoint1_demo.exe

View the generated output image file checkpoint1_render.ppm using standard image viewers or image extensions in VS Code.

Current Progress

Software renderer initialized working on a 1024x768 framebuffer canvas.

3D planetary system rendered with all 8 planets placed in relative orbital positions around the central Sun.

Directional lighting implemented to show realistic light and shadow sides across planetary surfaces.

Saturn ring structure, Earth's moon, planetary orbit lines, and a 3D camera spline flight trajectory rendered into the scene.

Z-buffer depth testing fully functional.

Known Limitations and Issues

Static Output: The current build outputs a static PPM image file instead of real-time interactive rendering in a desktop window.

Fixed Camera Orientation: Camera coordinates and pitch angles are hardcoded inside the render configuration rather than driven by user input controls.

Sphere Bounding Representation: Planets are rendered via screen-projected sphere volumes rather than explicit indexed triangle meshes.