#include "config.h"

#ifdef IMPLEMENT_ECOLOGY_GENERATION

#include "battle.h"
#include "constants/file.h"
#include "constants/species.h"
#include "encounter.h"
#include "pokemon.h"
#include "setencount_ecology.h"
#include "wild_encounter_finalize.h"

extern u32 space_for_setmondata;

#define WILD_PLACEHOLDER_LEVEL 5

static u32 WildPlaceholderPersonality(void)
{
    return gf_rand() | (gf_rand() << 16);
}

struct PartyPokemon *CreateEcologyWildMon(u32 encounterType, u32 rodType, u32 ivs)
{
    struct PartyPokemon *wild = AllocMonZeroed(HEAPID_WORLD);
    if (wild == NULL) {
        return NULL;
    }
    space_for_setmondata = 0;
    PokeParaSet(wild, SPECIES_WOOLOO, WILD_PLACEHOLDER_LEVEL, ivs, TRUE,
                WildPlaceholderPersonality(), 0, 0);
    WildEncounterFinalizeForEncount(wild, SPECIES_WOOLOO, encounterType, rodType);
    ChangeToBattleForm(wild);
    return wild;
}

// leadMon is the player's party lead (read-only in vanilla, used for ability checks).
// The wild mon must be built in its own buffer; writing to leadMon clobbers the save party.
u32 SetEncountData_Ecology(
    struct PartyPokemon *leadMon UNUSED,
    u32 rodType,
    void *encInfo UNUSED,
    void *encArea UNUSED,
    u32 encounterType,
    u32 battler,
    void *bw)
{
    struct BATTLE_PARAM *battleParam;
    struct Party *party;
    struct PartyPokemon *wild;
    BOOL added;

    if (bw == NULL) {
        return FALSE;
    }

    if (battler >= 4) {
        return FALSE;
    }

    battleParam = (struct BATTLE_PARAM *)bw;
    party = battleParam->poke_party[battler];
    if (party == NULL) {
        return FALSE;
    }

    wild = CreateEcologyWildMon(encounterType, rodType, 31);
    if (wild == NULL) {
        return FALSE;
    }

    added = PokeParty_Add(party, wild);
    sys_FreeMemoryEz(wild);

    return added ? TRUE : FALSE;
}

#endif
