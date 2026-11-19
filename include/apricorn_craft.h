#ifndef APRICORN_CRAFT_H
#define APRICORN_CRAFT_H
#include "bag.h"

enum ApricornCraftStatus {
    APRICORN_CRAFT_OK,
    APRICORN_CRAFT_EMPTY,
    APRICORN_CRAFT_NO_MONEY,
    APRICORN_CRAFT_NO_SPACE,
    APRICORN_CRAFT_UNAVAILABLE,
};

u16 ApricornCraft_Exchange(BAG_DATA *bag, u32 *money, BOOL commit,
                          u16 *total, u16 *feeHundreds);
u16 ApricornCraft_Run(void *saveData, BOOL commit, u16 *total, u16 *feeHundreds);
#endif
