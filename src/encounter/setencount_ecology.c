#include "config.h"

#ifdef IMPLEMENT_ECOLOGY_GENERATION

#include "battle.h"
#include "constants/ability.h"
#include "constants/file.h"
#include "constants/species.h"
#include "encounter.h"
#include "pokemon.h"
#include "setencount_ecology.h"
#include "wild_encounter_finalize.h"

extern u32 space_for_setmondata;

BOOL LONG_CALL BugContest_DoesRepelSuppress(u8 level, void *encounterGen);
u16 WildEncounterFinalizeWithLead(struct PartyPokemon *pp, u16 vanillaTableSpecies, u32 encounterType,
                                  u32 rodType, struct PartyPokemon *lead, u8 ability, u32 ivs);

// Overlay 2 initializes these first fields for every regular encounter method.
typedef struct EncounterGenStatePrefix {
    u32 playerId;
    BOOL isRepel;
    BOOL isSweetScent;
} EncounterGenStatePrefix;

#define WILD_PLACEHOLDER_LEVEL 5

static u32 WildPlaceholderPersonality(void)
{
    return gf_rand() | (gf_rand() << 16);
}

static struct PartyPokemon *CreateWildMon(u32 encounterType, u32 rodType, u32 ivs,
                                          struct PartyPokemon *lead, u8 ability)
{
    struct PartyPokemon *wild = AllocMonZeroed(HEAPID_WORLD);
    if (wild == NULL) {
        return NULL;
    }
    space_for_setmondata = 0;
    PokeParaSet(wild, SPECIES_WOOLOO, WILD_PLACEHOLDER_LEVEL, ivs, TRUE,
                WildPlaceholderPersonality(), 0, 0);
    WildEncounterFinalizeWithLead(wild, SPECIES_WOOLOO, encounterType, rodType, lead, ability, ivs);
    ChangeToBattleForm(wild);
    return wild;
}

struct PartyPokemon *CreateEcologyWildMon(u32 encounterType, u32 rodType, u32 ivs)
{
    return CreateWildMon(encounterType, rodType, ivs, NULL, 0);
}

static BOOL LeadAbilitySuppresses(struct PartyPokemon *lead, u8 ability, u8 wildLevel,
                                  const EncounterGenStatePrefix *encInfo)
{
    if ((ability != ABILITY_INTIMIDATE && ability != ABILITY_KEEN_EYE)
        || (encInfo != NULL && encInfo->isSweetScent)) {
        return FALSE;
    }

    u32 leadLevel = GetMonData(lead, MON_DATA_LEVEL, NULL);
    return leadLevel > 5 && leadLevel >= wildLevel + 5u && gf_rand() % 2 == 0;
}

// leadMon is the player's party lead (read-only in vanilla, used for ability checks).
// The wild mon must be built in its own buffer; writing to leadMon clobbers the save party.
u32 SetEncountData_Ecology(
    struct PartyPokemon *leadMon,
    u32 rodType,
    void *encInfo,
    void *encArea UNUSED,
    u32 encounterType,
    u32 battler,
    void *bw)
{
    struct BATTLE_PARAM *battleParam;
    struct Party *party;
    struct PartyPokemon *wild;
    BOOL added;
    u8 ability = 0;
    u8 level;

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

    if (leadMon != NULL && !GetMonData(leadMon, MON_DATA_IS_EGG, NULL)) {
        ability = GetMonData(leadMon, MON_DATA_ABILITY, NULL);
    }
    wild = CreateWildMon(encounterType, rodType, 32, leadMon, ability);
    if (wild == NULL) {
        return FALSE;
    }

    level = GetMonData(wild, MON_DATA_LEVEL, NULL);
    if ((encInfo != NULL && BugContest_DoesRepelSuppress(level, encInfo))
        || LeadAbilitySuppresses(leadMon, ability, level, encInfo)) {
        sys_FreeMemoryEz(wild);
        return FALSE;
    }

    added = PokeParty_Add(party, wild);
    sys_FreeMemoryEz(wild);

    return added ? TRUE : FALSE;
}

#endif
