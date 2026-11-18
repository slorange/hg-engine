#ifndef WILD_ENCOUNTER_FINALIZE_H
#define WILD_ENCOUNTER_FINALIZE_H

#include "pokemon.h"

/**
 * Resident entry points dispatch synchronous post-table generation to overlay
 * 152, which is unloaded before returning to the encounter/battle caller.
 *
 * @param pp PartyPokemon being filled for the wild battler
 * @param vanillaTableSpecies species from the encounter table / EncountParamSet stack
 */
u16 WildEncounterFinalize(struct PartyPokemon *pp, u16 vanillaTableSpecies);

u16 WildEncounterFinalizeForEncount(
    struct PartyPokemon *pp,
    u16 vanillaTableSpecies,
    u32 encounterType,
    u32 rodType);

#endif
