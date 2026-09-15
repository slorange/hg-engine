#include "config.h"

#ifdef HEAL_AFTER_BATTLE

#include "heal_after_battle.h"

#include "battle.h"
#include "pokemon.h"
#include "save.h"
#include "types.h"

static void HealPartyMon(struct PartyPokemon *mon)
{
    u32 maxhp;
    u32 status = 0;

    if (mon == NULL || IS_NOT_VALID_EWRAM_POINTER(mon)) {
        return;
    }

    if (!GetMonData(mon, MON_DATA_SPECIES_EXISTS, NULL)) {
        return;
    }

    maxhp = GetMonData(mon, MON_DATA_MAXHP, NULL);
    SetMonData(mon, MON_DATA_HP, &maxhp);
    SetMonData(mon, MON_DATA_STATUS, &status);
    RestoreBoxMonPP(&mon->box);
}

void HealAfterBattle_HealParty(struct BattleSystem *bw)
{
    int i;
    int count;
    struct Party *party;
    struct PartyPokemon *pp;
    void *saveData;

    if (bw == NULL || IS_NOT_VALID_EWRAM_POINTER(bw)) {
        return;
    }

    if (bw->sp == NULL || IS_NOT_VALID_EWRAM_POINTER(bw->sp) || !bw->sp->fight_end_flag) {
        return;
    }

    count = BattleWorkPokeCountGet(bw, 0);
    if (count > 6) {
        count = 6;
    }

    for (i = 0; i < count; i++) {
        pp = BattleWorkPokemonParamGet(bw, 0, i);
        HealPartyMon(pp);
    }

    saveData = SaveBlock2_get();
    if (saveData == NULL) {
        return;
    }

    party = SaveData_GetPlayerPartyPtr(saveData);
    if (party == NULL) {
        return;
    }

    for (i = 0; i < party->count && i < (int)(sizeof(party->members) / sizeof(party->members[0])); i++) {
        HealPartyMon(&party->members[i]);
    }
}

#endif // HEAL_AFTER_BATTLE
