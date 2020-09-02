"""
Copyright (c) 2020 Gustavo Valiente gustavo.valiente@protonmail.com
zlib License, see LICENSE file.
"""
import os
import shutil


def optimize_screen_buffer_colors(screen_buffer, colors):
    colors_count = [0] * 160

    for screen_line in screen_buffer:
        for x, color_index in enumerate(screen_line):
            colors_count[color_index] += 1

    most_common_color_index = -1
    most_common_color_count = -1

    for color_index, color_count in enumerate(colors_count):
        if color_count > most_common_color_count:
            most_common_color_count = color_count
            most_common_color_index = color_index

    if most_common_color_index != 0:
        colors[0], colors[most_common_color_index] = colors[most_common_color_index], colors[0]

        for screen_line in screen_buffer:
            for x, color_index in enumerate(screen_line):
                if color_index == 0:
                    screen_line[x] = most_common_color_index
                elif color_index == most_common_color_index:
                    screen_line[x] = 0


def generate_horizontal_line_sets(screen_buffer):
    horizontal_line_sets = {}

    for y, screen_line in enumerate(screen_buffer):
        start_x = 0
        current_color_index = screen_line[0]

        for x, color_index in enumerate(screen_line):
            if color_index != current_color_index:
                if current_color_index > 0:
                    if current_color_index not in horizontal_line_sets:
                        horizontal_line_sets[current_color_index] = []

                    horizontal_line_sets[current_color_index].append((y, start_x, x - 1))

                start_x = x
                current_color_index = color_index

        if current_color_index > 0:
            if current_color_index not in horizontal_line_sets:
                horizontal_line_sets[current_color_index] = []

            horizontal_line_sets[current_color_index].append((y, start_x, len(screen_line) - 1))

    return horizontal_line_sets


def generate_horizontal_line_groups(horizontal_line_sets):
    horizontal_line_groups = []

    for color_index, horizontal_lines in horizontal_line_sets.items():
        if color_index != 0:
            _split_horizontal_lines(horizontal_lines)
            _group_horizontal_lines(color_index, horizontal_lines, horizontal_line_groups)

    return horizontal_line_groups


def generate_shapes(horizontal_line_groups):
    shapes = []

    for horizontal_line_group in horizontal_line_groups:
        shape_lines = []
        shape_start_y = 0
        shape_current_y = 0
        shape_current_color_index = 0

        for line_y, line_pair in enumerate(horizontal_line_group):
            if line_pair is None:
                if len(shape_lines) > 0:
                    shapes.append((shape_current_color_index, shape_start_y, shape_current_y, shape_lines))
                    shape_lines = []
            else:
                color_index = line_pair[0]
                line = line_pair[1]

                if len(shape_lines) > 0 and (shape_current_color_index != color_index):
                    shapes.append((shape_current_color_index, shape_start_y, shape_current_y, shape_lines))
                    shape_lines = []

                if len(shape_lines) == 0:
                    shape_start_y = line_y

                shape_current_y = line_y
                shape_current_color_index = color_index
                shape_lines.append((line[1], line[2]))

        if len(shape_lines) > 0:
            shapes.append((shape_current_color_index, shape_start_y, shape_current_y, shape_lines))

    return shapes


def generate_shape_groups(shapes):
    def collide(a, b):
        if a[1] < b[1]:
            return a[2] >= b[1]
        else:
            return b[2] >= a[1]

    shape_groups = []

    for shape in shapes:
        new_shape = True

        for shape_group in shape_groups:
            collision = False

            for group_shape in shape_group:
                if collide(shape, group_shape):
                    collision = True
                    break

            if not collision:
                shape_group.append(shape)
                new_shape = False
                break

        if new_shape:
            shape_groups.append([shape])

    def start_y(item):
        return item[1]

    for shape_group in shape_groups:
        shape_group.sort(key=start_y)

    return shape_groups


def _split_horizontal_lines(horizontal_lines):
    num_horizontal_lines = len(horizontal_lines)
    max_length = 62
    i = 0

    while i < num_horizontal_lines:
        line = horizontal_lines[i]

        if line[2] - line[1] >= max_length:
            horizontal_lines[i] = (line[0], line[1], line[1] + max_length)
            horizontal_lines.append((line[0], line[1] + max_length, line[2]))
            num_horizontal_lines += 1

        i += 1


def _group_horizontal_lines(color_index, horizontal_lines, horizontal_line_groups):
    for horizontal_line in horizontal_lines:
        horizontal_line_y = horizontal_line[0]
        target_horizontal_line_group = None

        for horizontal_line_group in horizontal_line_groups:
            if horizontal_line_group[horizontal_line_y] is None:
                target_horizontal_line_group = horizontal_line_group
                break

        if target_horizontal_line_group is None:
            target_horizontal_line_group = [None] * 160
            horizontal_line_groups.append(target_horizontal_line_group)

        target_horizontal_line_group[horizontal_line_y] = (color_index, horizontal_line)


def write_frames(frames, output_folder_path='../data'):
    if os.path.exists(output_folder_path):
        print('Removing ' + output_folder_path + ' ...')
        shutil.rmtree(output_folder_path)

    print('Creating ' + output_folder_path + ' ...')
    os.makedirs(output_folder_path)

    max_frames_per_file = 60

    frames_file = None
    frames_file_index = 0
    frames_file_count = 0

    for frame_index, _ in enumerate(frames):
        if frames_file is None:
            frames_file_path = output_folder_path + '/frames_' + str(frames_file_index) + '_data.h'
            print('Writing header file ' + frames_file_path + ' ...')
            frames_file = open(frames_file_path, 'w')
            frames_file.write('#ifndef FRAMES_' + str(frames_file_index) + '_DATA_H' + '\n')
            frames_file.write('#define FRAMES_' + str(frames_file_index) + '_DATA_H' + '\n\n')
            frames_file.write('class frame;' + '\n\n')

        frames_file.write('[[nodiscard]] const frame& frame_' + str(frame_index) + '();' + '\n\n')
        frames_file_count += 1

        if frames_file_count == max_frames_per_file:
            frames_file.write('#endif' + '\n')
            frames_file.close()
            frames_file = None
            frames_file_index += 1
            frames_file_count = 0

    if frames_file is not None:
        frames_file.write('#endif' + '\n')
        frames_file.close()
        frames_file = None

    frames_file_index = 0
    frames_file_count = 0

    for frame_index, frame in enumerate(frames):
        if frames_file is None:
            frames_file_path = output_folder_path + '/frames_' + str(frames_file_index) + '_data.cpp'
            print('Writing src file ' + frames_file_path + ' ...')
            frames_file = open(frames_file_path, 'w')
            frames_file.write('#include \"frames_' + str(frames_file_index) + '_data.h\"' + '\n\n')
            frames_file.write('#include \"data.h\"' + '\n\n')

        frame_tag = 'frame_' + str(frame_index)
        frames_file.write('namespace' + '\n')
        frames_file.write('{' + '\n')
        frames_file.write('    constexpr const btn::color ' + frame_tag + '_colors[] = {' + '\n')

        for frame_color in frame[0]:
            r = int(frame_color[0] / 8)
            g = int(frame_color[1] / 8)
            b = int(frame_color[2] / 8)
            frames_file.write('        btn::color(' + str(r) + ', ' + str(g) + ', ' + str(b) + '),' + '\n')

        frames_file.write('    };' + '\n\n')

        for shape_group_index, shape_group in enumerate(frame[1]):
            shape_group_tag = frame_tag + '_shape_group_' + str(shape_group_index)

            for shape_index, shape in enumerate(shape_group):
                shape_tag = shape_group_tag + '_shape_' + str(shape_index)
                frames_file.write('    constexpr const horizontal_line ' + shape_tag +
                                  '_horizontal_lines[] = {' + '\n')

                for horizontal_line in shape[3]:
                    x = horizontal_line[0]
                    y = horizontal_line[1]
                    frames_file.write('        horizontal_line(' + str(x) + ', ' + str(y) + '),' + '\n')

                frames_file.write('    };' + '\n\n')

            frames_file.write('    constexpr const shape ' + shape_group_tag + '_shapes[] = {' + '\n')

            for shape_index, shape in enumerate(shape_group):
                shape_tag = shape_group_tag + '_shape_' + str(shape_index)
                color_index = shape[0]
                start_y = shape[1]
                frames_file.write('        shape(' + shape_tag + '_horizontal_lines, ' + str(start_y) + ', ' +
                                  str(color_index) + '),' + '\n')

            frames_file.write('    };' + '\n\n')

        shape_groups = frame[1]

        if len(shape_groups) > 0:
            frames_file.write('    constexpr const shape_group ' + frame_tag + '_shape_groups[] = {' + '\n')

            for shape_group_index, shape_group in enumerate(shape_groups):
                shape_group_tag = frame_tag + '_shape_group_' + str(shape_group_index)
                frames_file.write('        shape_group(' + shape_group_tag + '_shapes),' + '\n')

            frames_file.write('    };' + '\n\n')

            frames_file.write('    constexpr const frame ' + frame_tag + '_impl(' + frame_tag + '_colors, ' +
                              frame_tag + '_shape_groups);' + '\n')
            frames_file.write('} ' + '\n\n')
        else:
            frames_file.write('    constexpr const frame ' + frame_tag + '_impl(' + frame_tag + '_colors, ' +
                              'btn::span<const shape_group>());' + '\n')
            frames_file.write('} ' + '\n\n')

        frames_file.write('const frame& ' + frame_tag + '()' + '\n')
        frames_file.write('{' + '\n')
        frames_file.write('    return ' + frame_tag + '_impl;' + '\n')
        frames_file.write('}' + '\n\n')

        frames_file_count += 1

        if frames_file_count == max_frames_per_file:
            frames_file.close()
            frames_file = None
            frames_file_index += 1
            frames_file_count = 0

    if frames_file is not None:
        frames_file.close()
        frames_file_index += 1

    with open(output_folder_path + '/data.cpp', 'w') as output_file:
        print('Writing final file ...')
        output_file.write('#include \"data.h\"' + '\n\n')

        for i in range(frames_file_index):
            output_file.write('#include \"frames_' + str(i) + '_data.h\"' + '\n')

        output_file.write('\n')
        output_file.write('namespace' + '\n')
        output_file.write('{' + '\n')
        output_file.write('    BTN_DATA_EWRAM const frame frames[] = {' + '\n')

        for frame_index, _ in enumerate(frames):
            frame_tag = 'frame_' + str(frame_index)
            output_file.write('        ' + frame_tag + '(),' + '\n')

        output_file.write('    };' + '\n')

        output_file.write('}' + '\n\n')
        output_file.write('btn::span<const frame> all_frames()' + '\n')
        output_file.write('{' + '\n')
        output_file.write('    return frames;' + '\n')
        output_file.write('}' + '\n')

    print('Output frames file written in ' + output_folder_path)
