#include "battle.h"
#include "constants/species.h"
#include "pokedex.h"
#include "pokemon.h"
#include "save.h"

void LONG_CALL LoadSpeciesFormPersonalData(u32 species, u32 form, void *data);
void LONG_CALL CopyPokedexData(const struct Save_DexData *src, struct Save_DexData *dest);

void UnownLoadStatPersonalData(u32 species, u32 form, u8 *data)
{
    LoadSpeciesFormPersonalData(species, form, data);
    if (species != SPECIES_UNOWN) {
        return;
    }

    void *save = SaveBlock2_get();
    u8 count = Pokedex_CountCaughtUnown(save != NULL ? SaveData_GetDexPtr(save) : NULL);
    u8 low = 44 + (56 * count + 14) / 28;
    u8 high = 66 + (84 * count + 14) / 28;

    // Packed personal data orders these as HP, Attack, Defense, Speed, Sp. Atk, Sp. Def.
    data[0] = high;
    data[1] = low;
    data[2] = low;
    data[3] = low;
    data[4] = high;
    data[5] = low;
}

void UnownCopyBattlePokedex(const struct Save_DexData *src, struct Save_DexData *dest)
{
    u8 oldCount = Pokedex_CountCaughtUnown(dest);
    CopyPokedexData(src, dest);
    if (oldCount == Pokedex_CountCaughtUnown(dest)) {
        return;
    }

    void *save = SaveBlock2_get();
    if (save == NULL || dest != SaveData_GetDexPtr(save)) {
        return;
    }
    // Battle exit has already copied the updated battle party into the save.
    struct Party *party = SaveData_GetPlayerPartyPtr(save);
    for (int slot = 0; slot < party->count; slot++) {
        struct PartyPokemon *member = Party_GetMonByIndex(party, slot);
        if (GetMonData(member, MON_DATA_SPECIES, NULL) == SPECIES_UNOWN) {
            RecalcPartyPokemonStats(member);
        }
    }
}

BOOL UnownBattleCaughtIcon(struct BattleSystem *battle, u32 species, u32 battler)
{
    if (species != SPECIES_UNOWN) {
        return Battle_CheckIfHasCaughtMon(battle, species);
    }

    return Pokedex_HasCaughtUnownForm(BattleWorkZukanWorkGet(battle), battle->sp->battlemon[battler].form_no);
}
