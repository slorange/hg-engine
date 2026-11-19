#include "field_pickups.h"

#include "apricorn_craft.h"
#include "constants/file.h"
#include "constants/item.h"
#include "map_events_internal.h"

typedef struct {
    u16 firstItem;
    u16 lastItem;
    u8 weight;
    u8 minQuantity;
    u8 maxQuantity;
} PickupEntry;

typedef struct {
    const PickupEntry *entries;
    u8 count;
    u8 weight;
} PickupCategory;

#define RANGE(first, last, weight, min, max) { first, last, weight, min, max }
#define BUNDLE(item, weight, min, max) RANGE(item, item, weight, min, max)
#define SINGLE(item) BUNDLE(item, 1, 1, 1)
#define CATEGORY(entries, weight) { entries, sizeof(entries) / sizeof((entries)[0]), weight }

static const PickupEntry sTreasures[] = {
    SINGLE(ITEM_TINY_MUSHROOM), SINGLE(ITEM_BIG_MUSHROOM), SINGLE(ITEM_PEARL),
    SINGLE(ITEM_BIG_PEARL), SINGLE(ITEM_STARDUST), SINGLE(ITEM_STAR_PIECE),
    SINGLE(ITEM_NUGGET), SINGLE(ITEM_HEART_SCALE),
};

// Evolution items with at least three distinct users in the evolution data.
static const PickupEntry sEvolutionItems[] = {
    SINGLE(ITEM_FIRE_STONE), SINGLE(ITEM_THUNDER_STONE), SINGLE(ITEM_WATER_STONE),
    SINGLE(ITEM_LEAF_STONE), SINGLE(ITEM_ICE_STONE), SINGLE(ITEM_DUSK_STONE),
    SINGLE(ITEM_METAL_COAT),
};

static const PickupEntry sHeldItems[] = {
    SINGLE(ITEM_SILK_SCARF), SINGLE(ITEM_CHARCOAL), SINGLE(ITEM_MYSTIC_WATER),
    SINGLE(ITEM_MAGNET), SINGLE(ITEM_MIRACLE_SEED), SINGLE(ITEM_NEVER_MELT_ICE),
    SINGLE(ITEM_BLACK_BELT), SINGLE(ITEM_POISON_BARB), SINGLE(ITEM_SOFT_SAND),
    SINGLE(ITEM_SHARP_BEAK), SINGLE(ITEM_TWISTED_SPOON), SINGLE(ITEM_SILVER_POWDER),
    SINGLE(ITEM_HARD_STONE), SINGLE(ITEM_SPELL_TAG), SINGLE(ITEM_DRAGON_FANG),
    SINGLE(ITEM_BLACK_GLASSES), SINGLE(ITEM_METAL_COAT), SINGLE(ITEM_FAIRY_FEATHER),
};

// Weight each range by its size so each TM or berry is equally likely.
#define UNIFORM_RANGE(first, last) RANGE(first, last, (last) - (first) + 1, 1, 1)

static const PickupEntry sTms[] = {
    UNIFORM_RANGE(ITEM_TM001, ITEM_TM092),
};

static const PickupEntry sBalls[] = {
    BUNDLE(ITEM_ULTRA_BALL, 2, 3, 5), BUNDLE(ITEM_NET_BALL, 1, 2, 3),
    BUNDLE(ITEM_REPEAT_BALL, 1, 2, 3), BUNDLE(ITEM_TIMER_BALL, 1, 2, 3),
    BUNDLE(ITEM_FAST_BALL, 1, 2, 3), BUNDLE(ITEM_LEVEL_BALL, 1, 2, 3),
    BUNDLE(ITEM_HEAVY_BALL, 1, 2, 3), BUNDLE(ITEM_LOVE_BALL, 1, 2, 3),
    BUNDLE(ITEM_FRIEND_BALL, 1, 2, 3),
    BUNDLE(ITEM_DREAM_BALL, 1, 2, 3), BUNDLE(ITEM_QUICK_BALL, 1, 2, 3),
    BUNDLE(ITEM_DUSK_BALL, 1, 2, 3),
};

static const PickupEntry sBerries[] = {
    UNIFORM_RANGE(ITEM_CHERI_BERRY, ITEM_SITRUS_BERRY),
    UNIFORM_RANGE(ITEM_POMEG_BERRY, ITEM_TAMATO_BERRY),
    UNIFORM_RANGE(ITEM_OCCA_BERRY, ITEM_ROWAP_BERRY),
};

static const PickupEntry sUtility[] = {
    SINGLE(ITEM_REPEL), SINGLE(ITEM_SUPER_REPEL), SINGLE(ITEM_MAX_REPEL),
    SINGLE(ITEM_ESCAPE_ROPE),
};

static const PickupEntry sApricorns[] = {
    RANGE(ITEM_RED_APRICORN, ITEM_BLACK_APRICORN, 1, 3, 5),
};

static const PickupEntry sUpgrades[] = {
    BUNDLE(ITEM_RARE_CANDY, 24, 1, 1), BUNDLE(ITEM_PP_UP, 12, 1, 1),
    BUNDLE(ITEM_PP_MAX, 5, 1, 1), RANGE(ITEM_HP_UP, ITEM_CALCIUM, 18, 1, 1),
    BUNDLE(ITEM_ZINC, 3, 1, 1),
    BUNDLE(ITEM_BOTTLE_CAP, 10, 1, 1), BUNDLE(ITEM_GOLD_BOTTLE_CAP, 5, 1, 1),
    RANGE(ITEM_LONELY_MINT, ITEM_SERIOUS_MINT, 18, 1, 1),
    BUNDLE(ITEM_ABILITY_CAPSULE, 8, 1, 1), BUNDLE(ITEM_ABILITY_PATCH, 4, 1, 1),
};

static const PickupCategory sCategories[] = {
    CATEGORY(sTreasures, 20),
    CATEGORY(sEvolutionItems, 15),
    CATEGORY(sHeldItems, 10),
    CATEGORY(sTms, 10),
    CATEGORY(sBalls, 10),
    CATEGORY(sBerries, 0),
    CATEGORY(sUtility, 0),
    CATEGORY(sApricorns, 15),
    CATEGORY(sUpgrades, 20),
};

// A fixed integer mixer keeps a spot's reward stable across reloads and retries.
static u32 PickupRoll(u32 value)
{
    value = (value ^ (value >> 16)) * 0x7FEB352Du;
    value = (value ^ (value >> 15)) * 0x846CA68Bu;
    return value ^ (value >> 16);
}

static void PickReward(u32 seed, u16 flag, u16 *item, u16 *quantity)
{
    u32 key = seed ^ ((u32)flag * 0x9E3779B9u);
    u32 total = 0;
    for (u32 i = 0; i < sizeof(sCategories) / sizeof(sCategories[0]); i++)
        total += sCategories[i].weight;
    u32 roll = PickupRoll(key) % total;
    const PickupCategory *category = sCategories;
    while (roll >= category->weight) {
        roll -= category->weight;
        category++;
    }

    total = 0;
    for (u32 i = 0; i < category->count; i++)
        total += category->entries[i].weight;
    roll = PickupRoll(key + 1) % total;
    const PickupEntry *entry = category->entries;
    while (roll >= entry->weight) {
        roll -= entry->weight;
        entry++;
    }
    *item = entry->firstItem + PickupRoll(key + 2) % (entry->lastItem - entry->firstItem + 1);
    *quantity = entry->minQuantity + PickupRoll(key + 3) % (entry->maxQuantity - entry->minQuantity + 1);
}

void FieldPickup_Run(SCRIPTCONTEXT *ctx, u16 action)
{
    FieldSystem *field = ctx->fsys;
    void *save = field->savedata;
    u16 *item = GetVarPointer(field, 0x8004);
    u16 *quantity = GetVarPointer(field, 0x8005);
    u16 *result = GetVarPointer(field, 0x800C);

    if (action != FIELD_PICKUP_GRANT) {
        u16 flag = 0;
        if (action == FIELD_PICKUP_CHECK_HIDDEN) {
            flag = *GetVarPointer(field, 0x8006);
        } else {
            LocalMapObject **target = FieldSysGetAttrAddr(field, SCRIPTENV_LAST_TALKED);
            if (target != NULL && *target != NULL)
                flag = (*target)->evFlagId;
        }
        if (flag != 0)
            PickReward(Sav2_PlayerData_GetProfileAddr(save)->id, flag, item, quantity);
    }

    if (*item >= ITEM_RED_APRICORN && *item <= ITEM_BLACK_APRICORN) {
        u8 *count = &ApricornCraft_GetBox(save)[*item - ITEM_RED_APRICORN];
        *result = *count + *quantity <= 99;
        if (*result && action == FIELD_PICKUP_GRANT)
            *count += *quantity;
        return;
    }

    BAG_DATA *bag = Sav2_Bag_get(save);
    if (action == FIELD_PICKUP_GRANT)
        *result = Bag_AddItem(bag, *item, *quantity, HEAPID_WORLD);
    else
        *result = Bag_HasSpaceForItem(bag, *item, *quantity, HEAPID_WORLD);
}
