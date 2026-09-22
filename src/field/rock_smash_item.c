#include "debug.h"
#include "types.h"

#include "rock_smash_item.h"

#include "constants/maps.h"

#include "map_events_internal.h"
#include "script.h"

/*
Each vanilla map header (NARC a253) has 2 bytes for odds (out of 100) to receive an item from a rock
and 2 bytes for a table index. Table indices are ignored for item choice; all locations use RockSmashItemPool.
DrawRockSmashIdx picks a uniform index into that pool.
Per-map item odds in NARC a253 are ignored; ROCK_SMASH_ITEM_ODDS_PERCENT is used instead.
*/
#define ROCK_SMASH_ITEM_ODDS_PERCENT 80

static const u16 RockSmashItemPool[] = {
    ITEM_RED_SHARD,
    ITEM_BLUE_SHARD,
    ITEM_YELLOW_SHARD,
    ITEM_GREEN_SHARD,
    ITEM_PEARL,
    ITEM_BIG_PEARL,
    ITEM_STARDUST,
    ITEM_STAR_PIECE,
    ITEM_NUGGET,
    ITEM_HEART_SCALE,
    ITEM_ROOT_FOSSIL,
    ITEM_CLAW_FOSSIL,
    ITEM_HELIX_FOSSIL,
    ITEM_DOME_FOSSIL,
    ITEM_OLD_AMBER,
    ITEM_ARMOR_FOSSIL,
    ITEM_SKULL_FOSSIL,
    ITEM_RARE_BONE,
    ITEM_EVERSTONE,
    ITEM_ICY_ROCK,
    ITEM_SMOOTH_ROCK,
    ITEM_HEAT_ROCK,
    ITEM_DAMP_ROCK,
    ITEM_SUN_STONE,
    ITEM_MOON_STONE,
    ITEM_FIRE_STONE,
    ITEM_THUNDER_STONE,
    ITEM_WATER_STONE,
    ITEM_LEAF_STONE,
    ITEM_SHINY_STONE,
    ITEM_DUSK_STONE,
    ITEM_DAWN_STONE,
    ITEM_KINGS_ROCK,
    ITEM_DEEP_SEA_TOOTH,
    ITEM_DEEP_SEA_SCALE,
    ITEM_METAL_COAT,
    ITEM_HARD_STONE,
};

#define NUM_ROCK_SMASH_ITEMS NELEMS(RockSmashItemPool)

// List of abilities that increase the odds (out of 100) to receive an item from a rock and their percentage increases.
const RockSmashAbilityOdds RockSmashAbilityOddsTable[] = {
    { ABILITY_SUCTION_CUPS, 5 },
    { ABILITY_MAGNET_PULL, 5 },
    { ABILITY_KEEN_EYE, 5 },
};

u32 DetermineRockSmashItem(u32 tableIndex, u32 itemIndex)
{
    if (tableIndex >= NUM_ROCK_SMASH_TABLES) {
        return ITEM_NONE;
    }

    if (itemIndex >= NUM_ROCK_SMASH_ITEMS) {
        itemIndex = NUM_ROCK_SMASH_ITEMS - 1;
    }

    return RockSmashItemPool[itemIndex];
}

BOOL LONG_CALL CheckRockSmashItemDrop(FieldSystem *fieldSystem, RockSmashItemCheckWork *env);
int LONG_CALL DrawRockSmashIdx(FieldSystem *fieldSystem);

BOOL LONG_CALL CheckRockSmashItemDrop(FieldSystem *fieldSystem, RockSmashItemCheckWork *env)
{
    int ability;
    RockSmashMapData data;

    int mapID = fieldSystem->location->mapId;
    if (mapID < MAP_ID_MAX) {
        // Fills data with base odds and table ID.
        ReadWholeNarcMemberByIdPair(&data, 255, mapID); // NARC_a_2_5_3
    } else {
        // It's definitely easier to store that here for now with custom maps.
        switch (mapID) {
        default:
            data.odds = 0;
            data.table = ROCK_SMASH_TABLE_DEFAULT;
            break;
        }
    }

    if (data.table >= NUM_ROCK_SMASH_TABLES) {
        return FALSE;
    }

    int odds = ROCK_SMASH_ITEM_ODDS_PERCENT;

    int partySlot = 0;
    struct Party *party = SaveData_GetPlayerPartyPtr(fieldSystem->savedata);
#ifdef ENTIRE_PARTY_AFFECTS_ROCK_SMASH
    for (; partySlot < party->count; partySlot++) {
#endif
        struct PartyPokemon *mon = Party_GetMonByIndex(party, partySlot);
        if (GetMonData(mon, MON_DATA_IS_EGG, NULL) == FALSE) {
            ability = GetMonData(mon, MON_DATA_ABILITY, NULL);
        } else {
            ability = NUM_ABILITIES;
        }
        env->ability = ability;

        for (u32 i = 0; i < NELEMS(RockSmashAbilityOddsTable); i++) {
            if (ability == RockSmashAbilityOddsTable[i].ability) {
                odds += RockSmashAbilityOddsTable[i].odds;
                break;
            }
        }
#ifdef ENTIRE_PARTY_AFFECTS_ROCK_SMASH
    }
#endif

    if (env->followMonKnowsHM) {
        odds += 5;
    }

    if (odds > 100) {
        odds = 100;
    } else if (odds <= 0) {
        return FALSE;
    }

    if (gf_rand() % 100 < odds) {
        env->rockSmash = data;
        return TRUE;
    }
    return FALSE;
}

int LONG_CALL DrawRockSmashIdx(UNUSED FieldSystem *fieldSystem)
{
    return gf_rand() % NUM_ROCK_SMASH_ITEMS;
}
