"""
Copyright (c) 2020 Gustavo Valiente gustavo.valiente@protonmail.com
zlib License, see LICENSE file.
"""
import json

import pygame

from draw import draw_polygon
from export import generate_shape_groups, write_frames, generate_horizontal_line_sets, generate_shapes, \
    generate_horizontal_line_groups, optimize_screen_buffer_colors


def gba_vertex(st_vertex):
    x_margin = 0
    x = x_margin + float(st_vertex['x']) * ((240 - x_margin) / 256)
    x = int(round(x))
    y = float(st_vertex['y']) * (160 / 200)
    y = int(round(y))
    return x, y


def draw_horizontal_line_sets(screen, horizontal_line_sets, colors):
    for color_index, horizontal_lines in horizontal_line_sets.items():
        color = colors[color_index]

        for horizontal_line in horizontal_lines:
            y = horizontal_line[0]
            pygame.draw.line(screen, color, (horizontal_line[1], y), (horizontal_line[2], y))


def draw_horizontal_line_groups(screen, horizontal_line_groups, colors):
    for horizontal_line_group in horizontal_line_groups:
        for y, line_pair in enumerate(horizontal_line_group):
            if line_pair is not None:
                color_index = line_pair[0]
                line = line_pair[1]
                pygame.draw.line(screen, colors[color_index], (line[1], y), (line[2], y))


def draw_shapes(screen, shapes, colors):
    for shape in shapes:
        color = colors[shape[0]]
        y = shape[1]

        for horizontal_line in shape[3]:
            pygame.draw.line(screen, color, (horizontal_line[0], y), (horizontal_line[1], y))
            y += 1


def draw_shape_groups(screen, shape_groups, colors):
    # print(len(shape_groups))

    for shape_group in shape_groups:
        draw_shapes(screen, shape_group, colors)


with open('niccc.json') as json_file:
    niccc = json.load(json_file)

pygame.init()
screen = pygame.display.set_mode([240, 160])
clock = pygame.time.Clock()

output_frames = []

for frame_index, frame in enumerate(niccc['frames']):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    colors = []

    for frame_color in frame['palette']:
        colors.append(pygame.Color(frame_color))

    try:
        frame_vertices = frame['vertices']
        indexed_vertices = True
    except KeyError:
        frame_vertices = []
        indexed_vertices = False

    vertices = []

    for frame_vertex in frame_vertices:
        vertices.append(gba_vertex(frame_vertex))

    screen_buffer = [0] * 160

    for i in range(160):
        screen_buffer[i] = [0] * 240

    for frame_polygon in frame['polygons']:
        polygon_vertices = []

        if indexed_vertices:
            for vertex_index in frame_polygon['verticesIdx']:
                polygon_vertices.append(vertices[vertex_index['idx']])
        else:
            for vertex in frame_polygon['vertices']:
                polygon_vertices.append(gba_vertex(vertex))

        color_index = frame_polygon['colidx']

        if color_index > 0:
            draw_polygon(screen, color_index, polygon_vertices, screen_buffer)

    optimize_screen_buffer_colors(screen_buffer, colors)
    screen.fill(colors[0])

    horizontal_line_sets = generate_horizontal_line_sets(screen_buffer)
    # draw_horizontal_line_sets(screen, horizontal_line_sets, colors)

    horizontal_line_groups = generate_horizontal_line_groups(horizontal_line_sets)
    # draw_horizontal_line_groups(screen, horizontal_line_groups, colors)

    shapes = generate_shapes(horizontal_line_groups)
    # draw_shapes(screen, shapes, colors)

    shape_groups = generate_shape_groups(shapes)
    draw_shape_groups(screen, shape_groups, colors)

    output_frames.append((colors, shape_groups))

    pygame.display.flip()
    clock.tick(60)

    # if len(output_frames) >= 2 * 60:
    #     break

write_frames(output_frames)
