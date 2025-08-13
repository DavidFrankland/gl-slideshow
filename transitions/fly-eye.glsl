// Author: gre
// License: MIT

const float size = 0.04;
const float zoom = 50.0;
const float colorSeparation = 0.3;
const float aspect_ratio = 1.6;

vec4 transition(vec2 p) {
  float inv = 1. - progress;
  vec2 disp = size*vec2(cos(zoom*p.x*aspect_ratio), sin(zoom*p.y));
  vec4 texTo = getToColor(p + inv*disp);
  vec4 texFrom = vec4(
    getFromColor(p + progress*disp*(1.0 - colorSeparation)).r,
    getFromColor(p + progress*disp).g,
    getFromColor(p + progress*disp*(1.0 + colorSeparation)).b,
    1.0);
  return texTo*progress + texFrom*inv;
}
