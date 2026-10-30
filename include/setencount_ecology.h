#ifndef SETENCOUNT_ECOLOGY_H
#define SETENCOUNT_ECOLOGY_H

#include "pokemon.h"

u32 LONG_CALL SetEncountData_Ecology(
    struct PartyPokemon *pp,
    u32 rodType,
    void *encInfo,
    void *encArea,
    u32 encounterType,
    u32 battler,
    void *bw);

#endif
