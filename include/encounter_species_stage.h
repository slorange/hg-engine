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

static inline u16 WalkEncounterStageForLevel(u16 species, u8 level, u32 entropy,
    u8 context, BOOL allowBabies)
{
    u16 cur = species;
    u8 reachedLevel = 0;
    u8 steps;
    for (steps = 0; steps < SYNTHETIC_EVO_MAX_CHAIN; steps++) {
        BOOL skipBaby = !allowBabies && IsEncounterBaby(cur);
        u16 nextSynth = PickSyntheticEvolutionStep(cur, level, reachedLevel, entropy, context, allowBabies);
        u16 nextLevel;
        if (nextSynth != cur && nextSynth != SPECIES_NONE) {
            // Fixed thresholds determine when this stage first became available.
            const SyntheticEvoEdgesData *tables = gSyntheticEvoEdgesPtr;
            u16 i;
            for (i = 0; i < tables->count; i++) {
                const SyntheticEvoEdge *edge = &tables->edges[i];
                if (edge->from == cur && edge->to == nextSynth) {
                    reachedLevel = skipBaby ? 0 : edge->minLevel;
                    break;
                }
            }
            cur = nextSynth;
            continue;
        }
        nextLevel = sLevelUpEvoTarget[cur];
        if (nextLevel != SPECIES_NONE && (skipBaby || level >= sLevelUpMinStageLevel[nextLevel])) {
            reachedLevel = skipBaby ? 0 : sLevelUpMinStageLevel[nextLevel];
            cur = nextLevel;
            continue;
        }
        break;
    }
    return cur;
}

static inline u16 AdjustEncounterSpeciesForLevel(u16 species, u8 level, u32 entropy,
    u8 context, BOOL allowBabies)
{
    species = (u16)(species & 0x07FF);
    species = FindEncounterChainBase(species);
    return WalkEncounterStageForLevel(species, level, entropy, context, allowBabies);
}

#endif
