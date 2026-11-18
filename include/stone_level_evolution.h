#ifndef STONE_LEVEL_EVOLUTION_H
#define STONE_LEVEL_EVOLUTION_H

#include "pokemon.h"
#include "constants/item.h"
#include "constants/pokemon.h"
#include "constants/species.h"

// Early item evolution applies only to plain level evolutions.
static inline u8 StoneLevelEvolutionRequirement(u16 item, const struct Evolution *evolution)
{
    u8 type;
    if (evolution->method != EVO_LEVEL || evolution->target == SPECIES_NONE) {
        return 0;
    }
    // The Beldum family keeps its normal evolution pacing.
    if ((evolution->target & 0x07FF) == SPECIES_METANG ||
        (evolution->target & 0x07FF) == SPECIES_METAGROSS) {
        return 0;
    }
    switch (item) {
    case ITEM_FIRE_STONE: type = TYPE_FIRE; break;
    case ITEM_WATER_STONE: type = TYPE_WATER; break;
    case ITEM_LEAF_STONE: type = TYPE_GRASS; break;
    case ITEM_THUNDER_STONE: type = TYPE_ELECTRIC; break;
    case ITEM_ICE_STONE: type = TYPE_ICE; break;
    case ITEM_METAL_COAT: type = TYPE_STEEL; break;
    case ITEM_DUSK_STONE: type = TYPE_GHOST; break;
    default: return 0;
    }
    u16 target = evolution->target & 0x07FF;
    u8 form = evolution->target >> 11;
    if (PokeFormNoPersonalParaGet(target, form, PERSONAL_TYPE_1) != type &&
        PokeFormNoPersonalParaGet(target, form, PERSONAL_TYPE_2) != type) {
        return 0;
    }
    // ceil(normal level * 0.90 - 3), with a minimum requirement of level 1.
    u16 scaled = (evolution->param * 90u + 99u) / 100u;
    return scaled > 3 ? scaled - 3 : 1;
}

u8 LONG_CALL GetStoneLevelEvolutionRequirement(struct PartyPokemon *mon, u16 item);

#endif
