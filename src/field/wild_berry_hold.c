#include "config.h"

#ifdef IMPLEMENT_WILD_BERRY_HOLD

#include "wild_berry_hold.h"

#include "constants/ability.h"
#include "constants/battle_constants.h"
#include "constants/generated/wild_species_held_items.h"
#include "constants/item.h"
#include "constants/species.h"
#include "pokemon.h"
#include "save.h"
#include "types.h"

extern const u16 sWildSpeciesHeldCommon[WILD_SPECIES_HELD_ITEM_COUNT];
extern const u16 sWildSpeciesHeldRare[WILD_SPECIES_HELD_ITEM_COUNT];

static const u16 sWildBerryHoldPool[] = {
    ITEM_CHERI_BERRY,
    ITEM_CHESTO_BERRY,
    ITEM_PECHA_BERRY,
    ITEM_RAWST_BERRY,
    ITEM_ASPEAR_BERRY,
    ITEM_LEPPA_BERRY,
    ITEM_ORAN_BERRY,
    ITEM_PERSIM_BERRY,
    ITEM_LUM_BERRY,
    ITEM_SITRUS_BERRY,
    ITEM_POMEG_BERRY,
    ITEM_KELPSY_BERRY,
    ITEM_QUALOT_BERRY,
    ITEM_HONDEW_BERRY,
    ITEM_GREPA_BERRY,
    ITEM_TAMATO_BERRY,
    ITEM_OCCA_BERRY,
    ITEM_PASSHO_BERRY,
    ITEM_WACAN_BERRY,
    ITEM_RINDO_BERRY,
    ITEM_YACHE_BERRY,
    ITEM_CHOPLE_BERRY,
    ITEM_KEBIA_BERRY,
    ITEM_SHUCA_BERRY,
    ITEM_COBA_BERRY,
    ITEM_PAYAPA_BERRY,
    ITEM_TANGA_BERRY,
    ITEM_CHARTI_BERRY,
    ITEM_KASIB_BERRY,
    ITEM_HABAN_BERRY,
    ITEM_COLBUR_BERRY,
    ITEM_BABIRI_BERRY,
    ITEM_CHILAN_BERRY,
    ITEM_LIECHI_BERRY,
    ITEM_GANLON_BERRY,
    ITEM_SALAC_BERRY,
    ITEM_PETAYA_BERRY,
    ITEM_APICOT_BERRY,
    ITEM_LANSAT_BERRY,
    ITEM_STARF_BERRY,
    ITEM_ENIGMA_BERRY,
    ITEM_MICLE_BERRY,
    ITEM_CUSTAP_BERRY,
    ITEM_JABOCA_BERRY,
    ITEM_ROWAP_BERRY,
};

/*
 * pret: one roll 0–99 — if chance >= holdMin, common when chance < commonMax else rare.
 * Normal: 20 / 85 → 20% nothing, 65% common, 15% rare.
 * Compound Eyes (lead): 0 / 70 → 70% common, 30% rare, 0% nothing.
 */
static const u8 sWildHeldItemOdds[2][2] = {
    { 20, 85 },
    { 0, 70 },
};

#define WILD_BERRY_HOLD_FALLBACK_PERCENT 50

static u16 RollRandomBerry(void)
{
    return sWildBerryHoldPool[gf_rand() % NELEMS(sWildBerryHoldPool)];
}

static u32 PlayerLeadHasCompoundEyes(void)
{
    void *saveData;
    struct Party *party;
    struct PartyPokemon *lead;
    u32 ability;

    saveData = SaveBlock2_get();
    if (saveData == NULL) {
        return FALSE;
    }

    party = SaveData_GetPlayerPartyPtr(saveData);
    if (party == NULL || party->count == 0) {
        return FALSE;
    }

    lead = Party_GetMonByIndex(party, 0);
    if (lead == NULL || GetMonData(lead, MON_DATA_IS_EGG, NULL) != FALSE) {
        return FALSE;
    }

    ability = GetMonData(lead, MON_DATA_ABILITY, NULL);
    return ability == ABILITY_COMPOUND_EYES;
}

static u16 RollSpeciesTableHeldItem(u16 species, u32 isCompoundEyes)
{
    u32 chance;
    u16 item1;
    u16 item2;
    u8 holdMin;
    u8 commonMax;

    if (species >= WILD_SPECIES_HELD_ITEM_COUNT) {
        return ITEM_NONE;
    }

    item1 = sWildSpeciesHeldCommon[species];
    item2 = sWildSpeciesHeldRare[species];

    if (item1 == item2 && item1 != ITEM_NONE) {
        return item1;
    }

    holdMin = sWildHeldItemOdds[isCompoundEyes != 0 ? 1 : 0][0];
    commonMax = sWildHeldItemOdds[isCompoundEyes != 0 ? 1 : 0][1];

    chance = (u32)(gf_rand() % 100);
    if (chance < holdMin) {
        return ITEM_NONE;
    }
    if (chance < commonMax) {
        return item1;
    }
    return item2;
}

static void WildMonSetRandomHeldItemImpl(struct PartyPokemon *pokemon, u32 battleType, u32 isCompoundEyes)
{
    u16 species;
    u16 item;

    if (pokemon == NULL) {
        return;
    }

    if (battleType & (BATTLE_TYPE_TRAINER | BATTLE_TYPE_FRONTIER)) {
        return;
    }

    species = (u16)GetMonData(pokemon, MON_DATA_SPECIES, NULL);
    item = RollSpeciesTableHeldItem(species, isCompoundEyes);

    if (item == ITEM_NONE) {
        if (isCompoundEyes != 0) {
            item = RollRandomBerry();
        } else if ((gf_rand() % 100) < WILD_BERRY_HOLD_FALLBACK_PERCENT) {
            item = RollRandomBerry();
        }
    }

    SetMonData(pokemon, MON_DATA_HELD_ITEM, &item);
}

void WildMonApplyHeldItemForEncounter(struct PartyPokemon *pokemon)
{
    WildMonSetRandomHeldItemImpl(pokemon, 0, PlayerLeadHasCompoundEyes());
}

void WildMonSetRandomHeldItem_hook(struct PartyPokemon *pokemon, u32 battleType, u32 isCompoundEyes)
{
    WildMonSetRandomHeldItemImpl(pokemon, battleType, isCompoundEyes);
}

#endif // IMPLEMENT_WILD_BERRY_HOLD
