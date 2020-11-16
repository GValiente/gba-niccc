/**
 * Copyright (c) 2020 Gustavo Valiente gustavo.valiente@protonmail.com
 * zlib License, see LICENSE file.
 */

#include "shape_group_sprite.h"

#include "bn_sprite_items_texture_8.h"
#include "bn_sprite_items_texture_16.h"
#include "bn_sprite_items_texture_32.h"
#include "bn_sprite_items_texture_64.h"
#include "data.h"

#include "../../butano/hw/include/bn_hw_sprites.h"

void shape_group_sprite::draw(const shape_group* shape_groups_ptr, int shape_groups_count,
                              const int* tiles_ids, const int* palette_ids, uint16_t* hdma_source)
{
    bn::hw::sprites::handle_type base_sprite_handles[4];
    bn::hw::sprites::setup_regular(bn::sprite_items::texture_8.shape_size(), tiles_ids[0], 0,
                                    bn::sprite_items::texture_8.palette_item().bpp_mode(), false,
                                    base_sprite_handles[0]);
    bn::hw::sprites::setup_regular(bn::sprite_items::texture_16.shape_size(), tiles_ids[1], 0,
                                    bn::sprite_items::texture_16.palette_item().bpp_mode(), false,
                                    base_sprite_handles[1]);
    bn::hw::sprites::setup_regular(bn::sprite_items::texture_32.shape_size(), tiles_ids[2], 0,
                                    bn::sprite_items::texture_32.palette_item().bpp_mode(), false,
                                    base_sprite_handles[2]);
    bn::hw::sprites::setup_regular(bn::sprite_items::texture_64.shape_size(), tiles_ids[3], 0,
                                    bn::sprite_items::texture_64.palette_item().bpp_mode(), false,
                                    base_sprite_handles[3]);

    for(int shape_group_index = 0; shape_group_index < shape_groups_count; ++shape_group_index)
    {
        const shape_group& shape_group = shape_groups_ptr[shape_group_index];
        uint16_t* sprite_hdma_source = hdma_source + (shape_group_index * 4);
        int current_y = 0;

        for(int shape_index = 0, shape_limit = shape_group.shapes_count; shape_index < shape_limit; ++shape_index)
        {
            const shape& shape = shape_group.shapes[shape_index];
            int shape_start_y = shape.start_y;

            while(current_y < shape_start_y)
            {
                bn::hw::sprites::hide_and_destroy(sprite_hdma_source[0]);

                sprite_hdma_source += shape_group::max * 4;
                ++current_y;
            }

            bn::hw::sprites::handle_type& base_sprite_handle = base_sprite_handles[shape.tiles_index];
            bn::hw::sprites::set_palette(palette_ids[shape.color_index], base_sprite_handle);

            for(int line_index = 0, line_limit = shape.horizontal_lines_count; line_index < line_limit; ++line_index)
            {
                const horizontal_line& line = shape.horizontal_lines[line_index];
                sprite_hdma_source[0] = base_sprite_handle.attr0;
                bn::hw::sprites::set_y(current_y - line.length_minus_one + 1, sprite_hdma_source[0]);
                sprite_hdma_source[1] = base_sprite_handle.attr1;
                bn::hw::sprites::set_x(line.x, sprite_hdma_source[1]);
                sprite_hdma_source[2] = base_sprite_handle.attr2;

                sprite_hdma_source += shape_group::max * 4;
                ++current_y;
            }
        }

        while(current_y < bn::display::height())
        {
            bn::hw::sprites::hide_and_destroy(sprite_hdma_source[0]);

            sprite_hdma_source += shape_group::max * 4;
            ++current_y;
        }
    }

    for(int shape_group_index = shape_groups_count; shape_group_index < shape_group::max; ++shape_group_index)
    {
        uint16_t* sprite_hdma_source = hdma_source + (shape_group_index * 4);

        for(int index = 0; index < bn::display::height(); ++index)
        {
            bn::hw::sprites::hide_and_destroy(sprite_hdma_source[0]);

            sprite_hdma_source += shape_group::max * 4;
        }
    }
}
