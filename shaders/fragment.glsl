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
uniform bool u_is_star;   // Starfield rendering flag

void main() {
    if (u_is_star) {
        // Crisp bright white star emission
        fragColor = vec4(1.0, 1.0, 1.0, 1.0);
        return;
    }

    if (u_is_orbit) {
        fragColor = vec4(0.95, 0.95, 1.0, 0.70);
        return;
    }

    vec4 tex_color = texture(u_texture, v_texcoord);

    if (u_is_sun) {
        fragColor = vec4(tex_color.rgb * 1.35, tex_color.a);
        return;
    }

    // Standard Phong Shading
    float ambient_strength = 0.40;
    vec3 ambient = ambient_strength * vec3(1.0);

    vec3 norm = normalize(v_normal);
    vec3 light_dir = normalize(u_light_pos - v_frag_pos);
    float diff = max(dot(norm, light_dir), 0.0);
    vec3 diffuse = diff * vec3(1.0);

    float specular_strength = 0.25;
    vec3 view_dir = normalize(u_view_pos - v_frag_pos);
    vec3 reflect_dir = reflect(-light_dir, norm);
    float spec = pow(max(dot(view_dir, reflect_dir), 0.0), 32.0);
    vec3 specular = specular_strength * spec * vec3(1.0);

    vec3 final_color = (ambient + diffuse + specular) * tex_color.rgb;
    fragColor = vec4(final_color, tex_color.a);
}