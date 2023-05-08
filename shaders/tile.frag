#version 150 core

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