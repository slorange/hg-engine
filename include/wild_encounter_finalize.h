#ifndef WILD_ENCOUNTER_FINALIZE_H
#define WILD_ENCOUNTER_FINALIZE_H

#include "pokemon.h"

/**
 * Post-table wild encounter setup (overlay 129).
 * Called from modify_species_encounter_data today; SetEncountData stub will call
 * this after a placeholder mon exists (Phase 2+).
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
