#ifndef SYNTHETIC_EVO_APPLY_H
#define SYNTHETIC_EVO_APPLY_H

#include "constants/generated/synthetic_evo_edges.h"
#include "constants/species.h"
#include "types.h"

#define SYNTHETIC_EVO_MAX_CHAIN 8

enum EncounterStageContext {
    ENCOUNTER_STAGE_WILD,
    ENCOUNTER_STAGE_TRAINER,
    ENCOUNTER_STAGE_LEADER,
};

static inline BOOL IsEncounterBaby(u16 species)
{
    const SyntheticEvoEdgesData *tables = gSyntheticEvoEdgesPtr;
    u16 i;
    if (tables == NULL) {
        return FALSE;
    }
    for (i = 0; i < tables->babyCount; i++) {
        if (tables->babies[i] == species) {
            return TRUE;
        }
    }
    return FALSE;
}

// Separate branch and probability domains, and decorrelate successive stages.
// A caller supplies one seed per encounter/slot; no RNG is consumed in the walk.
static inline u32 EncounterStageEntropy(u32 seed, u16 species, u32 domain)
{
    u32 value = seed ^ ((u32)species * 0x9E3779B9u) ^ domain;
    value ^= value >> 16;
    value *= 0x7FEB352Du;
    value ^= value >> 15;
    value *= 0x846CA68Bu;
    return value ^ (value >> 16);
}

static inline BOOL EncounterEvolutionRoll(u8 level, u8 start, u8 end, u32 entropy)
{
    if (level <= start) {
        return FALSE;
    }
    if (level >= end) {
        return TRUE;
    }
    return entropy % (end - start) < (u32)(level - start);
}

static inline BOOL EncounterEvolutionMethodAllowed(u8 method, u8 context)
{
    return context != ENCOUNTER_STAGE_WILD ||
        (method != ENCOUNTER_EVO_TRAINER_ITEM && method != ENCOUNTER_EVO_FRIENDSHIP);
}

static inline u16 PickSyntheticEvolutionStep(u16 species, u8 level, u8 reachedLevel,
    u32 entropy, u8 context, BOOL allowBabies)
{
    const SyntheticEvoEdgesData *tables = gSyntheticEvoEdgesPtr;
    const SyntheticEvoEdge *chosen = NULL;
    u16 i, count = 0, selection;
    BOOL baby = IsEncounterBaby(species);
    u8 start = 15, end;
    if (tables == NULL) {
        return species;
    }

    // First select among context-eligible outcomes, then roll that method once.
    // Baby rolls retain the old fixed thresholds for baby-to-adult transitions.
    for (i = 0; i < tables->count; i++) {
        const SyntheticEvoEdge *edge = &tables->edges[i];
        if (edge->from != species) {
            continue;
        }
        if (baby && !allowBabies) {
            return edge->to;
        }
        if (baby || edge->method == ENCOUNTER_EVO_FIXED) {
            if (level < edge->minLevel) {
                continue;
            }
        } else if (!EncounterEvolutionMethodAllowed(edge->method, context)) {
            continue;
        }
        count++;
    }
    if (count == 0) {
        return species;
    }
    selection = EncounterStageEntropy(entropy, species, 0x4252414Eu) % count;
    for (i = 0; i < tables->count; i++) {
        const SyntheticEvoEdge *edge = &tables->edges[i];
        if (edge->from != species) {
            continue;
        }
        if (baby || edge->method == ENCOUNTER_EVO_FIXED) {
            if (level < edge->minLevel) {
                continue;
            }
        } else if (!EncounterEvolutionMethodAllowed(edge->method, context)) {
            continue;
        }
        if (selection-- == 0) {
            chosen = edge;
            break;
        }
    }
    if (chosen == NULL || baby || chosen->method == ENCOUNTER_EVO_FIXED) {
        return chosen != NULL ? chosen->to : species;
    }
    if (context == ENCOUNTER_STAGE_WILD) {
        if (reachedLevel + 5 > start) {
            start = reachedLevel + 5;
        }
        end = 60;
    } else if (chosen->method == ENCOUNTER_EVO_FRIENDSHIP) {
        end = context == ENCOUNTER_STAGE_LEADER ? 20 : 25;
    } else {
        end = context == ENCOUNTER_STAGE_LEADER ? 25 : 40;
    }
    // Endpoints remain well-defined even for a source stage reached above 60.
    if (level >= end) {
        return chosen->to;
    }
    return EncounterEvolutionRoll(level, start, end,
        EncounterStageEntropy(entropy, species, 0x50524F42u)) ? chosen->to : species;
}

#endif
