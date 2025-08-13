#version 330

in vec2 pos;
out vec2 uv;

void main()
{
    uv = (pos + 1.0) / 2.0;
    gl_Position = vec4(pos, 0, 1);
}