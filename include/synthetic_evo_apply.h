#ifndef SYNTHETIC_EVO_APPLY_H
#define SYNTHETIC_EVO_APPLY_H

#include "constants/generated/synthetic_evo_edges.h"
#include "constants/species.h"
#include "types.h"

#define SYNTHETIC_EVO_MAX_CHAIN 8
#define SYNTHETIC_RANDOM50_MAX 4

static inline u16 PickSyntheticEvolutionStep(u16 species, u8 level)
{
    u16 i;
    u16 bestTo = SPECIES_NONE;
    u8 bestMin = 0;
    u16 randomTo[SYNTHETIC_RANDOM50_MAX];
    u8 randomCount = 0;
    u8 randomMin = 0;
    const SyntheticEvoEdgesData *tables = gSyntheticEvoEdgesPtr;

    if (tables == NULL || tables->count == 0) {
        return species;
    }

    for (i = 0; i < tables->count; i++) {
        const SyntheticEvoEdge *edge = &tables->edges[i];

        if (edge->from != species || level < edge->minLevel) {
            continue;
        }

        if (edge->branch == SYNTH_BRANCH_RANDOM50) {
            if (randomCount == 0) {
                randomMin = edge->minLevel;
            }
            if (edge->minLevel != randomMin) {
                continue;
            }
            if (randomCount < SYNTHETIC_RANDOM50_MAX) {
                randomTo[randomCount++] = edge->to;
            }
            continue;
        }

        if (edge->minLevel >= bestMin) {
            bestMin = edge->minLevel;
            bestTo = edge->to;
        }
    }

    if (randomCount > 0) {
        return randomTo[gf_rand() % randomCount];
    }

    if (bestTo != SPECIES_NONE) {
        return bestTo;
    }

    return species;
}

static inline u16 ApplySyntheticEvolutionEdges(u16 species, u8 level)
{
    u16 cur = species;
    u16 next;
    u8 steps;

    for (steps = 0; steps < SYNTHETIC_EVO_MAX_CHAIN; steps++) {
        next = PickSyntheticEvolutionStep(cur, level);
        if (next == cur || next == SPECIES_NONE) {
            break;
        }
        cur = next;
    }

    return cur;
}

#endif
