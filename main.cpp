#include <iostream>
#include <vector>
#include <fstream>
#include <cmath>
#include <algorithm>
#include <cstdint>
#include <random>

const int WIDTH = 1024;
const int HEIGHT = 768;

uint32_t framebuffer[HEIGHT][WIDTH];

void plotPixel(int x, int y, uint32_t color) {
    if (x >= 0 && x < WIDTH && y >= 0 && y < HEIGHT) {
        framebuffer[y][x] = color;
    }
}

// -----------------------------------------------------------------------------
// 0. Space Environment: Starfield
// -----------------------------------------------------------------------------
void drawStarfield(int count) {
    std::mt19937 rng(42);
    std::uniform_int_distribution<int> distX(0, WIDTH - 1);
    std::uniform_int_distribution<int> distY(0, HEIGHT - 1);
    std::uniform_int_distribution<int> distBrightness(120, 255);

    for (int y = 0; y < HEIGHT; ++y) {
        for (int x = 0; x < WIDTH; ++x) {
            framebuffer[y][x] = 0x00050510;
        }
    }

    for (int i = 0; i < count; ++i) {
        int val = distBrightness(rng);
        uint32_t starColor = (val << 16) | (val << 8) | val;
        plotPixel(distX(rng), distY(rng), starColor);
    }
}

// -----------------------------------------------------------------------------
// 1. Line Drawing: Bresenham's Line Algorithm
// -----------------------------------------------------------------------------
void drawLineBresenham(int x0, int y0, int x1, int y1, uint32_t color) {
    int dx = std::abs(x1 - x0);
    int dy = std::abs(y1 - y0);
    int sx = (x0 < x1) ? 1 : -1;
    int sy = (y0 < y1) ? 1 : -1;
    int err = dx - dy;

    while (true) {
        plotPixel(x0, y0, color);
        if (x0 == x1 && y0 == y1) break;
        int e2 = 2 * err;
        if (e2 > -dy) { err -= dy; x0 += sx; }
        if (e2 < dx) { err += dx; y0 += sy; }
    }
}

// -----------------------------------------------------------------------------
// 2. Midpoint Ellipse Algorithm (Fixed 64-bit Overflow)
// -----------------------------------------------------------------------------
void drawEllipseMidpoint(int centerX, int centerY, double rx, double ry, uint32_t color) {
    double rx2 = rx * rx;
    double ry2 = ry * ry;
    double x = 0;
    double y = ry;

    auto plotSymmetric = [&](int px, int py) {
        plotPixel(centerX + px, centerY + py, color);
        plotPixel(centerX - px, centerY + py, color);
        plotPixel(centerX + px, centerY - py, color);
        plotPixel(centerX - px, centerY - py, color);
    };

    // Region 1
    double d1 = ry2 - (rx2 * ry) + (0.25 * rx2);
    double dx = 2 * ry2 * x;
    double dy = 2 * rx2 * y;

    while (dx < dy) {
        plotSymmetric(static_cast<int>(x), static_cast<int>(y));
        if (d1 < 0) {
            x++;
            dx += 2 * ry2;
            d1 += dx + ry2;
        } else {
            x++; y--;
            dx += 2 * ry2;
            dy -= 2 * rx2;
            d1 += dx - dy + ry2;
        }
    }

    // Region 2
    double d2 = (ry2 * (x + 0.5) * (x + 0.5)) + (rx2 * (y - 1) * (y - 1)) - (rx2 * ry2);

    while (y >= 0) {
        plotSymmetric(static_cast<int>(x), static_cast<int>(y));
        if (d2 > 0) {
            y--;
            dy -= 2 * rx2;
            d2 += rx2 - dy;
        } else {
            y--; x++;
            dx += 2 * ry2;
            dy -= 2 * rx2;
            d2 += dx - dy + rx2;
        }
    }
}

// -----------------------------------------------------------------------------
// 3. Shaded Planet Renderer
// -----------------------------------------------------------------------------
void drawShadedPlanet(int centerX, int centerY, int radius, uint32_t baseColor, int sunX, int sunY) {
    int r = (baseColor >> 16) & 0xFF;
    int g = (baseColor >> 8) & 0xFF;
    int b = baseColor & 0xFF;

    for (int y = -radius; y <= radius; ++y) {
        for (int x = -radius; x <= radius; ++x) {
            if (x * x + y * y <= radius * radius) {
                int pixelX = centerX + x;
                int pixelY = centerY + y;

                float dirX = static_cast<float>(sunX - pixelX);
                float dirY = static_cast<float>(sunY - pixelY);
                float length = std::sqrt(dirX * dirX + dirY * dirY);

                if (length > 0) { dirX /= length; dirY /= length; }

                float nx = static_cast<float>(x) / radius;
                float ny = static_cast<float>(y) / radius;

                float lightFactor = (nx * (-dirX) + ny * (-dirY));
                lightFactor = std::max(0.15f, std::min(1.0f, lightFactor + 0.35f));

                uint8_t nr = static_cast<uint8_t>(r * lightFactor);
                uint8_t ng = static_cast<uint8_t>(g * lightFactor);
                uint8_t nb = static_cast<uint8_t>(b * lightFactor);

                plotPixel(pixelX, pixelY, (nr << 16) | (ng << 8) | nb);
            }
        }
    }
}

// -----------------------------------------------------------------------------
// 4. Glowing Sun Renderer
// -----------------------------------------------------------------------------
void drawGlowingSun(int centerX, int centerY, int radius) {
    for (int y = -radius * 2; y <= radius * 2; ++y) {
        for (int x = -radius * 2; x <= radius * 2; ++x) {
            float dist = std::sqrt(x * x + y * y);
            if (dist <= radius) {
                plotPixel(centerX + x, centerY + y, 0x00FFE066);
            } else if (dist <= radius * 1.8f) {
                float alpha = 1.0f - ((dist - radius) / (radius * 0.8f));
                uint8_t r = 255;
                uint8_t g = static_cast<uint8_t>(160 * alpha);
                plotPixel(centerX + x, centerY + y, (r << 16) | (g << 8));
            }
        }
    }
}

// -----------------------------------------------------------------------------
// 5. Parametric Bézier Camera Path
// -----------------------------------------------------------------------------
struct Point2D { int x, y; };

void drawBezierCurve(Point2D p0, Point2D p1, Point2D p2, Point2D p3, int segments, uint32_t color) {
    Point2D prev = p0;
    for (int i = 1; i <= segments; ++i) {
        float t = static_cast<float>(i) / segments;
        float u = 1.0f - t;

        float bx = u * u * u * p0.x + 3 * u * u * t * p1.x + 3 * u * t * t * p2.x + t * t * t * p3.x;
        float by = u * u * u * p0.y + 3 * u * u * t * p1.y + 3 * u * t * t * p2.y + t * t * t * p3.y;

        Point2D curr = { static_cast<int>(std::round(bx)), static_cast<int>(std::round(by)) };
        drawLineBresenham(prev.x, prev.y, curr.x, curr.y, color);
        prev = curr;
    }
}

void exportToPPM(const std::string& filename) {
    std::ofstream file(filename, std::ios::binary);
    file << "P6\n" << WIDTH << " " << HEIGHT << "\n255\n";
    for (int y = 0; y < HEIGHT; ++y) {
        for (int x = 0; x < WIDTH; ++x) {
            uint32_t pixel = framebuffer[y][x];
            file.put((pixel >> 16) & 0xFF);
            file.put((pixel >> 8) & 0xFF);
            file.put(pixel & 0xFF);
        }
    }
}

// -----------------------------------------------------------------------------
// Main Execution
// -----------------------------------------------------------------------------
int main() {
    int sunX = WIDTH / 2;
    int sunY = HEIGHT / 2 + 30; // Shift down slightly for perspective balance

    drawStarfield(500);

    // Orbit radii (rx, ry) set with isometric aspect ratio to change angle
    struct PlanetData {
        double rx, ry;
        int radius;
        uint32_t color;
        float angle;
    };

    // Tilted camera angle ratio (ry = rx * sin(tilt_angle))
    double tiltFactor = std::sin(35.0 * 3.14159 / 180.0); // 35 degree view angle

    std::vector<PlanetData> planets = {
        {  80.0,  80.0 * tiltFactor,  4, 0x00A6A6A6, 0.4f }, // Mercury
        { 120.0, 120.0 * tiltFactor,  6, 0x00E3BB76, 2.1f }, // Venus
        { 170.0, 170.0 * tiltFactor,  7, 0x002B82C5, 4.2f }, // Earth
        { 220.0, 220.0 * tiltFactor,  5, 0x00C1440E, 1.2f }, // Mars
        { 280.0, 280.0 * tiltFactor, 15, 0x00B07F35, 5.5f }, // Jupiter
        { 340.0, 340.0 * tiltFactor, 12, 0x00E2BF7D, 3.1f }, // Saturn
        { 400.0, 400.0 * tiltFactor,  9, 0x004B70DD, 0.8f }, // Uranus
        { 450.0, 450.0 * tiltFactor,  9, 0x00274687, 2.5f }  // Neptune
    };

    // 1. Draw Orbit Ellipses
    for (const auto& p : planets) {
        drawEllipseMidpoint(sunX, sunY, p.rx, p.ry, 0x002A2A44);
    }

    // 2. Draw Sun Core
    drawGlowingSun(sunX, sunY, 26);

    Point2D earthPos = { 0, 0 };
    Point2D saturnPos = { 0, 0 };

    // 3. Render Planets & Saturn Rings
    for (size_t i = 0; i < planets.size(); ++i) {
        const auto& p = planets[i];

        int px = sunX + static_cast<int>(p.rx * std::cos(p.angle));
        int py = sunY + static_cast<int>(p.ry * std::sin(p.angle));

        if (i == 2) earthPos = { px, py };
        if (i == 5) saturnPos = { px, py };

        if (i == 5) { // Saturn rings
            drawEllipseMidpoint(px, py, 26, 26 * tiltFactor, 0x00C2A060);
            drawEllipseMidpoint(px, py, 30, 30 * tiltFactor, 0x00997A40);
        }

        drawShadedPlanet(px, py, p.radius, p.color, sunX, sunY);

        if (i == 2) { // Moon
            int mx = px + 14;
            int my = py - 6;
            drawShadedPlanet(mx, my, 2, 0x00CCCCCC, sunX, sunY);
        }
    }

    // 4. Draw Camera Flight Spline
    Point2D camCtrl1 = { earthPos.x - 60, earthPos.y - 100 };
    Point2D camCtrl2 = { saturnPos.x + 80, saturnPos.y - 80 };
    drawBezierCurve(earthPos, camCtrl1, camCtrl2, saturnPos, 40, 0x0000FFCC);

    exportToPPM("checkpoint1_render.ppm");
    std::cout << "Fix applied! Clean curved ellipses rendered." << std::endl;

    return 0;
}