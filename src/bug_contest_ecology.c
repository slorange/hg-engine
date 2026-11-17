#include "config.h"

#ifdef IMPLEMENT_ECOLOGY_GENERATION

#include "battle.h"
#include "bug_contest_ecology.h"
#include "constants/encounter_tables.h"
#include "constants/item.h"
#include "constants/species.h"
#include "constants/generated/ecology_compat.h"
#include "ecology/ecology_encounter.h"
#include "setencount_ecology.h"
#include "wild_level_caps.h"

#define PARK_BANK ENCDATA_D22R0101_NATIONAL_PARK
#define CONTEST_OPPONENT_ROLLS 5

static u16 ContestStatTotal(struct PartyPokemon *mon)
{
    u16 total = 0;
    u8 stat;
    // Max HP and the five battle stats are consecutive MON_DATA fields.
    for (stat = 0; stat < 6; stat++) {
        total += GetMonData(mon, MON_DATA_MAXHP + stat, NULL);
    }
    return total;
}

// Only called from overlay 2, while its vanilla Repel check remains resident.
BOOL LONG_CALL BugContest_DoesRepelSuppress(u8 level, void *encounterGen);

u32 BugContest_GenerateEcologyEncounter(FieldSystem *fsys, struct PartyPokemon *lead UNUSED,
    u32 rod UNUSED, void *encounterGen, u32 encType UNUSED, u32 battler, void *setup)
{
    struct PartyPokemon *wild;
    struct Party *party;
    u32 perfectIv = 31;
    BOOL added;
    if (setup == NULL || battler >= 4) {
        return FALSE;
    }
    party = ((struct BATTLE_PARAM *)setup)->poke_party[battler];
    if (party == NULL) {
        return FALSE;
    }
    CacheWildLevelCapFromFieldSystem(fsys);
    wild = CreateEcologyWildMon(0, 255, 32);
    if (wild == NULL) {
        return FALSE;
    }
    if (BugContest_DoesRepelSuppress(GetMonData(wild, MON_DATA_LEVEL, NULL), encounterGen)) {
        sys_FreeMemoryEz(wild);
        return FALSE;
    }
    // Vanilla contest encounters guarantee one perfect IV, not six.
    SetMonData(wild, MON_DATA_HP_IV + gf_rand() % 6, &perfectIv);
    RecalcPartyPokemonStats(wild);
    added = PokeParty_Add(party, wild);
    sys_FreeMemoryEz(wild);
    return added;
}

// Replaces InitEncounters, after vanilla has selected the five NPC identities.
void BugContest_InitEcologyEntries(BugContest *contest)
{
    struct PartyPokemon *candidate = AllocMonZeroed(contest->heapId);
    u8 i, roll;
    u8 cap = GetWildLevelCapForEncounterBank(PARK_BANK);
    u32 perfectIv = 31;
    if (candidate == NULL) {
        return;
    }
    for (i = 0; i < 5; i++) {
        contest->contestants[i].score = 0;
        for (roll = 0; roll < CONTEST_OPPONENT_ROLLS; roll++) {
            u16 species = EcologyRollSpeciesForEncounterBank(PARK_BANK, ECOLOGY_METHOD_LAND);
            BOOL babyRoll;
            u8 level = RollWildLevel(cap, &babyRoll);
            u32 personality = (u32)gf_rand() | ((u32)gf_rand() << 16);
            u16 score;
            if (species == 0) {
                species = SPECIES_CATERPIE;
            }
            // CreateMon resets the reused buffer. Random nature/IVs, zero EVs,
            // and one perfect IV match the contest's wild-mon rules.
            PokeParaSet(candidate, species, level, 32, TRUE, personality, 0, 0);
            SetMonData(candidate, MON_DATA_HP_IV + gf_rand() % 6, &perfectIv);
            ApplyWildEncounterLevelAndStage(candidate, level, babyRoll);
            score = ContestStatTotal(candidate);
            if (score > contest->contestants[i].score) {
                contest->contestants[i].data.species = GetMonData(candidate, MON_DATA_SPECIES, NULL);
                contest->contestants[i].score = score;
            }
        }
    }
    sys_FreeMemoryEz(candidate);
}

u16 BugContest_JudgeEcologyMon(BugContest *contest, struct PartyPokemon *mon)
{
    if ((contest->flags & 1) == 0 || mon == NULL) {
        return 0;
    }
    return ContestStatTotal(mon);
}

// Called after vanilla judging has set placement (the upper six flag bits).
// Keep the selected item in the retail prize field for announcement and claiming.
void BugContest_AssignPrize(BugContest *contest)
{
    static const u16 first[] = {
        ITEM_ABILITY_PATCH, ITEM_GOLD_BOTTLE_CAP, ITEM_ABILITY_CAPSULE,
    };
    static const u16 second[] = {
        ITEM_STAR_PIECE, ITEM_BOTTLE_CAP, ITEM_PP_MAX,
    };
    static const u16 third[] = {
        ITEM_NUGGET, ITEM_BIG_PEARL, ITEM_RARE_CANDY, ITEM_PP_UP,
    };
    static const u16 consolation[] = {
        ITEM_RARE_BONE, ITEM_BIG_MUSHROOM, ITEM_STARDUST,
    };
    const u16 *pool;
    u8 count;
    switch (contest->flags >> 2) {
    case 0:
        pool = first;
        count = NELEMS(first);
        break;
    case 1:
        pool = second;
        count = NELEMS(second);
        break;
    case 2:
        pool = third;
        count = NELEMS(third);
        break;
    default:
        pool = consolation;
        count = NELEMS(consolation);
        break;
    }
    contest->prize = pool[gf_rand() % count];
}

#endif
