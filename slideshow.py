import glfw
from OpenGL.GL import *
from PIL import Image
import numpy as np
import time
import os
import random
from typing import List


def load_shader_source(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def load_texture(path: str):
    img = Image.open(path).convert("RGB").transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    img_data = np.array(img, np.uint8)
    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    return tex


def compile_shader(source: str, shader_type: int):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
        raise RuntimeError(glGetShaderInfoLog(shader))
    return shader


def create_program(vertex_src: str, fragment_src: str):
    vs = compile_shader(vertex_src, GL_VERTEX_SHADER)
    fs = compile_shader(fragment_src, GL_FRAGMENT_SHADER)
    program = glCreateProgram()
    glAttachShader(program, vs)
    glAttachShader(program, fs)
    glLinkProgram(program)
    if glGetProgramiv(program, GL_LINK_STATUS) != GL_TRUE:
        raise RuntimeError(glGetProgramInfoLog(program))
    glDeleteShader(vs)
    glDeleteShader(fs)
    return program


def get_images(folder: str) -> List[str]:
    img_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif')
    files = [f for f in os.listdir(folder) if f.lower().endswith(img_exts)]
    if len(files) < 2:
        raise ValueError("not enough images in the folder")
    return [os.path.join(folder, f) for f in sorted(files)]


def get_transitions(folder: str) -> List[str]:
    files = [f for f in os.listdir(folder) if f.lower().endswith('.glsl')]
    if len(files) == 0:
        raise ValueError(f"no fragment .glsl transitions found in folder: {folder}")
    return [os.path.join(folder, f) for f in files]


def draw_transition(window, program, tex1, tex2, progress):
    glClear(GL_COLOR_BUFFER_BIT)
    glUseProgram(program)
    glUniform1f(glGetUniformLocation(program, "progress"), progress)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, tex1)
    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D, tex2)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
    glfw.swap_buffers(window)
    glfw.poll_events()


def main() -> None:

    transition_duration: float = 1.5
    pause_duration: float = 1.0

    image_folder = "oms-images"
    shader_folder = "transitions"
    source_folder = "source"

    if not os.path.isdir(image_folder):
        raise ValueError("invalid image folder")
    if not os.path.isdir(shader_folder):
        raise ValueError("invalid shader folder")
    if not os.path.isdir(source_folder):
        raise ValueError("invalid source folder")

    image_paths: List[str] = get_images(image_folder)
    transition_paths: List[str] = get_transitions(shader_folder)
    vertex_path: str = os.path.join(source_folder, "vertex.glsl")
    vertex_src: str = load_shader_source(vertex_path)
    header_path: str = os.path.join(source_folder, "fragment-header.glsl")
    header_src: str = load_shader_source(header_path)
    footer_path: str = os.path.join(source_folder, "fragment-footer.glsl")
    footer_src: str = load_shader_source(footer_path)

    if not glfw.init():
        raise Exception("glfw can not be initialized")

    monitor = glfw.get_primary_monitor()
    mode = glfw.get_video_mode(monitor)
    window = glfw.create_window(mode.size.width, mode.size.height, "Fullscreen Window", monitor, None)

    if not window:
        glfw.terminate()
        raise Exception("glfw window can not be created")

    glfw.make_context_current(window)
    width, height = glfw.get_framebuffer_size(window)
    glViewport(0, 0, width, height)

    quad: np.ndarray = np.array([
        [-1, -1],
        [1, -1],
        [-1, 1],
        [1, 1],
    ], dtype=np.float32)

    glBindVertexArray(glGenVertexArrays(1))
    glBindBuffer(GL_ARRAY_BUFFER, glGenBuffers(1))
    glBufferData(GL_ARRAY_BUFFER, quad.nbytes, quad, GL_STATIC_DRAW)

    # Preload all textures
    textures: List[int] = [load_texture(p) for p in image_paths]

    # Loop through image pairs
    image_index: int = 0
    trans_index: int = 0

    while not glfw.window_should_close(window):
        tex1: int = textures[image_index]
        tex2: int = textures[(image_index + 1) % len(textures)]
        fragment_path: str = transition_paths[trans_index]
        trans_index = (trans_index+1) % len(transition_paths)
        print(fragment_path)
        fragment_src: str = load_shader_source(fragment_path)
        fragment_src = header_src + fragment_src + footer_src

        program = create_program(vertex_src, fragment_src)

        pos_loc = glGetAttribLocation(program, "pos")
        glEnableVertexAttribArray(pos_loc)
        glVertexAttribPointer(pos_loc, 2, GL_FLOAT, GL_FALSE, 0, None)

        glUseProgram(program)
        glUniform1i(glGetUniformLocation(program, "from"), 0)
        glUniform1i(glGetUniformLocation(program, "to"), 1)

        # show first image
        start_time: float = time.time()
        while time.time() - start_time < pause_duration and not glfw.window_should_close(window):
            draw_transition(window, program, tex1, tex2, 0.0)

        # transition to the second image
        start_time: float = time.time()
        frame_count: int = 0
        while not glfw.window_should_close(window):
            elapsed: float = time.time() - start_time
            progress: float = min(elapsed / transition_duration, 1.0)
            draw_transition(window, program, tex1, tex2, progress)
            frame_count += 1
            if progress >= 1.0:
                break
        
        fps = frame_count / transition_duration
        print(f'{fps:.2f} fps')

        image_index = (image_index + 1) % len(textures)
        glDeleteProgram(program)

    glfw.terminate()


if __name__ == "__main__":
    main()
