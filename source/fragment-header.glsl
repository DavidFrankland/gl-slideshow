#version 100

precision mediump float;

uniform sampler2D from;
uniform sampler2D to;
uniform float progress;
varying vec2 uv;

vec4 getFromColor(vec2 v2)
{
    return texture2D(from, v2);
}

vec4 getToColor(vec2 v2)
{
    return texture2D(to, v2);
}
