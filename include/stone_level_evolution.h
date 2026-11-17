#ifndef STONE_LEVEL_EVOLUTION_H
#define STONE_LEVEL_EVOLUTION_H

#include "pokemon.h"
#include "constants/item.h"
#include "constants/pokemon.h"
#include "constants/species.h"

// Proof of concept: only the five elemental stones and plain level evolutions.
static inline u8 StoneLevelEvolutionRequirement(u16 item, u8 type1, u8 type2, const struct Evolution *evolution)
{
    u8 type;
    if (evolution->method != EVO_LEVEL || evolution->target == SPECIES_NONE) {
        return 0;
    }
    switch (item) {
    case ITEM_FIRE_STONE: type = TYPE_FIRE; break;
    case ITEM_WATER_STONE: type = TYPE_WATER; break;
    case ITEM_LEAF_STONE: type = TYPE_GRASS; break;
    case ITEM_THUNDER_STONE: type = TYPE_ELECTRIC; break;
    case ITEM_ICE_STONE: type = TYPE_ICE; break;
    default: return 0;
    }
    if (type1 != type && type2 != type) {
        return 0;
    }
    return (evolution->param * 3u + 3u) / 4u;
}

u8 LONG_CALL GetStoneLevelEvolutionRequirement(struct PartyPokemon *mon, u16 item);

#endif
