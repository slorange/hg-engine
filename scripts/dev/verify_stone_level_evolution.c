#include <assert.h>
#include <stdlib.h>
extern int puts(const char *);
extern int printf(const char *, ...);
extern int fflush(void *);
#include "stone_level_evolution.h"
#include "constants/file.h"
#undef THUMB_FUNC
#define THUMB_FUNC
#include "data/Evolutions.c"

static u16 testSpecies;
static u8 testType1, testType2, testLevel;
static BOOL testEgg;
static struct PartyPokemon testMon;
static u16 printed[8];
static int printedMessage;
u32 GetMonData(struct PartyPokemon *mon, int field, void *buffer)
{
    switch (field) {
    case MON_DATA_SPECIES: return testSpecies;
    case MON_DATA_TYPE_1: return testType1;
    case MON_DATA_TYPE_2: return testType2;
    case MON_DATA_LEVEL: return testLevel;
    case MON_DATA_IS_EGG: return testEgg;
    default: return 0;
    }
}
struct PartyPokemon *Party_GetMonByIndex(struct Party *party, int pos) { return &testMon; }
int PokeOtherFormMonsNoGet(int species, int form) { return species; }
void ReadWholeNarcMemberByIdPair(void *data, int narc, int species)
{
    assert(narc == ARC_EVOLUTIONS);
    memcpy(data, &__data[species], sizeof(__data[species]));
}
/* REQUIREMENT_WRAPPER */

static u16 resolve(u16 usedItem)
{
    EvolutionTable table;
    struct Evolution *evoTable = table.entries;
    struct PartyPokemon *pokemon = &testMon;
    u16 target = SPECIES_NONE, heldItem = 0;
    u8 level = testLevel;
    int i, method = 0, *method_ret = &method;
    ReadWholeNarcMemberByIdPair(&table, ARC_EVOLUTIONS, testSpecies);
    /* ITEM_RESOLUTION */
    return target;
}

void FillWindowPixelBuffer(void *window, u8 fill) {}
void *String_New(u32 count, u32 heap) { return calloc(1, sizeof(String) + count * 2); }
void String_Delete(void *s) { free(s); }
void CopyU16ArrayToString(String *s, const u16 *src)
{
    int i = 0;
    do { s->data[i] = src[i]; } while (src[i++] != 0xFFFF);
    s->size = i - 1;
}
String *NewString_ReadMsgData(MsgData *data, s32 message)
{
    printedMessage = message;
    return String_New(6, 12);
}
u8 AddTextPrinterParameterizedWithColor(void *window, u8 font, String *s, u32 x, u32 y, u32 speed, u32 color, void *cb)
{
    memcpy(printed, s->data, (s->size + 1) * 2);
    return 0;
}
void ScheduleWindowCopyToVram(struct Window *window) {}
/* MENU_LABEL */

static void setup(u16 species, u8 type1, u8 type2, u8 level)
{
    testSpecies = species; testType1 = type1; testType2 = type2;
    testLevel = level; testEgg = FALSE;
}
static void boundary(u16 species, u8 type1, u8 type2, u16 item, u8 required, u16 target)
{
    setup(species, type1, type2, required - 1);
    u8 got = GetStoneLevelEvolutionRequirement(&testMon, item);
    if (got != required) {
        printf("species=%u item=%u expected=%u got=%u\n", species, item, required, got);
        fflush(NULL);
    }
    assert(got == required);
    assert(resolve(item) == SPECIES_NONE);
    testLevel = required;
    assert(resolve(item) == target);
    testLevel = 100;
    assert(resolve(item) == target);
}
int main(void)
{
    boundary(SPECIES_CYNDAQUIL, TYPE_FIRE, TYPE_FIRE, ITEM_FIRE_STONE, 11, SPECIES_QUILAVA);
    boundary(SPECIES_QUILAVA, TYPE_FIRE, TYPE_FIRE, ITEM_FIRE_STONE, 27, SPECIES_TYPHLOSION);
    boundary(SPECIES_WARTORTLE, TYPE_WATER, TYPE_WATER, ITEM_WATER_STONE, 27, SPECIES_BLASTOISE);
    boundary(SPECIES_BULBASAUR, TYPE_GRASS, TYPE_POISON, ITEM_LEAF_STONE, 12, SPECIES_IVYSAUR);
    boundary(SPECIES_LOTAD, TYPE_WATER, TYPE_GRASS, ITEM_LEAF_STONE, 11, SPECIES_LOMBRE);
    boundary(SPECIES_LOTAD, TYPE_WATER, TYPE_GRASS, ITEM_WATER_STONE, 11, SPECIES_LOMBRE);
    boundary(SPECIES_MAGNEMITE, TYPE_ELECTRIC, TYPE_STEEL, ITEM_THUNDER_STONE, 23, SPECIES_MAGNETON);
    boundary(SPECIES_SWINUB, TYPE_ICE, TYPE_GROUND, ITEM_ICE_STONE, 17, SPECIES_PILOSWINE);
    boundary(SPECIES_SNORUNT, TYPE_ICE, TYPE_ICE, ITEM_ICE_STONE, 32, SPECIES_GLALIE);
    setup(SPECIES_CYNDAQUIL, TYPE_FIRE, TYPE_FIRE, 100);
    assert(resolve(ITEM_LEAF_STONE) == SPECIES_NONE);
    assert(resolve(ITEM_MOON_STONE) == SPECIES_NONE);
    setup(SPECIES_CHARIZARD, TYPE_FIRE, TYPE_FLYING, 100);
    assert(resolve(ITEM_FIRE_STONE) == SPECIES_NONE);
    setup(SPECIES_TANGELA, TYPE_GRASS, TYPE_GRASS, 100);
    assert(resolve(ITEM_LEAF_STONE) == SPECIES_NONE); // Move-known is excluded.
    setup(SPECIES_PILOSWINE, TYPE_ICE, TYPE_GROUND, 100);
    assert(resolve(ITEM_ICE_STONE) == SPECIES_NONE);
    setup(SPECIES_GROWLITHE, TYPE_FIRE, TYPE_FIRE, 2);
    assert(resolve(ITEM_FIRE_STONE) == SPECIES_ARCANINE); // Native evolution unchanged.
    setup(SPECIES_EEVEE, TYPE_NORMAL, TYPE_NORMAL, 2);
    assert(resolve(ITEM_WATER_STONE) == SPECIES_VAPOREON);
    setup(SPECIES_CYNDAQUIL, TYPE_FIRE, TYPE_FIRE, 12);
    testEgg = TRUE;
    assert(GetStoneLevelEvolutionRequirement(&testMon, ITEM_FIRE_STONE) == 0);
    assert(resolve(ITEM_FIRE_STONE) == SPECIES_NONE);
    // Render the actual party-menu function into a captured string.
    struct PartyMenu menu = {0};
    PartyMenuArgs args = {0};
    menu.args = &args;
    args.itemId = ITEM_ICE_STONE;
    setup(SPECIES_SNORUNT, TYPE_ICE, TYPE_ICE, 31);
    printedMessage = -1;
    PartyMenu_PrintEvoStoneCompatString(&menu, 0, 1);
    assert(printedMessage == -1);
    assert(printed[0] == 0x136 && printed[1] == 0x140);
    assert(printed[2] == 0x124 && printed[3] == 0x123 && printed[4] == 0xFFFF); // LV32
    testLevel = 32;
    PartyMenu_PrintEvoStoneCompatString(&menu, 0, 0);
    assert(printedMessage == 161);
    args.itemId = ITEM_FIRE_STONE;
    PartyMenu_PrintEvoStoneCompatString(&menu, 0, 1);
    assert(printedMessage == 162);
    args.itemId = ITEM_ICE_STONE;
    testEgg = TRUE;
    PartyMenu_PrintEvoStoneCompatString(&menu, 0, 1);
    assert(printedMessage == 162);
    puts("PASS: five stones, both types, ceil thresholds, item-resolution boundaries, native evolutions, excluded methods, eggs, and LV32/ABLE/UNABLE labels.");
    return 0;
}

