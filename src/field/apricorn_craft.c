#include "apricorn_craft.h"
#include "constants/file.h"
#include "constants/item.h"

#ifndef APRICORN_CRAFT_HOST_TEST
// Imported linker symbols do not carry ELF Thumb function metadata. Force
// indirect calls so the odd function address controls instruction-set state.
extern u16 LONG_CALL Craft_GetQuantity(BAG_DATA *, u16, int) asm("Bag_GetQuantity");
extern void *LONG_CALL Craft_Copy(void *, const void *, u32) asm("memcpy");
extern u32 LONG_CALL Craft_Divide(u32, u32) asm("__aeabi_uidiv");
#else
#define Craft_GetQuantity Bag_GetQuantity
#define Craft_Copy memcpy
#define Craft_Divide(n, d) ((n) / (d))
#endif

static const struct {
    u16 apricorn;
    u16 ball;
} sCraftRecipes[] = {
    { ITEM_RED_APRICORN,    ITEM_FAST_BALL },
    { ITEM_YELLOW_APRICORN, ITEM_LEVEL_BALL },
    { ITEM_BLUE_APRICORN,   ITEM_QUICK_BALL },
    { ITEM_GREEN_APRICORN,  ITEM_FRIEND_BALL },
    { ITEM_PINK_APRICORN,   ITEM_LOVE_BALL },
    { ITEM_BLACK_APRICORN,  ITEM_DUSK_BALL },
    { ITEM_PURPLE_APRICORN, ITEM_DREAM_BALL },
    { ITEM_GREY_APRICORN,   ITEM_HEAVY_BALL },
};

u16 ApricornCraft_Exchange(BAG_DATA *bag, u32 *money, BOOL commit,
                          u16 *total, u16 *feeHundreds)
{
    u16 inBag[NELEMS(sCraftRecipes)];
    unsigned i;
    BAG_DATA *trial;
    *total = 0;
    for (i = 0; i < NELEMS(sCraftRecipes); i++) {
        inBag[i] = Craft_GetQuantity(bag, sCraftRecipes[i].apricorn, HEAPID_DEFAULT);
        *total += inBag[i];
    }
    *feeHundreds = Craft_Divide(*total + 9, 10);
    if (*total == 0)
        return APRICORN_CRAFT_EMPTY;
    if (*money < (u32)*feeHundreds * 100)
        return APRICORN_CRAFT_NO_MONEY;
    trial = sys_AllocMemory(HEAPID_DEFAULT, sizeof(*trial));
    if (trial == NULL)
        return APRICORN_CRAFT_UNAVAILABLE;
    Craft_Copy(trial, bag, sizeof(*trial));
    // Simulate the entire exchange first: no partial rewards or lost payment.
    for (i = 0; i < NELEMS(sCraftRecipes); i++) {
        u16 quantity = inBag[i];
        if (quantity && (!Bag_TakeItem(trial, sCraftRecipes[i].apricorn, quantity, HEAPID_DEFAULT)
                         || !Bag_AddItem(trial, sCraftRecipes[i].ball, quantity, HEAPID_DEFAULT))) {
            sys_FreeMemoryEz(trial);
            return APRICORN_CRAFT_NO_SPACE;
        }
    }
    if (commit) {
        Craft_Copy(bag, trial, sizeof(*bag));
        *money -= (u32)*feeHundreds * 100;
    }
    sys_FreeMemoryEz(trial);
    return APRICORN_CRAFT_OK;
}

#ifndef APRICORN_CRAFT_HOST_TEST
#include "save.h"

u16 ApricornCraft_FieldRun(void *saveData, BOOL commit, u16 *total, u16 *feeHundreds)
{
    struct PlayerProfile *profile = Sav2_PlayerData_GetProfileAddr(saveData);
    return ApricornCraft_Exchange(Sav2_Bag_get(saveData), &profile->money, commit,
                                  total, feeHundreds);
}
#endif
