#ifndef ENCOUNTER_SPECIES_STAGE_H
#define ENCOUNTER_SPECIES_STAGE_H

#include "species_stage_for_level.h"
#include "synthetic_evo_apply.h"
#include "types.h"

#define ENCOUNTER_EVO_MAX_BASE_WALK 16

static inline u16 FindSyntheticPrevo(u16 species)
{
    u16 i;
    const SyntheticEvoEdgesData *tables = gSyntheticEvoEdgesPtr;

    if (tables == NULL || tables->count == 0) {
        return SPECIES_NONE;
    }

    for (i = 0; i < tables->count; i++) {
        if (tables->edges[i].to == species) {
            return tables->edges[i].from;
        }
    }

    return SPECIES_NONE;
}

static inline u16 FindEncounterChainBase(u16 species)
{
    u16 levelUpPrevo;
    u16 synthPrevo;
    u8 steps;

    species = (u16)(species & 0x07FF);

    for (steps = 0; steps < ENCOUNTER_EVO_MAX_BASE_WALK; steps++) {
        levelUpPrevo = sLevelUpPrevo[species];
        synthPrevo = FindSyntheticPrevo(species);

        if (levelUpPrevo != SPECIES_NONE) {
            species = levelUpPrevo;
            continue;
        }

        if (synthPrevo != SPECIES_NONE) {
            species = synthPrevo;
            continue;
        }

        break;
    }

    return species;
}

static inline u16 WalkEncounterStageForLevel(u16 species, u8 level)
{
    u16 cur = species;
    u16 nextLevel;
    u16 nextSynth;
    u8 steps;

    for (steps = 0; steps < SYNTHETIC_EVO_MAX_CHAIN; steps++) {
        BOOL advanced = FALSE;

        nextLevel = sLevelUpEvoTarget[cur];
        if (nextLevel != SPECIES_NONE && level >= sLevelUpMinStageLevel[nextLevel]) {
            cur = nextLevel;
            advanced = TRUE;
        }

        nextSynth = PickSyntheticEvolutionStep(cur, level);
        if (nextSynth != cur && nextSynth != SPECIES_NONE) {
            cur = nextSynth;
            advanced = TRUE;
        }

        if (!advanced) {
            break;
        }
    }

    return cur;
}

static inline u16 AdjustEncounterSpeciesForLevel(u16 species, u8 level)
{
    species = (u16)(species & 0x07FF);
    species = FindEncounterChainBase(species);
    return WalkEncounterStageForLevel(species, level);
}

#endif
