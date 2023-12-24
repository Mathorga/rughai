#version 150 core
in vec4 vertex_colors;
in vec3 texture_coords;

out vec4 final_color;

uniform sampler2D sprite_texture;

// The current fill value (between 0 and 1).
uniform float fill;
uniform vec3 sw_coord;
uniform vec3 ne_coord;


/// Scale the given fill from the scale of src to the scale of dst.
float scale(float val, float src_start, float src_end, float dst_start, float dst_end) {
    return ((val - src_start) / (src_end - src_start)) * (dst_end - dst_start) + dst_start;
}

void main() {
    // Fetch the current texture size.
    ivec2 texture_size = textureSize(sprite_texture, 0);

    // Fetch the current color.
    final_color = texture(sprite_texture, texture_coords.xy) * vertex_colors;

    // Coordinates greater than fill on the x axis should not be rendered.
    if (texture_coords.x > (ne_coord.x - sw_coord.x) * fill + sw_coord.x) {
        final_color.a = 0.0;
    }
}