#ifndef SPECIES_STAGE_FOR_LEVEL_H
#define SPECIES_STAGE_FOR_LEVEL_H

#include "constants/generated/level_up_evo_tables.h"
#include "constants/species.h"
#include "types.h"

static inline u16 FindLevelUpChainBase(u16 species)
{
    u16 prevo;

    species = (u16)(species & 0x07FF);

    while (species <= MAX_SPECIES_INCLUDING_FORMS) {
        prevo = sLevelUpPrevo[species];
        if (prevo == SPECIES_NONE) {
            break;
        }
        species = prevo;
    }

    return species;
}

static inline u16 AdjustSpeciesForLevel(u16 species, u8 level)
{
    u16 base;
    u16 cur;
    u16 best;
    u16 next;
    u8 minLv;
    u8 maxLv;

    species = (u16)(species & 0x07FF);
    base = FindLevelUpChainBase(species);
    cur = base;
    best = base;

    while (cur != SPECIES_NONE && cur <= MAX_SPECIES_INCLUDING_FORMS) {
        minLv = sLevelUpMinStageLevel[cur];
        maxLv = 100;
        next = sLevelUpEvoTarget[cur];

        if (next != SPECIES_NONE && next <= MAX_SPECIES_INCLUDING_FORMS) {
            maxLv = (u8)(sLevelUpMinStageLevel[next] - 1);
        }

        if (level >= minLv && level <= maxLv) {
            best = cur;
        }

        if (next == SPECIES_NONE) {
            break;
        }

        cur = next;
    }

    return best;
}

#endif
