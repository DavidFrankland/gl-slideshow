#version 330

uniform sampler2D from;
uniform sampler2D to;
uniform float progress;
in vec2 uv;
out vec4 fragColor;

vec4 getFromColor(vec2 v2)
{
    return texture(from, v2);
}

vec4 getToColor(vec2 v2)
{
    return texture(to, v2);
}
