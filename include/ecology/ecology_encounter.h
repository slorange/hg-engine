#ifndef ECOLOGY_ECOLOGY_ENCOUNTER_H
#define ECOLOGY_ECOLOGY_ENCOUNTER_H

#include "../types.h"

#define EcologyActiveMethodRef (*(volatile u8 *)0x021FF944)

static inline void EcologyScratchSetActiveMethod(u8 method)
{
    EcologyActiveMethodRef = (u8)(method + 1u);
}

u16 EcologyApplyGrassSpeciesOverride(u16 vanillaSpecies);

#endif
