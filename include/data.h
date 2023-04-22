/**
 * Copyright (c) 2020 Gustavo Valiente gustavo.valiente@protonmail.com
 * zlib License, see LICENSE file.
 */

#ifndef DATA_H
#define DATA_H

#include "bn_span.h"
#include "bn_color.h"
#include "bn_display.h"

class horizontal_line
{

public:
    uint8_t x;
    uint8_t length_minus_one: 6;
    uint8_t tiles_index: 2;

    constexpr horizontal_line(int x1, int x2) :
        x(uint8_t(x1)),
        length_minus_one(unsigned(x2 - x1))
    {
        BN_ASSERT(x1 >= 0, "Invalid x1: ", x1);
        BN_ASSERT(x2 < bn::display::width(), "Invalid x: ", x2);
        BN_ASSERT(x1 <= x2, "Invalid length: ", x1, " - ", x2);

        if(length_minus_one < 8 - 1)
        {
            tiles_index = 0;
        }
        else if(length_minus_one < 16 - 1)
        {
            tiles_index = 1;
        }
        else if(length_minus_one < 32 - 1)
        {
            tiles_index = 2;
        }
        else if(length_minus_one < 64 - 1)
        {
            tiles_index = 3;
        }
        else
        {
            BN_ERROR("Too much length: ", length_minus_one);
        }
    }
};


class shape
{

public:
    const horizontal_line* horizontal_lines;
    uint8_t horizontal_lines_count;
    uint8_t start_y;
    uint8_t tiles_index;
    uint8_t color_index;

    constexpr shape(const bn::span<const horizontal_line>& _horizontal_lines, int _start_y, int _color_index) :
        horizontal_lines(_horizontal_lines.data()),
        horizontal_lines_count(uint8_t(_horizontal_lines.size())),
        start_y(uint8_t(_start_y)),
        color_index(uint8_t(_color_index))
    {
        BN_ASSERT(! _horizontal_lines.empty(), "No horizontal lines");
        BN_ASSERT(_start_y >= 0, "Invalid start y: ", _start_y);
        BN_ASSERT(_start_y + _horizontal_lines.size() <= bn::display::height(), "Invalid end y: ",
                   _start_y, " - ", _horizontal_lines.size());
        BN_ASSERT(_color_index >= 1 && _color_index <= 15, "Invalid color index: ", _color_index);

        tiles_index = 0;

        for(int index = 0; index < horizontal_lines_count; ++index)
        {
            tiles_index = bn::max(tiles_index, uint8_t(horizontal_lines[index].tiles_index));
        }
    }
};


class shape_group
{

public:
    static const int max = 38;

    const shape* shapes;
    uint8_t shapes_count;
    uint8_t minimum_y;
    uint8_t maximum_y;

    constexpr explicit shape_group(const bn::span<const shape>& _shapes) :
        shapes(_shapes.data()),
        shapes_count(uint8_t(_shapes.size())),
        minimum_y(bn::display::height()),
        maximum_y(0)
    {
        int num_shapes = _shapes.size();
        BN_ASSERT(num_shapes, "No shapes");
        BN_ASSERT(num_shapes <= bn::display::height(), "Too much shapes: ", num_shapes);

        for(int index = 0; index < num_shapes - 1; ++index)
        {
            BN_ASSERT(_shapes[index].start_y + _shapes[index].horizontal_lines_count - 1 <
                       _shapes[index + 1].start_y, "Shapes must be sorted: ", index);
        }

        for(const shape& shape : _shapes)
        {
            minimum_y = bn::min(minimum_y, shape.start_y);
            maximum_y = bn::max(maximum_y, uint8_t(shape.start_y + shape.horizontal_lines_count));
        }
    }
};


class frame
{

public:
    const bn::color* colors;
    bn::span<const shape_group> shape_groups;

    constexpr frame(const bn::span<const bn::color>& _colors, const bn::span<const shape_group>& _shape_groups) :
        colors(_colors.data()),
        shape_groups(_shape_groups)
    {
        BN_ASSERT(_colors.size() == 16, "Invalid colors count: ", _colors.size());
        BN_ASSERT(shape_groups.size() <= shape_group::max, "Too much shape groups: ", shape_groups.size());
    }
};


[[nodiscard]] bn::span<const frame> all_frames();

#endif
