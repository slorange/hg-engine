#ifndef EVOLUTION_OVERLAY_H
#define EVOLUTION_OVERLAY_H

#include "pokemon.h"

// Both evolution overlays expose this table at the start of their load region.
struct EvolutionOverlayApi {
    u16 (*evolve)(struct Party *, struct PartyPokemon *, u8, u16, int *);
    u8 (*requiredLevel)(struct PartyPokemon *, u16);
    void (*printCompatibility)(struct PartyMenu *, u8, u8);
};

#ifndef EVOLUTION_OVERLAY_FIELD_API
#define EVOLUTION_OVERLAY_FIELD_API ((const struct EvolutionOverlayApi *)0x023C0400)
#endif
#ifndef EVOLUTION_OVERLAY_BATTLE_API
#define EVOLUTION_OVERLAY_BATTLE_API ((const struct EvolutionOverlayApi *)0x021FBE60)
#endif

const struct EvolutionOverlayApi *LONG_CALL OpenEvolutionOverlay(u32 *overlayId, BOOL *owned);
void LONG_CALL CloseEvolutionOverlay(u32 overlayId, BOOL owned);

#endif
