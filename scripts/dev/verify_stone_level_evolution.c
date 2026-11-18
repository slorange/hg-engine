#include <assert.h>
#include <stdlib.h>
extern int puts(const char *);
extern int printf(const char *, ...);
extern int fflush(void *);
#include "stone_level_evolution.h"
#include "eevee_evolutions.h"
#include "constants/file.h"
#undef THUMB_FUNC
#define THUMB_FUNC
#include "data/Evolutions.c"

static u16 testSpecies;
static u8 testType1, testType2, testLevel;
static BOOL testEgg;
static u16 testFriendship;
static BOOL testNight, testFairyMove;
static struct TestEvolutionLocation { u32 mapId; } testLocation;
static struct { void *unused; struct TestEvolutionLocation *location; } testField = { NULL, &testLocation };
#define gFieldSysPtr (&testField)
static struct PartyPokemon testMon;
static u16 printed[8];
static int printedMessage;
static const u8 personalTypes[MAX_SPECIES_INCLUDING_FORMS + 1][2] = {
/* PERSONAL_TYPES */
};
u32 PokeFormNoPersonalParaGet(int species, int form, int parameter)
{
    assert(parameter == PERSONAL_TYPE_1 || parameter == PERSONAL_TYPE_2);
    return personalTypes[species][parameter == PERSONAL_TYPE_2];
}
u32 GetMonData(struct PartyPokemon *mon, int field, void *buffer)
{
    switch (field) {
    case MON_DATA_SPECIES: return testSpecies;
    case MON_DATA_TYPE_1: return testType1;
    case MON_DATA_TYPE_2: return testType2;
    case MON_DATA_LEVEL: return testLevel;
    case MON_DATA_IS_EGG: return testEgg;
    case MON_DATA_FRIENDSHIP: return testFriendship;
    case MON_DATA_MOVE1: return testFairyMove ? MOVE_CHARM : MOVE_TACKLE;
    default: return 0;
    }
}
struct PartyPokemon *Party_GetMonByIndex(struct Party *party, int pos) { return &testMon; }
int PokeOtherFormMonsNoGet(int species, int form) { return species; }
BOOL IsNighttime(void) { return testNight; }
u32 GetMoveData(u16 move, u32 field) { return move == MOVE_CHARM ? TYPE_FAIRY : TYPE_NORMAL; }
void ReadWholeNarcMemberByIdPair(void *data, int narc, int species)
{
    assert(narc == ARC_EVOLUTIONS);
    memcpy(data, &__data[species], sizeof(__data[species]));
}
/* REQUIREMENT_WRAPPER */

static u16 resolve(u16 usedItem)
{
    struct {
        struct Evolution entries[MAX_EVOS_PER_POKE + NELEMS(sEeveeExtraEvolutions)];
        u16 terminator;
    } table;
    struct Evolution *evoTable = table.entries;
    struct PartyPokemon *pokemon = &testMon;
    u16 target = SPECIES_NONE, heldItem = 0;
    u8 level = testLevel;
    u8 evolutionCount = PlayerEvolutionEntryCount(testSpecies);
    int i, method = 0, *method_ret = &method;
    ReadWholeNarcMemberByIdPair(&table, ARC_EVOLUTIONS, testSpecies);
    AddEeveeEvolutionEntries(testSpecies, evoTable);
    /* ITEM_RESOLUTION */
    return target;
}

static u16 resolveLevel(void)
{
    struct Evolution table[MAX_EVOS_PER_POKE + NELEMS(sEeveeExtraEvolutions)];
    struct Evolution *evoTable = table;
    struct PartyPokemon *pokemon = &testMon;
    u8 evolutionCount = PlayerEvolutionEntryCount(testSpecies), level = testLevel;
    u16 target = SPECIES_NONE, friendship = testFriendship;
    int i, method = 0, *method_ret = &method;
    ReadWholeNarcMemberByIdPair(table, ARC_EVOLUTIONS, testSpecies);
    AddEeveeEvolutionEntries(testSpecies, table);
    for (i = 0; i < evolutionCount; i++) {
        switch (table[i].method) {
        /* EEVEE_LEVEL_CASES */
        }
        if (target != SPECIES_NONE) break;
    }
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
    // A hypothetical Grass source cannot use Leaf Stone if the target loses Grass.
    struct Evolution waterDragon = { EVO_LEVEL, 40, SPECIES_KINGDRA };
    assert(StoneLevelEvolutionRequirement(ITEM_LEAF_STONE, &waterDragon) == 0);
    assert(StoneLevelEvolutionRequirement(ITEM_WATER_STONE, &waterDragon) == 33);
    assert(MAX_EVOS_PER_POKE == 9);
    assert(PlayerEvolutionEntryCount(SPECIES_EEVEE) == 16);
    assert(__data[SPECIES_EEVEE].entries[8].method == EVO_NONE);
    assert(PlayerEvolutionEntryCount(SPECIES_PIKACHU) == 9);
    setup(SPECIES_EEVEE, TYPE_NORMAL, TYPE_NORMAL, 2);
    const u16 eeveeItems[][2] = {
        { ITEM_FIRE_STONE, SPECIES_FLAREON }, { ITEM_WATER_STONE, SPECIES_VAPOREON },
        { ITEM_THUNDER_STONE, SPECIES_JOLTEON }, { ITEM_LEAF_STONE, SPECIES_LEAFEON },
        { ITEM_ICE_STONE, SPECIES_GLACEON }, { ITEM_DAWN_STONE, SPECIES_ESPEON },
        { ITEM_SUN_STONE, SPECIES_ESPEON }, { ITEM_DUSK_STONE, SPECIES_UMBREON },
        { ITEM_MOON_STONE, SPECIES_UMBREON }, { ITEM_SHINY_STONE, SPECIES_SYLVEON },
    };
    for (u8 i = 0; i < NELEMS(eeveeItems); i++) assert(resolve(eeveeItems[i][0]) == eeveeItems[i][1]);
    assert(resolve(ITEM_METAL_COAT) == SPECIES_NONE);
    testLocation.mapId = 0; testFriendship = 0;
    assert(resolveLevel() == SPECIES_NONE);
    testLevel = 100;
    assert(resolveLevel() == SPECIES_NONE); // No high-level fallback.
    testFriendship = 255; testNight = FALSE;
    assert(resolveLevel() == SPECIES_ESPEON);
    testNight = TRUE;
    assert(resolveLevel() == SPECIES_UMBREON);
    const u16 maps[][2] = { {117, SPECIES_LEAFEON}, {147, SPECIES_LEAFEON},
        {239, SPECIES_GLACEON}, {456, SPECIES_GLACEON}, {18, SPECIES_JOLTEON} };
    for (u8 i = 0; i < NELEMS(maps); i++) {
        testLocation.mapId = maps[i][0];
        testFriendship = 0;
        assert(resolveLevel() == maps[i][1]);
        testFriendship = 255;
        assert(resolveLevel() == maps[i][1]);
        testFairyMove = TRUE;
        assert(resolveLevel() == SPECIES_SYLVEON);
        testFairyMove = FALSE;
    }
    testLocation.mapId = 18; testFriendship = 0;
    assert(resolveLevel() == SPECIES_JOLTEON);
    testLocation.mapId = 0; testFriendship = 0;
    puts("PASS: Eevee 16-entry extension, ten item choices, locations, friendship, Fairy-move priority, and no level-only fallback.");
    boundary(SPECIES_CYNDAQUIL, TYPE_FIRE, TYPE_FIRE, ITEM_FIRE_STONE, 10, SPECIES_QUILAVA);
    boundary(SPECIES_QUILAVA, TYPE_FIRE, TYPE_FIRE, ITEM_FIRE_STONE, 30, SPECIES_TYPHLOSION);
    boundary(SPECIES_WARTORTLE, TYPE_WATER, TYPE_WATER, ITEM_WATER_STONE, 30, SPECIES_BLASTOISE);
    boundary(SPECIES_BULBASAUR, TYPE_GRASS, TYPE_POISON, ITEM_LEAF_STONE, 12, SPECIES_IVYSAUR);
    boundary(SPECIES_LOTAD, TYPE_WATER, TYPE_GRASS, ITEM_LEAF_STONE, 10, SPECIES_LOMBRE);
    boundary(SPECIES_LOTAD, TYPE_WATER, TYPE_GRASS, ITEM_WATER_STONE, 10, SPECIES_LOMBRE);
    boundary(SPECIES_MAGNEMITE, TYPE_ELECTRIC, TYPE_STEEL, ITEM_THUNDER_STONE, 24, SPECIES_MAGNETON);
    boundary(SPECIES_SWINUB, TYPE_ICE, TYPE_GROUND, ITEM_ICE_STONE, 17, SPECIES_PILOSWINE);
    boundary(SPECIES_SNORUNT, TYPE_ICE, TYPE_ICE, ITEM_ICE_STONE, 35, SPECIES_GLALIE);
    boundary(SPECIES_MAGNEMITE, TYPE_ELECTRIC, TYPE_STEEL, ITEM_METAL_COAT, 24, SPECIES_MAGNETON);
    boundary(SPECIES_PINECO, TYPE_BUG, TYPE_BUG, ITEM_METAL_COAT, 25, SPECIES_FORRETRESS);
    boundary(SPECIES_PRINPLUP, TYPE_WATER, TYPE_WATER, ITEM_METAL_COAT, 30, SPECIES_EMPOLEON);
    boundary(SPECIES_ARON, TYPE_STEEL, TYPE_ROCK, ITEM_METAL_COAT, 26, SPECIES_LAIRON);
    boundary(SPECIES_LAIRON, TYPE_STEEL, TYPE_ROCK, ITEM_METAL_COAT, 35, SPECIES_AGGRON);
    boundary(SPECIES_SHIELDON, TYPE_ROCK, TYPE_STEEL, ITEM_METAL_COAT, 24, SPECIES_BASTIODON);
    boundary(SPECIES_BRONZOR, TYPE_STEEL, TYPE_PSYCHIC, ITEM_METAL_COAT, 27, SPECIES_BRONZONG);
    boundary(SPECIES_GASTLY, TYPE_GHOST, TYPE_POISON, ITEM_DUSK_STONE, 20, SPECIES_HAUNTER);
    boundary(SPECIES_DUSKULL, TYPE_GHOST, TYPE_GHOST, ITEM_DUSK_STONE, 31, SPECIES_DUSCLOPS);
    boundary(SPECIES_SHUPPET, TYPE_GHOST, TYPE_GHOST, ITEM_DUSK_STONE, 31, SPECIES_BANETTE);
    boundary(SPECIES_DRIFLOON, TYPE_GHOST, TYPE_FLYING, ITEM_DUSK_STONE, 23, SPECIES_DRIFBLIM);
    // Existing elemental stones also match newly acquired target types.
    boundary(SPECIES_SEEL, TYPE_WATER, TYPE_WATER, ITEM_ICE_STONE, 28, SPECIES_DEWGONG);
    setup(SPECIES_NOSEPASS, TYPE_ROCK, TYPE_ROCK, 2);
    assert(resolve(ITEM_METAL_COAT) == SPECIES_PROBOPASS);
    assert(resolve(ITEM_THUNDER_STONE) == SPECIES_PROBOPASS);
    setup(SPECIES_ONIX, TYPE_ROCK, TYPE_GROUND, 2);
    assert(resolve(ITEM_METAL_COAT) == SPECIES_STEELIX);
    setup(SPECIES_SCYTHER, TYPE_BUG, TYPE_FLYING, 2);
    assert(resolve(ITEM_METAL_COAT) == SPECIES_SCIZOR);
    setup(SPECIES_HOUNDOUR, TYPE_DARK, TYPE_FIRE, 100);
    assert(resolve(ITEM_DUSK_STONE) == SPECIES_NONE); // Ghost acceleration, not Dark.
    setup(SPECIES_BELDUM, TYPE_STEEL, TYPE_PSYCHIC, 100);
    assert(GetStoneLevelEvolutionRequirement(&testMon, ITEM_METAL_COAT) == 0);
    assert(resolve(ITEM_METAL_COAT) == SPECIES_NONE);
    setup(SPECIES_METANG, TYPE_STEEL, TYPE_PSYCHIC, 100);
    assert(GetStoneLevelEvolutionRequirement(&testMon, ITEM_METAL_COAT) == 0);
    assert(resolve(ITEM_METAL_COAT) == SPECIES_NONE);
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
    setup(SPECIES_SNORUNT, TYPE_ICE, TYPE_ICE, 33);
    printedMessage = -1;
    PartyMenu_PrintEvoStoneCompatString(&menu, 0, 1);
    assert(printedMessage == -1);
    assert(printed[0] == 0x136 && printed[1] == 0x140);
    assert(printed[2] == 0x124 && printed[3] == 0x126 && printed[4] == 0xFFFF); // LV35
    testLevel = 35;
    PartyMenu_PrintEvoStoneCompatString(&menu, 0, 0);
    assert(printedMessage == 161);
    args.itemId = ITEM_FIRE_STONE;
    PartyMenu_PrintEvoStoneCompatString(&menu, 0, 1);
    assert(printedMessage == 162);
    args.itemId = ITEM_ICE_STONE;
    testEgg = TRUE;
    PartyMenu_PrintEvoStoneCompatString(&menu, 0, 1);
    assert(printedMessage == 162);
    puts("PASS: seven items, target types, hybrid thresholds, item-resolution boundaries, native evolutions, excluded methods, eggs, and LV35/ABLE/UNABLE labels.");
    return 0;
}

