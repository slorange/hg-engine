#include "../include/config.h"
#include "../include/fishing_rod.h"

#include "../include/bag.h"
#include "../include/constants/file.h"
#include "../include/constants/item.h"
#include "../include/constants/species.h"
#include "../include/pokedex.h"
#include "../include/pokemon.h"
#include "../include/save.h"
#include "../include/script.h"

#define FISHING_ROD_FAMILY_CAP (MAX_SPECIES_INCLUDING_FORMS + 1)

#define FLAG_GOT_OLD_ROD  117
#define FLAG_GOT_GOOD_ROD 189

static u16 sFamilyParent[FISHING_ROD_FAMILY_CAP];
static BOOL sFamiliesInitialized = FALSE;

static u16 family_find(u16 species)
{
    if (sFamilyParent[species] != species) {
        sFamilyParent[species] = family_find(sFamilyParent[species]);
    }
    return sFamilyParent[species];
}

static void family_union(u16 a, u16 b)
{
    u16 rootA = family_find(a);
    u16 rootB = family_find(b);

    if (rootA != rootB) {
        sFamilyParent[rootB] = rootA;
    }
}

static void fishing_rod_init_families(void)
{
    u32 species;
    u32 i;

    if (sFamiliesInitialized) {
        return;
    }

    for (species = 0; species < FISHING_ROD_FAMILY_CAP; species++) {
        sFamilyParent[species] = (u16)species;
    }

    for (species = 1; species <= MAX_SPECIES_INCLUDING_FORMS; species++) {
        struct Evolution evos[MAX_EVOS_PER_POKE];

        ReadWholeNarcMemberByIdPair(evos, ARC_EVOLUTIONS, species);
        for (i = 0; i < MAX_EVOS_PER_POKE; i++) {
            u16 target;

            if (evos[i].method == EVO_NONE) {
                break;
            }

            target = evos[i].target & 0x7FF;
            if (target != 0 && target < FISHING_ROD_FAMILY_CAP) {
                family_union((u16)species, target);
            }
        }
    }

    sFamiliesInitialized = TRUE;
}

static BOOL species_is_water_type(u16 species)
{
    u32 type1 = PokePersonalParaGet(species, PERSONAL_TYPE_1);
    u32 type2 = PokePersonalParaGet(species, PERSONAL_TYPE_2);

    return type1 == TYPE_WATER || type2 == TYPE_WATER;
}

static BOOL species_is_caught(void *dex, u16 species)
{
    struct Save_DexData *dexData = (struct Save_DexData *)dex;
    u32 index;
    u32 byte;
    u32 bit;

    if (species == 0) {
        return FALSE;
    }

    index = species - 1;
    byte = index >> 3;
    bit = index & 7;
    return (((const u8 *)dexData->get_flag)[byte] >> bit) & 1;
}

u16 LONG_CALL CountCaughtWaterTypeFamilies(SaveData *saveData)
{
    void *dex = SaveData_GetDexPtr(saveData);
    BOOL familySeen[FISHING_ROD_FAMILY_CAP];
    u32 species;
    u16 count = 0;

    fishing_rod_init_families();

    for (species = 0; species < FISHING_ROD_FAMILY_CAP; species++) {
        familySeen[species] = FALSE;
    }

    for (species = 1; species <= MAX_SPECIES_INCLUDING_FORMS; species++) {
        if (species_is_caught(dex, (u16)species) && species_is_water_type((u16)species)) {
            u16 root = family_find((u16)species);

            if (!familySeen[root]) {
                familySeen[root] = TRUE;
                count++;
            }
        }
    }

    return count;
}

u16 LONG_CALL FishingRod_RemainingForNextTier(SaveData *saveData)
{
    u16 count = CountCaughtWaterTypeFamilies(saveData);
    BAG_DATA *bag;

    (void)saveData;

    if (!CheckScriptFlag(FLAG_GOT_OLD_ROD)) {
        return 0;
    }

    if (!CheckScriptFlag(FLAG_GOT_GOOD_ROD)) {
        if (count >= FISHING_ROD_GOOD_FAMILIES) {
            return 0;
        }
        return FISHING_ROD_GOOD_FAMILIES - count;
    }

    bag = Sav2_Bag_get(SaveBlock2_get());
    if (Bag_HasItem(bag, ITEM_SUPER_ROD, 1, HEAPID_MAIN_HEAP)) {
        return 0;
    }

    if (count >= FISHING_ROD_SUPER_FAMILIES) {
        return 0;
    }

    return FISHING_ROD_SUPER_FAMILIES - count;
}
