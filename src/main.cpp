/**
 * Copyright (c) 2020 Gustavo Valiente gustavo.valiente@protonmail.com
 * zlib License, see LICENSE file.
 */

#include "btn_core.h"

#include "btn_music.h"
#include "btn_keypad.h"
#include "btn_sprite_ptr.h"
#include "btn_green_swap.h"
#include "btn_bg_palettes.h"
#include "btn_music_items.h"
#include "btn_regular_bg_ptr.h"
#include "btn_sprite_tiles_ptr.h"
#include "btn_sprite_palette_ptr.h"
#include "btn_sprite_text_generator.h"
#include "btn_sprite_items_texture_8.h"
#include "btn_sprite_items_texture_16.h"
#include "btn_sprite_items_texture_32.h"
#include "btn_sprite_items_texture_64.h"
#include "btn_regular_bg_items_border.h"
#include "variable_8x16_sprite_font.h"
#include "data.h"
#include "shape_group_sprite.h"

#include "../../butano/hw/include/btn_hw_hdma.h"
#include "../../butano/hw/include/btn_hw_sprites.h"

namespace
{
    btn::color bw_color(btn::color color)
    {
        int value = (color.red() + color.green() + color.blue()) / 3;
        return btn::color(value, value, value);
    }

    void show_intro()
    {
        btn::bg_palettes::set_transparent_color(btn::color(16, 16, 16));

        btn::sprite_text_generator text_generator(variable_8x16_sprite_font);
        text_generator.set_center_alignment();

        int text_y = -btn::display::height() / 2;
        int text_y_margin = 15;
        text_y += text_y_margin;

        auto text_1 = text_generator.generate<16>(0, text_y, "G B A - N I C C C");
        text_y += text_y_margin * 2;

        auto text_2 = text_generator.generate<16>(0, text_y, "GBA port of the STNICCC 2000 demo");
        text_y += text_y_margin;

        auto text_3 = text_generator.generate<16>(0, text_y, "with 60FPS and music :)");
        text_y += text_y_margin * 2;

        auto text_4 = text_generator.generate<16>(0, text_y, "Press A to enable an antialiased mode");
        text_y += text_y_margin * 2;

        auto text_5 = text_generator.generate<16>(0, text_y, "Made by GValiente");
        text_y += text_y_margin;

        auto text_6 = text_generator.generate<16>(0, text_y, "https://github.com/GValiente");
        text_y += text_y_margin;

        while(! btn::keypad::a_pressed())
        {
            btn::core::update();
        }
    }

    void show_demo()
    {
        btn::regular_bg_ptr border = btn::regular_bg_items::border.create_bg(0, 0);
        border.set_priority(0);
        btn::music_items::chcknbnk.play();

        btn::sprite_palette_ptr sprite_palettes[] = {
            btn::sprite_items::texture_8.palette_item().create_new_palette(),
            btn::sprite_items::texture_8.palette_item().create_new_palette(),
            btn::sprite_items::texture_8.palette_item().create_new_palette(),
            btn::sprite_items::texture_8.palette_item().create_new_palette(),
            btn::sprite_items::texture_8.palette_item().create_new_palette(),
            btn::sprite_items::texture_8.palette_item().create_new_palette(),
            btn::sprite_items::texture_8.palette_item().create_new_palette(),
            btn::sprite_items::texture_8.palette_item().create_new_palette(),
            btn::sprite_items::texture_8.palette_item().create_new_palette(),
            btn::sprite_items::texture_8.palette_item().create_new_palette(),
            btn::sprite_items::texture_8.palette_item().create_new_palette(),
            btn::sprite_items::texture_8.palette_item().create_new_palette(),
            btn::sprite_items::texture_8.palette_item().create_new_palette(),
            btn::sprite_items::texture_8.palette_item().create_new_palette(),
            btn::sprite_items::texture_8.palette_item().create_new_palette(),
        };

        const int sprite_palette_ids[] = {
            0,
            sprite_palettes[0].id(),
            sprite_palettes[1].id(),
            sprite_palettes[2].id(),
            sprite_palettes[3].id(),
            sprite_palettes[4].id(),
            sprite_palettes[5].id(),
            sprite_palettes[6].id(),
            sprite_palettes[7].id(),
            sprite_palettes[8].id(),
            sprite_palettes[9].id(),
            sprite_palettes[10].id(),
            sprite_palettes[11].id(),
            sprite_palettes[12].id(),
            sprite_palettes[13].id(),
            sprite_palettes[14].id(),
        };

        btn::sprite_tiles_ptr sprite_tiles[] = {
            btn::sprite_items::texture_8.tiles_item().create_new_tiles(),
            btn::sprite_items::texture_16.tiles_item().create_new_tiles(),
            btn::sprite_items::texture_32.tiles_item().create_new_tiles(),
            btn::sprite_items::texture_64.tiles_item().create_new_tiles(),
        };

        const int sprite_tiles_ids[] = {
            sprite_tiles[0].id(),
            sprite_tiles[1].id(),
            sprite_tiles[2].id(),
            sprite_tiles[3].id(),
        };

        using hdma_source_array = btn::array<uint16_t, btn::display::height() * 4 * shape_group::max>;
        btn::unique_ptr<hdma_source_array> hdma_source_a(new hdma_source_array());
        btn::unique_ptr<hdma_source_array> hdma_source_b(new hdma_source_array());
        uint16_t* hdma_source_data = hdma_source_a->data();
        bool bw_mode = false;
        btn::core::update();

        for(const frame& frame : all_frames())
        {
            if(btn::keypad::a_pressed())
            {
                bw_mode = ! bw_mode;
                btn::green_swap::set_enabled(bw_mode);
            }

            btn::color colors[16];

            if(bw_mode)
            {
                btn::bg_palettes::set_transparent_color(bw_color(frame.colors[0]));

                for(int color_index = 1; color_index < 16; ++color_index)
                {
                    colors[1] = bw_color(frame.colors[color_index]);
                    sprite_palettes[color_index - 1].set_colors(colors);
                }
            }
            else
            {
                btn::bg_palettes::set_transparent_color(frame.colors[0]);

                for(int color_index = 1; color_index < 16; ++color_index)
                {
                    colors[1] = frame.colors[color_index];
                    sprite_palettes[color_index - 1].set_colors(colors);
                }
            }

            shape_group_sprite::draw(frame.shape_groups.data(), frame.shape_groups.size(),
                                     sprite_tiles_ids, sprite_palette_ids, hdma_source_data);

            btn::core::update();
            btn::hw::hdma::start(hdma_source_data, 4 * shape_group::max,
                                 &btn::hw::sprites::vram()[128 - shape_group::max].attr0);

            if(hdma_source_data == hdma_source_a->data())
            {
                hdma_source_data = hdma_source_b->data();
            }
            else
            {
                hdma_source_data = hdma_source_a->data();
            }
        }

        shape_group_sprite::draw(nullptr, 0, sprite_tiles_ids, sprite_palette_ids, hdma_source_data);

        btn::core::update();
        btn::hw::hdma::start(hdma_source_data, 4 * shape_group::max,
                             &btn::hw::sprites::vram()[128 - shape_group::max].attr0);

        btn::core::update();

        btn::hw::hdma::stop();
        btn::music::stop();
        btn::green_swap::set_enabled(false);
    }
}

int main()
{
    btn::core::init();

    while(true)
    {
        show_intro();
        show_demo();
    }
}
