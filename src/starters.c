#include "../include/constants/species.h"
#include "../include/pokemon.h"
#include "../include/script.h"
#include "../include/types.h"

extern u32 space_for_setmondata;
extern u32 sStarterChoiceCries[];
extern FieldSystem *gFieldSysPtr;

void LONG_CALL GetMonSpriteCharAndPlttNarcIdsEx(MON_PIC *picdata, u16 mons_no, u8 dir, u8 col, u8 form_no, u8 a5, u32 personality);

#define STARTER_COUNT 6
#define VAR_PLAYER_STARTER 0x4030

// Johto 0–2, Kanto 3–5. Before choose_starter, scripts set VAR_PLAYER_STARTER to 0 (Johto) or 3 (Kanto).
static const u16 sStarterChoices[STARTER_COUNT] = {
    SPECIES_CHIKORITA,
    SPECIES_CYNDAQUIL,
    SPECIES_TOTODILE,
    SPECIES_BULBASAUR,
    SPECIES_CHARMANDER,
    SPECIES_SQUIRTLE,
};

static u16 StarterChoiceBase(void)
{
    u16 base = 0;

    if (gFieldSysPtr != NULL) {
        u16 var = VarGet(gFieldSysPtr, VAR_PLAYER_STARTER);
        if (var >= 3) {
            base = 3;
        }
    }

    return base;
}

/**
 *  @brief fills the given array with the species ids of the starter choices
 *
 *  @param species pointer to the species array
 */
void LONG_CALL CreateStarter_SetStarterSpecies(int *species)
{
    u16 base = StarterChoiceBase();

    for (int i = 0; i < 3; i++) {
        species[i] = sStarterChoices[base + i] & 0x7FF;
    }
}

/**
 *  @brief wrap the CreateMon call within CreateStarter to allow for starter forms
 *
 *  @param mon the PartyPokemon pointer
 *  @param species the species id
 *  @param slot starter choice (0-2 within the active trio)
 */
void LONG_CALL CreateStarter_CreateMon(struct PartyPokemon *mon, int species, int slot)
{
    u32 form = 0;
    u16 base = StarterChoiceBase();

    if (slot >= 0 && slot < 3) {
        form = sStarterChoices[base + slot] >> 11;
    }

    space_for_setmondata = form;
    PokeParaSet(mon, species, 5, 32, FALSE, 0, 0, 0);
    space_for_setmondata = 0;

    if (form != 0) {
        SetMonData(mon, MON_DATA_FORM, &form);
    }
}

/**
 *  @brief wrap the GetMonSpriteCharAndPlttNarcIdsEx call within createMonSprites to handle starter forms
 *
 *  @param pic MON_PIC pointer
 *  @param species species id
 */
void LONG_CALL CreateMonSprites_HandleForm(MON_PIC *pic, u16 species, u8 gender, u8 shiny, int slot)
{
    u32 form = 0;
    u16 base = StarterChoiceBase();

    if (slot >= 0 && slot < 3) {
        form = sStarterChoices[base + slot] >> 11;
        sStarterChoiceCries[slot] = (form == 0) ? species : PokeOtherFormMonsNoGet(species, form);
    }

    GetMonSpriteCharAndPlttNarcIdsEx(pic, species, gender, 2, shiny, 0, 0);

    if (form != 0) {
        GetOtherFormPic(pic, species, 2, shiny, form);
    }
}
