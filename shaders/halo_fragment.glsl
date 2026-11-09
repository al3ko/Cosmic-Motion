#version 330 core

in vec2 v_texcoord;
out vec4 fragColor;

uniform vec3 u_halo_color;

void main() {
    // Distance from center of billboard quad (0.5, 0.5)
    float dist = length(v_texcoord - vec2(0.5));
    
    // Soft radial falloff curve
    float alpha = max(0.0, 1.0 - smoothstep(0.0, 0.5, dist));
    alpha = pow(alpha, 2.5);

    fragColor = vec4(u_halo_color, alpha * 0.6);
}