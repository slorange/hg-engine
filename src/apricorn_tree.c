#include "apricorn_tree.h"
#include "map_events_internal.h"

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

BOOL ApricornTree_HasFruit(FieldSystem *field, LocalMapObject *tree)
{
    if (tree == NULL)
        return FALSE;

    u32 tag = MapObject_GetGfxID(tree);
    return ((tag >= 263 && tag <= 269) || tag == APRICORN_TAG_PURPLE_TREE || tag == APRICORN_TAG_GREY_TREE)
        && FieldSystem_ApricornTree_IsRipe(field, tree) == TRUE;
}
