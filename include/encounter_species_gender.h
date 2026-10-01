#ifndef ENCOUNTER_SPECIES_GENDER_H
#define ENCOUNTER_SPECIES_GENDER_H

#include "constants/species.h"
#include "encounter_species_stage.h"
#include "pokemon.h"
#include "types.h"

struct EncounterForcedGender {
    u16 species;
    u8 gender;
};

static const struct EncounterForcedGender sEncounterForcedGender[] = {
    { SPECIES_WORMADAM, POKEMON_GENDER_FEMALE },
    { SPECIES_MOTHIM, POKEMON_GENDER_MALE },
    { SPECIES_VESPIQUEN, POKEMON_GENDER_FEMALE },
    { SPECIES_GALLADE, POKEMON_GENDER_MALE },
    { SPECIES_FROSLASS, POKEMON_GENDER_FEMALE },
};

static inline u8 LookupEncounterForcedGender(u16 species)
{
    u16 i;

    for (i = 0; i < NELEMS(sEncounterForcedGender); i++) {
        if (sEncounterForcedGender[i].species == species) {
            return sEncounterForcedGender[i].gender;
        }
    }

    return 0xFF;
}

static inline u16 ApplyGenderedStageAdjustCorrections(u16 species, u8 gender)
{
    if (species == SPECIES_VESPIQUEN && gender == POKEMON_GENDER_MALE) {
        return SPECIES_COMBEE;
    }

    return species;
}

static inline u16 AdjustEncounterSpeciesForLevelWithGender(u16 species, u8 level, u8 gender, u32 branchEntropy)
{
    species = AdjustEncounterSpeciesForLevel(species, level, branchEntropy);
    return ApplyGenderedStageAdjustCorrections(species, gender);
}

static inline void ApplyEncounterStageAdjustToMon(struct PartyPokemon *pp, u8 level, u32 branchEntropy)
{
    u16 species;
    u16 adjusted;
    u8 gender;
    u32 formZero = 0;

    if (pp == NULL) {
        return;
    }

#if defined(OVERLAY129)
    if (LevelUpEvoTablesFieldAddr == 0 || SyntheticEvoEdgesFieldAddr == 0) {
        return;
    }
#endif

    species = (u16)(GetMonData(pp, MON_DATA_SPECIES, NULL) & 0x07FF);
    gender = (u8)GetMonData(pp, MON_DATA_GENDER, NULL);
    adjusted = AdjustEncounterSpeciesForLevelWithGender(species, level, gender, branchEntropy);

    if (adjusted == species) {
        return;
    }

    SetMonData(pp, MON_DATA_SPECIES, &adjusted);
    SetMonData(pp, MON_DATA_SPECIES_NAME, NULL);
    SetMonData(pp, MON_DATA_FORM, &formZero);
}

static inline void ApplyEncounterGenderAfterStageAdjust(struct PartyPokemon *pp)
{
    u16 species;
    u32 form;
    u32 pid;
    u32 gender;
    u8 genderByte;
    u8 forced;
    u32 i;

    if (pp == NULL) {
        return;
    }

    species = (u16)(GetMonData(pp, MON_DATA_SPECIES, NULL) & 0x07FF);
    form = GetMonData(pp, MON_DATA_FORM, NULL);
    pid = GetMonData(pp, MON_DATA_PERSONALITY, NULL);
    forced = LookupEncounterForcedGender(species);

    if (forced != 0xFF) {
        for (i = 0; i < 256; i++) {
            u32 tryPid = (pid & 0xFFFFFF00) | i;

            if (GrabSexFromSpeciesAndForm(species, tryPid, form) == forced) {
                pid = tryPid;
                break;
            }
        }
        SetMonData(pp, MON_DATA_PERSONALITY, &pid);
        gender = forced;
    } else {
        gender = GrabSexFromSpeciesAndForm(species, pid, form);
    }

    genderByte = (u8)gender;
    SetMonData(pp, MON_DATA_GENDER, &genderByte);
}

#endif
