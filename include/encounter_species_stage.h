#ifndef ENCOUNTER_SPECIES_STAGE_H
#define ENCOUNTER_SPECIES_STAGE_H

#include "species_stage_for_level.h"
#include "synthetic_evo_apply.h"
#include "types.h"

static inline u16 AdjustEncounterSpeciesForLevel(u16 species, u8 level)
{
    species = (u16)(species & 0x07FF);
    species = AdjustSpeciesForLevel(species, level);
    return ApplySyntheticEvolutionEdges(species, level);
}

#endif
