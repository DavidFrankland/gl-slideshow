vec4 transition(vec2 uv) {
    // Interpolate smoothly between the two images
    float t = smoothstep(0.0, 1.0, progress);
    return mix(getFromColor(uv), getToColor(uv), t);
}