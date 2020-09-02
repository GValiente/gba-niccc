"""
Copyright (c) 2020 Gustavo Valiente gustavo.valiente@protonmail.com
zlib License, see LICENSE file.
"""


def draw_polygon(surface, color, points, screen_buffer):
    num_points = len(points)
    point_x = [x for x, y in points]
    point_y = [y for x, y in points]

    miny = min(point_y)
    maxy = max(point_y)

    if miny == maxy:
        minx = min(point_x)
        maxx = max(point_x)
        _clip_and_draw_horizline(surface, color, minx, miny, maxx, screen_buffer)
        return

    for y_coord in range(miny, maxy + 1):
        x_intersect = []
        for i in range(num_points):
            _draw_polygon_inner_loop(i, point_x, point_y,
                                     y_coord, x_intersect)

        x_intersect.sort()
        for i in range(0, len(x_intersect), 2):
            _clip_and_draw_horizline(surface, color, x_intersect[i], y_coord,
                                     x_intersect[i + 1], screen_buffer)

    # special case : horizontal border lines
    for i in range(num_points):
        i_prev = i - 1 if i else num_points - 1
        if miny < point_y[i] == point_y[i_prev] < maxy:
            _clip_and_draw_horizline(surface, color, point_x[i], point_y[i],
                                     point_x[i_prev], screen_buffer)


def _clip_and_draw_horizline(surf, color, x_from, in_y, x_to, screen_buffer):
    """draw clipped horizontal line."""
    # check Y inside surf
    clip = surf.get_clip()
    if in_y < clip.y or in_y >= clip.y + clip.h:
        return

    x_from = max(x_from, clip.x)
    x_to = min(x_to, clip.x + clip.w - 1)

    # check any x inside surf
    if x_to < clip.x or x_from >= clip.x + clip.w:
        return

    _drawhorzline(surf, color, x_from, in_y, x_to, screen_buffer)


def _drawhorzline(surf, color, x_from, in_y, x_to, screen_buffer):
    if x_from == 10:
        x_from += 0

    if x_from == x_to:
        # surf.set_at((x_from, in_y), color)
        screen_buffer[in_y][x_from] = color
        return

    start, end = (x_from, x_to) if x_from <= x_to else (x_to, x_from)
    for line_x in range(start, end + 1):
        # surf.set_at((line_x, in_y), color)
        screen_buffer[in_y][line_x] = color


def _draw_polygon_inner_loop(index, point_x, point_y, y_coord, x_intersect):
    i_prev = index - 1 if index else len(point_x) - 1

    y_1 = point_y[i_prev]
    y_2 = point_y[index]

    if y_1 < y_2:
        x_1 = point_x[i_prev]
        x_2 = point_x[index]
    elif y_1 > y_2:
        y_2 = point_y[i_prev]
        y_1 = point_y[index]
        x_2 = point_x[i_prev]
        x_1 = point_x[index]
    else:  # special case handled below
        return

    if ((y_2 > y_coord >= y_1) or
            ((y_coord == max(point_y)) and (y_coord <= y_2))):
        x_intersect.append((y_coord - y_1) *
                           (x_2 - x_1) //
                           (y_2 - y_1) + x_1)
