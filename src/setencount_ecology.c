#include "config.h"

#ifdef IMPLEMENT_ECOLOGY_GENERATION

#include "battle.h"
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

u32 SetEncountData_Ecology(
    struct PartyPokemon *pp,
    u32 rodType,
    void *encInfo UNUSED,
    void *encArea UNUSED,
    u32 encounterType,
    u32 battler,
    void *bw)
{
    u32 rnd;
    u16 placeholder;
    struct BATTLE_PARAM *battleParam;
    struct Party *party;

    if (pp == NULL || bw == NULL) {
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

    placeholder = SPECIES_RATTATA;
    rnd = WildPlaceholderPersonality();
    space_for_setmondata = 0;

    PokeParaSet(pp, placeholder, WILD_PLACEHOLDER_LEVEL, 31, TRUE, rnd, 0, 0);
    WildEncounterFinalizeForEncount(pp, placeholder, encounterType, rodType);
    ChangeToBattleForm(pp);

    if (!PokeParty_Add(party, pp)) {
        return FALSE;
    }

    return TRUE;
}

#endif
