#version 150 core
in vec4 vertex_colors;
in vec3 texture_coords;
out vec4 final_color;

uniform sampler2D sprite_texture;

void main() {
    final_color = texture(sprite_texture, texture_coords.xy) * vertex_colors;
    // final_color = vec4(0.52, 0.57, 0.57, final_color.a * 0.3);
    final_color = vec4(1.0, 1.0, 1.0, final_color.a * 0.4);

    // No GL_ALPHA_TEST in core, use shader to discard.
    if (final_color.a < 0.01) {
        discard;
    }
}