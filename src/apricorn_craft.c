#include "apricorn_craft.h"
#include "constants/file.h"
#include "constants/item.h"

// Same colour order and mapping as Kurt / ApricornBox_GetKurtBall.
static const u16 sCraftBalls[7] = {
    ITEM_LEVEL_BALL, ITEM_MOON_BALL, ITEM_LURE_BALL, ITEM_FRIEND_BALL,
    ITEM_LOVE_BALL, ITEM_FAST_BALL, ITEM_HEAVY_BALL,
};

u16 ApricornCraft_Exchange(BAG_DATA *bag, u8 *box, u32 *money, BOOL commit,
                          u16 *total, u16 *feeHundreds)
{
    u16 inBag[7];
    unsigned i;
    BAG_DATA *trial;
    *total = 0;
    for (i = 0; i < 7; i++) {
        inBag[i] = Bag_GetQuantity(bag, ITEM_RED_APRICORN + i, HEAPID_DEFAULT);
        *total += inBag[i] + box[i];
    }
    *feeHundreds = (*total + 9) / 10;
    if (*total == 0)
        return APRICORN_CRAFT_EMPTY;
    if (*money < (u32)*feeHundreds * 100)
        return APRICORN_CRAFT_NO_MONEY;
    trial = sys_AllocMemory(HEAPID_DEFAULT, sizeof(*trial));
    if (trial == NULL)
        return APRICORN_CRAFT_UNAVAILABLE;
    *trial = *bag;
    // Simulate the entire exchange first: no partial rewards or lost payment.
    for (i = 0; i < 7; i++) {
        u16 quantity = inBag[i] + box[i];
        if (quantity > BAG_SLOT_QUANTITY_MAX
            || (inBag[i] && !Bag_TakeItem(trial, ITEM_RED_APRICORN + i, inBag[i], HEAPID_DEFAULT))
            || (quantity && !Bag_AddItem(trial, sCraftBalls[i], quantity, HEAPID_DEFAULT))) {
            sys_FreeMemoryEz(trial);
            return APRICORN_CRAFT_NO_SPACE;
        }
    }
    if (commit) {
        *bag = *trial;
        // Only the first seven bytes are colour counts. Leave Kurt's pending
        // order, Aprijuice, and all other Apricorn Box fields intact.
        for (i = 0; i < 7; i++)
            box[i] = 0;
        *money -= (u32)*feeHundreds * 100;
    }
    sys_FreeMemoryEz(trial);
    return APRICORN_CRAFT_OK;
}

#ifndef APRICORN_CRAFT_HOST_TEST
#include "save.h"
extern u8 *LONG_CALL ApricornCraft_GetBox(void *saveData);

u16 ApricornCraft_Run(void *saveData, BOOL commit, u16 *total, u16 *feeHundreds)
{
    struct PlayerProfile *profile = Sav2_PlayerData_GetProfileAddr(saveData);
    return ApricornCraft_Exchange(Sav2_Bag_get(saveData), ApricornCraft_GetBox(saveData),
                                  &profile->money, commit, total, feeHundreds);
}
#endif
