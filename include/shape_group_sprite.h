/**
 * Copyright (c) 2020 Gustavo Valiente gustavo.valiente@protonmail.com
 * zlib License, see LICENSE file.
 */

#ifndef SHAPE_GROUP_SPRITE_H
#define SHAPE_GROUP_SPRITE_H

#include "btn_common.h"

class shape_group;

namespace shape_group_sprite
{
    BTN_CODE_IWRAM void draw(const shape_group* shape_groups_ptr, int shape_groups_count,
                             const int* tiles_ids, const int* palette_ids, uint16_t* hdma_source);
}

#endif
