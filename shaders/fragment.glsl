#version 330 core

in vec2 v_texcoord;
in vec3 v_normal;
in vec3 v_frag_pos;

out vec4 fragColor;

uniform sampler2D u_texture;
uniform vec3 u_light_pos;
uniform vec3 u_view_pos;
uniform bool u_is_sun;
uniform bool u_is_orbit;
uniform bool u_is_star;
uniform bool u_is_asteroid;
uniform bool u_is_ring;

void main() {
    if (u_is_star) {
        fragColor = vec4(1.0, 1.0, 1.0, 1.0);
        return;
    }

    if (u_is_asteroid) {
        vec2 point = gl_PointCoord - vec2(0.5);
        if (length(point) > 0.5) discard;
        float seed = fract(sin(dot(floor(v_frag_pos * 17.0), vec3(12.9898, 78.233, 37.719))) * 43758.5453);
        vec3 rock_color = mix(vec3(0.24, 0.22, 0.19), vec3(0.52, 0.43, 0.31), seed);
        float edge = 1.0 - smoothstep(0.34, 0.5, length(point));
        fragColor = vec4(rock_color * (0.62 + edge * 0.38), 1.0);
        return;
    }

    if (u_is_orbit) {
        fragColor = vec4(0.95, 0.95, 1.0, 0.70);
        return;
    }

    vec4 tex_color = texture(u_texture, v_texcoord);
    vec3 albedo = pow(max(tex_color.rgb, vec3(0.0)), vec3(2.2));

    if (u_is_sun) {
        vec3 solar_color = pow(albedo * 1.5, vec3(1.0 / 2.2));
        fragColor = vec4(solar_color, tex_color.a);
        return;
    }

    // Treat the color map as sRGB and do lighting in linear space.
    vec3 normal = normalize(v_normal);
    vec3 light_dir = normalize(u_light_pos - v_frag_pos);

    if (u_is_ring) {
        // Ring particles sit in a thin plane; grazing sunlight needs a modest
        // floor so the translucent material remains visible in this scale model.
        float ring_light = 0.28 + 0.62 * abs(dot(normal, light_dir));
        vec3 ring_color = pow(max(tex_color.rgb, vec3(0.0)), vec3(2.2)) * ring_light;
        fragColor = vec4(pow(ring_color, vec3(1.0 / 2.2)), tex_color.a);
        return;
    }

    float diffuse = max(dot(normal, light_dir), 0.0);
    float lighting = 0.10 + 0.95 * diffuse;

    // Restrained specular response keeps land and cloud maps from looking plastic.
    vec3 view_dir = normalize(u_view_pos - v_frag_pos);
    vec3 reflect_dir = reflect(-light_dir, normal);
    float spec = pow(max(dot(view_dir, reflect_dir), 0.0), 48.0) * 0.08 * diffuse;

    float fresnel = pow(1.0 - max(dot(normal, view_dir), 0.0), 3.0);
    vec3 rim_glow = albedo * fresnel * 0.06;

    vec3 linear_color = (albedo * lighting) + vec3(spec) + rim_glow;
    vec3 display_color = pow(max(linear_color, vec3(0.0)), vec3(1.0 / 2.2));
    fragColor = vec4(display_color, tex_color.a);
}
