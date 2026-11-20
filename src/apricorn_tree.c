#include "apricorn_tree.h"
#include "map_events_internal.h"
#include "save.h"

// Indexed by the saved tree's 1-based colour. Index zero is the bare tree.
const u32 gApricornTreeTags[] = {
    262, 263, 264, 265, 266, 267, 268, 269,
    [APRICORN_TYPE_PURPLE] = APRICORN_TAG_PURPLE_TREE,
    [APRICORN_TYPE_GREY] = APRICORN_TAG_GREY_TREE,
};

// Index zero falls back to red if a tree has no colour.
const u16 gApricornFruitTags[] = {
    270, 270, 271, 272, 273, 274, 275, 276,
    [APRICORN_TYPE_PURPLE] = APRICORN_TAG_PURPLE_FRUIT,
    [APRICORN_TYPE_GREY] = APRICORN_TAG_GREY_FRUIT,
};

extern BOOL LONG_CALL FieldSystem_ApricornTree_IsRipe(FieldSystem *, LocalMapObject *);

static void ShuffleApricornColours(u8 *colours, u32 count, u32 *seed)
{
    for (u32 remaining = count; remaining > 1; remaining--) {
        *seed += 0x9E3779B9u;
        u32 roll = (*seed ^ (*seed >> 16)) * 0x7FEB352Du;
        roll = (roll ^ (roll >> 15)) * 0x846CA68Bu;
        u32 other = (roll ^ (roll >> 16)) % remaining;
        u8 last = colours[remaining - 1];
        colours[remaining - 1] = colours[other];
        colours[other] = last;
    }
}

u32 ApricornTree_GetType(FieldSystem *field, LocalMapObject *tree)
{
    // Native type 6 is White, which no longer grows on trees.
    u8 colours[] = {1, 2, 3, 4, 5, 7, APRICORN_TYPE_PURPLE, APRICORN_TYPE_GREY};
    u8 bucket[NUM_APRICORN_TREE];
    u32 slot = MapObject_GetParam(tree, 0);
    u32 seed = Sav2_PlayerData_GetProfileAddr(field->savedata)->id ^ 0xA91C0A5Eu;

    if (slot >= NUM_APRICORN_TREE)
        return 1; // Red fallback for an unconfigured slot.

    // Shuffling the color order chooses which colors receive the extra trees.
    ShuffleApricornColours(colours, sizeof(colours), &seed);
    for (u32 i = 0; i < NUM_APRICORN_TREE; i++)
        bucket[i] = colours[i % sizeof(colours)];

    ShuffleApricornColours(bucket, NUM_APRICORN_TREE, &seed);
    return bucket[slot];
}

int ApricornTree_GetApricorn(FieldSystem *field, LocalMapObject *tree)
{
    return ApricornTree_GetType(field, tree) - 1;
}

BOOL ApricornTree_HasFruit(FieldSystem *field, LocalMapObject *tree)
{
    if (tree == NULL)
        return FALSE;

    u32 tag = MapObject_GetGfxID(tree);
    return ((tag >= 263 && tag <= 269) || tag == APRICORN_TAG_PURPLE_TREE || tag == APRICORN_TAG_GREY_TREE)
        && FieldSystem_ApricornTree_IsRipe(field, tree) == TRUE;
}
