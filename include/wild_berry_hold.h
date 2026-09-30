#ifndef WILD_BERRY_HOLD_H
#define WILD_BERRY_HOLD_H

#include "types.h"

struct PartyPokemon;

void WildMonApplyHeldItemForEncounter(struct PartyPokemon *pokemon);
void WildMonSetRandomHeldItem_hook(struct PartyPokemon *pokemon, u32 battleType, u32 isCompoundEyes);

#endif
