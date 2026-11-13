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

void main() {
    if (u_is_star) {
        fragColor = vec4(1.0, 1.0, 1.0, 1.0);
        return;
    }

    if (u_is_orbit) {
        fragColor = vec4(0.95, 0.95, 1.0, 0.70);
        return;
    }

    vec4 tex_color = texture(u_texture, v_texcoord);

    if (u_is_sun) {
        fragColor = vec4(tex_color.rgb * 1.30, tex_color.a);
        return;
    }

    // 1. Micro-relief surface detail derived from texture luminance gradients
    float lum = dot(tex_color.rgb, vec3(0.299, 0.587, 0.114));
    vec3 dpos_dx = dFdx(v_frag_pos);
    vec3 dpos_dy = dFdy(v_frag_pos);
    float dlum_dx = dFdx(lum);
    float dlum_dy = dFdy(lum);

    vec3 base_norm = normalize(v_normal);
    vec3 bump_norm = normalize(base_norm - 0.18 * (dlum_dx * normalize(dpos_dx) + dlum_dy * normalize(dpos_dy)));

    // 2. Full-visibility illumination (no dark shadow side)
    vec3 light_dir = normalize(u_light_pos - v_frag_pos);
    // Half-Lambert wrap lighting keeps the far side completely clear and bright
    float wrap_diff = dot(bump_norm, light_dir) * 0.5 + 0.5;
    float lighting = mix(0.85, 1.15, wrap_diff);

    // 3. Subtle specular sheen for crisp 3D curvature
    vec3 view_dir = normalize(u_view_pos - v_frag_pos);
    vec3 reflect_dir = reflect(-light_dir, bump_norm);
    float spec = pow(max(dot(view_dir, reflect_dir), 0.0), 24.0) * 0.15;

    // 4. Subtle Fresnel atmospheric limb brightening for 3D spherical volume
    float fresnel = pow(1.0 - max(dot(base_norm, view_dir), 0.0), 3.0);
    vec3 rim_glow = tex_color.rgb * fresnel * 0.22;

    vec3 final_color = (tex_color.rgb * lighting) + vec3(spec) + rim_glow;
    fragColor = vec4(final_color, tex_color.a);
}