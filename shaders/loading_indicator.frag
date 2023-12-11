#version 150 core
in vec4 vertex_colors;
in vec3 texture_coords;
in vec3 frag_position;
// in vec4 comp_position;

out vec4 final_color;

uniform sampler2D sprite_texture;

// The current fill value (between 0 and 1).
// uniform float value;

void main() {
    // Fetch the current texture size.
    ivec2 texture_size = textureSize(sprite_texture, 0);

    // Fetch the current color.
    final_color = texture(sprite_texture, texture_coords.xy) * vertex_colors;
    // final_color = texture(sprite_texture, texture_coords.xy * 0.1 + frag_position.xy * 100) * vertex_colors;
    // vec4 source = texture(sprite_texture, texture_coords.xy) * vertex_colors;
    // final_color = vec4(gl_FragCoord.xy, 0.0, 1.0);

    // Coordinates greater than value% on the x axis should not be rendered.
    // if (texture_coords.x > value) {
    //     discard;
    // }

    // No GL_ALPHA_TEST in core, use shader to discard.
    if (final_color.a < 0.01) {
        discard;
    }
}