#version 150 core

in vec4 vertex_colors;
in vec3 texture_coords;
out vec4 final_color;

uniform sampler2D sprite_texture;

// Lookup palette texture.
uniform sampler2D palette;

// Tells how much the original and alternate colors should be mixed together.
// Usually this depends on stats.
uniform float mixer;

// Tells whether to display all white or not.
uniform bool hit;

// Tells whether to darken the resulting color (when dead).
uniform bool dead;

// Checks whether [color_1] and [color_2] are the same
// (aka they do not differ by more than [tolerance] on each channel).
bool full_color_match(vec4 color_1, vec4 color_2, float tolerance) {
    return (
        abs(color_1.r - color_2.r) < tolerance &&
        abs(color_1.g - color_2.g) < tolerance &&
        abs(color_1.b - color_2.b) < tolerance &&
        abs(color_1.a - color_2.a) < tolerance
    );
}

// Checks whether [color_1] and [color_2] are the same
// (aka they do not differ by more than [tolerance] on each channel).
bool color_match(vec3 color_1, vec3 color_2, float tolerance) {
    return (
        abs(color_1.r - color_2.r) < tolerance &&
        abs(color_1.g - color_2.g) < tolerance &&
        abs(color_1.b - color_2.b) < tolerance
    );
}

// Fetches the alternate color from [palette_texture] and mixes it with source.
// [source] is the color to look up for.
// [palette_texture] is the texture where to look for the alternate color. Should be a 2xN texture,
// where N is the number of colors present in the sprite texture.
// [tuner] defines the amount of mixing between [source] and the fetched color. Should be between
// 0 and 1. 0 means all source, 1 means all fetched.
vec4 alt_color(vec4 source, sampler2D palette_texture, float tuner) {
    // Fetch palette size in order to look it up.
    ivec2 palette_size = textureSize(palette_texture, 0);
    // vec4 new_color = source;
    // Setting the color to plain red helps you spot errors in the shader.
    vec4 new_color = vec4(1.0, 0.0, 0.0, source.a);

    // Precompute palette height as float.
    float palette_width = float(palette_size.x);
    float palette_height = float(palette_size.y);
    // float half_pixel_width = 0.5f / palette_width;
    // float half_pixel_height = 0.5f / palette_height;
    float half_pixel_width = 0.5f;
    float half_pixel_height = 0.5f;
    // new_color = texelFetch(palette_texture, ivec2(0, 0), 0);

    // Look for the current color in the palette.
    for (int i = 0; i < palette_size.y; i++) {
        // Fetch the i-th color in the first column of the palette.
        // CAREFUL: vertical coordinates are offset by half a pixel in order to make sure the middle part of the texel is fetched.
        // vec4 palette_color = texture(palette_texture, vec2(0.0f + half_pixel_width, (float(i) / palette_height) + half_pixel_height));
        vec4 palette_color = texelFetch(palette_texture, ivec2(0, i), 0);

        if (color_match(source.rgb, palette_color.rgb, 0.05f)) {
            // If it matches the current UV color, then save the i-th color in the second column
            // of the palette.
            // new_color = texture(palette_texture, vec2((1.0f / palette_width) + half_pixel_width, (float(i) / palette_height) + half_pixel_height));
            new_color = texelFetch(palette_texture, ivec2(1, i), 0);
            new_color = vec4(mix(source, new_color, tuner).rgb, source.a);
            break;
        }
    }

    return new_color;
    // return vec4(1.0, 0.5, 0.5, 0.5);
}

void main(){
    // Fetch original color.
    vec4 source = texture(sprite_texture, texture_coords.xy) * vertex_colors;

    vec4 color = source;

    // White color if hit.
    if (hit) {
        color = vec4(1.0, 1.0, 1.0, source.a);
    } else {
        // Fetch alternate color from palette.
        color = alt_color(source, palette, mixer);

        if (dead) {
            color.rgb *= 0.6;
        }
    }

    // Set the newly calculated color.
    final_color = color;
    // final_color = texture(palette, vec2(0.1, 0.1));
    // final_color = texelFetch(palette, ivec2(1, 3), 0);
}