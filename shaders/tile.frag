#version 150 core

// Make sure you offset your texture coordinates with 1/2 pixel, because in OpenGL the texel origin are defined to be the bottom left corner of a texel.
// That means that the exact center of a texel is located at [S'+0.5, T'+0.5] where S' and T' are the unnormalized texture coordinates.
// https://www.reddit.com/r/opengl/comments/6h7rkl/comment/diwo35x/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button

in vec4 vertex_colors;
in vec3 texture_coords;
uniform sampler2D tex;
out vec4 final_color;

void main(){
    ivec2 texSize = textureSize(tex, 0);
    float x_offset = (1.0 / (float(texSize.x))) * 0.5;
    float y_offset = (1.0 / (float(texSize.y))) * 0.5;
    vec2 tc_final = vec2(texture_coords.x + x_offset, texture_coords.y + y_offset);
    // final_color = texture(tex, tc_final);
    final_color = vec4(0xFF, 0x00, 0x00, 0xFF);
}