#ifndef EEVEE_EVOLUTIONS_H
#define EEVEE_EVOLUTIONS_H

#include "pokemon.h"
#include "constants/item.h"
#include "constants/species.h"
#include "../data/eevee_extra_evolutions.h"

static inline u8 PlayerEvolutionEntryCount(u16 species)
{
    // Eevee's ninth native slot is now empty; count its eight active base methods.
    return species == SPECIES_EEVEE ? MAX_EVOS_PER_POKE - 1 + NELEMS(sEeveeExtraEvolutions) : MAX_EVOS_PER_POKE;
}

// Called after reading the ordinary fixed-size NARC member into a larger buffer.
static inline void AddEeveeEvolutionEntries(u16 species, struct Evolution *entries)
{
    int i;
    if (species != SPECIES_EEVEE) {
        return;
    }
    // Preserve explicit items and Fairy-move priority. All three location methods
    // take priority over ordinary friendship. Skip the empty ninth native slot.
    for (i = MAX_EVOS_PER_POKE - 2; i >= 6; i--) {
        entries[i + NELEMS(sEeveeExtraEvolutions)] = entries[i];
    }
    for (i = 0; i < (int)NELEMS(sEeveeExtraEvolutions); i++) {
        entries[6 + i] = sEeveeExtraEvolutions[i];
    }
}

#endif
