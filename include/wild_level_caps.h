#ifndef WILD_LEVEL_CAPS_H
#define WILD_LEVEL_CAPS_H

#include "pokemon.h"

void CacheWildLevelCapFromFieldSystem(FieldSystem *fsys);
void ApplyWildDistanceLevelCapToMon(struct PartyPokemon *pp);

#endif
