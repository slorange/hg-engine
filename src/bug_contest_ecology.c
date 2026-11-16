#include "config.h"

#ifdef IMPLEMENT_ECOLOGY_GENERATION

#include "battle.h"
#include "bug_contest_ecology.h"
#include "constants/encounter_tables.h"
#include "constants/species.h"
#include "ecology/ecology_compat_access.h"
#include "ecology/ecology_encounter.h"
#include "setencount_ecology.h"
#include "wild_level_caps.h"

#define PARK_BANK ENCDATA_D22R0101_NATIONAL_PARK

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

static u16 ContestEntryValue(u16 species)
{
    u16 family;
    species = WildEncounterFamilyRoot(species);
    if (!EcologyCompatSessionEnsure()) {
        return 60;
    }
    for (family = 0; family < ECOLOGY_NUM_FAMILIES; family++) {
        EcologyFamilyInfo info = ECO_FAMILY_INFO(family);
        if (info.baseSpecies == species) {
            if (info.rarity == ECOLOGY_RARITY_COMMON) {
                return 60;
            }
            return info.rarity == ECOLOGY_RARITY_NORMAL ? 80 : 100;
        }
    }
    return 60;
}

// Replaces InitEncounters, after vanilla has selected the five NPC identities.
// The cap snapshot stays valid after warping to the gatehouse for judging.
void BugContest_InitEcologyEntries(BugContest *contest)
{
    u8 i, stat;
    u8 cap = GetWildLevelCapForEncounterBank(PARK_BANK);
    contest->encounters[0].lvlmax = cap;
    for (i = 0; i < 5; i++) {
        u16 species = EcologyRollSpeciesForEncounterBank(PARK_BANK, ECOLOGY_METHOD_LAND);
        u8 level = RollWildLevel(cap);
        u16 ivTotal = 31;
        u16 score;
        if (species == 0) {
            species = SPECIES_CATERPIE;
        }
        score = ContestEntryValue(species) + level * 100 / cap;
        for (stat = 1; stat < 6; stat++) {
            ivTotal += gf_rand() % 32;
        }
        score += ivTotal * 100 / 186;
        score += 50 + gf_rand() % 51;
        contest->contestants[i].data.species = WildEncounterStageAtLevel(species, level);
        contest->contestants[i].score = score;
    }
}

u16 BugContest_JudgeEcologyMon(BugContest *contest, struct PartyPokemon *mon)
{
    u16 score, ivTotal = 0;
    u32 cap, levelScore, maxHp;
    u8 i;
    if ((contest->flags & 1) == 0 || mon == NULL) {
        return 0;
    }
    cap = contest->encounters[0].lvlmax;
    if (cap == 0) {
        cap = GetWildLevelCapForEncounterBank(PARK_BANK);
    }
    score = ContestEntryValue(GetMonData(mon, MON_DATA_SPECIES, NULL));
    levelScore = GetMonData(mon, MON_DATA_LEVEL, NULL) * 100 / cap;
    score += levelScore > 100 ? 100 : levelScore;
    for (i = 0; i < 6; i++) {
        ivTotal += GetMonData(mon, MON_DATA_HP_IV + i, NULL);
    }
    score += ivTotal * 100 / 186;
    maxHp = GetMonData(mon, MON_DATA_MAXHP, NULL);
    if (maxHp != 0) {
        score += GetMonData(mon, MON_DATA_HP, NULL) * 100 / maxHp;
    }
    return score;
}

#endif
