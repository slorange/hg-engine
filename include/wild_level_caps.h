#ifndef WILD_LEVEL_CAPS_H
#define WILD_LEVEL_CAPS_H

#include "pokemon.h"

void CacheWildLevelCapFromFieldSystem(FieldSystem *fsys);
void ApplyWildDistanceLevelCapToMon(struct PartyPokemon *pp);
u8 GetWildLevelCapForEncounterBank(u8 encBank);
u8 RollWildLevel(u8 cap);
void ApplyWildEncounterLevelAndStage(struct PartyPokemon *pp, u8 level);

#endif
