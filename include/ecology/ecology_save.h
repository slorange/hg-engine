#ifndef ECOLOGY_ECOLOGY_SAVE_H
#define ECOLOGY_ECOLOGY_SAVE_H

#include "config.h"

#if defined(ALLOW_SAVE_CHANGES) && defined(IMPLEMENT_ECOLOGY_GENERATION)

#include "constants/generated/ecology_compat.h"
#include "types.h"

#define ECOLOGY_SAVE_MAGIC 0x314F4345u /* 'ECO1' little-endian */

typedef struct EcologyWorldSave {
    u32 magic;
    u32 compatVersion;
    u32 worldSeed;
    u16 slotCount;
    u16 reserved;
    u16 familyIds[ECOLOGY_GEN_TOTAL_SLOTS];
    u8 landTimeMasks[ECOLOGY_GEN_TOTAL_SLOTS];
} EcologyWorldSave;

typedef struct SaveData SaveData;

void EcologySaveClear(struct EcologyWorldSave *eco);
EcologyWorldSave *EcologySaveGetMutable(SaveData *saveData);
void EcologySaveWriteGeneration(
    struct EcologyWorldSave *eco,
    u32 worldSeed,
    u16 slotCount,
    const u16 *familyIds,
    const u8 *landTimeMasks);
BOOL EcologySaveIsValid(const struct EcologyWorldSave *eco);

#endif

#endif
