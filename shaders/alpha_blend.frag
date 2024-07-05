#version 150 core

in vec4 vertex_colors;
in vec3 texture_coords;
out vec4 final_color;

uniform sampler2D sprite_texture;

// Alpha channel.
uniform float alpha;

void main() {
    final_color = texture(sprite_texture, texture_coords.xy) * vertex_colors;
    final_color = vec4(1.0, 1.0, 1.0, final_color.a * alpha);

    // Discard transparent fragments or they'll be drawn over other sprites' on the same layer.
    if (final_color.a < 0.01) {
        discard;
    }
}