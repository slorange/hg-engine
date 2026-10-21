#include "config.h"

#ifdef HEAL_AFTER_BATTLE

#include "heal_after_battle.h"

#include "pokemon.h"
#include "save.h"
#include "types.h"

int LONG_CALL PokeParty_GetPokeCount(struct Party *party);

static void HealPartyMon(struct PartyPokemon *mon)
{
    u16 maxhp;
    u16 status = 0;

    if (mon == NULL) {
        return;
    }

    if (!GetMonData(mon, MON_DATA_SPECIES_EXISTS, NULL)) {
        return;
    }

    maxhp = (u16)GetMonData(mon, MON_DATA_MAXHP, NULL);
    SetMonData(mon, MON_DATA_HP, &maxhp);
    SetMonData(mon, MON_DATA_STATUS, &status);
    RestoreBoxMonPP(&mon->box);
}

static void HealSaveParty(void *saveData)
{
    int i;
    int count;
    struct Party *party;
    struct PartyPokemon *mon;

    if (saveData == NULL) {
        return;
    }

    party = SaveData_GetPlayerPartyPtr(saveData);
    if (party == NULL) {
        return;
    }

    count = PokeParty_GetPokeCount(party);
    if (count <= 0 || count > 6) {
        return;
    }

    for (i = 0; i < count; i++) {
        mon = Party_GetMonByIndex(party, i);
        HealPartyMon(mon);
    }
}

void LONG_CALL HealAfterBattle_HealPartyOnFieldStep(void *saveData)
{
    HealSaveParty(saveData);
}

#endif // HEAL_AFTER_BATTLE
