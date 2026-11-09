#version 330 core

// Attributes matching VBO layout (3f position, 2f texcoord, 3f normal)
layout (location = 0) in vec3 in_position;
layout (location = 1) in vec2 in_texcoord;
layout (location = 2) in vec3 in_normal;

// Outputs passed to fragment shader
out vec2 v_texcoord;
out vec3 v_normal;
out vec3 v_frag_pos;

// Transformation matrices
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    vec4 world_pos = model * vec4(in_position, 1.0);
    v_frag_pos = vec3(world_pos);
    v_texcoord = in_texcoord;
    
    // Transform normals to world space (handles non-uniform scaling)
    v_normal = mat3(transpose(inverse(model))) * in_normal;
    
    gl_Position = projection * view * world_pos;
}