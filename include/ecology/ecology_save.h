#ifndef ECOLOGY_ECOLOGY_SAVE_H
#define ECOLOGY_ECOLOGY_SAVE_H

#include "config.h"

#if defined(ALLOW_SAVE_CHANGES) && defined(IMPLEMENT_ECOLOGY_GENERATION)

#include "constants/generated/ecology_compat.h"
#include "types.h"

#define ECOLOGY_SAVE_MAGIC 0x314F4345u /* 'ECO1' little-endian */
#define ECOLOGY_SAVE_FAMILY_EMPTY 0xFFu

/* Families with ROM landTimeMask != 0 (deduped by family at write time). */
#define ECOLOGY_SAVE_LAND_TIME_SPARSE_MAX 96u

typedef struct EcologyLandTimeSparseEntry {
    u8 familyId;
    u8 landTimeMask;
} EcologyLandTimeSparseEntry;

typedef struct EcologyWorldSave {
    u32 magic;
    u32 compatVersion; /* written at gen; not used to invalidate saves on TSV regen */
    u32 worldSeed;
    u16 slotCount;
    u16 reserved;
    u8 familyIds[ECOLOGY_GEN_TOTAL_SLOTS];
    u8 landTimeSparseCount;
    u8 landTimeSparsePad[3];
    EcologyLandTimeSparseEntry landTimeSparse[ECOLOGY_SAVE_LAND_TIME_SPARSE_MAX];
} EcologyWorldSave;

typedef struct SaveData SaveData;
struct SAVE_MISC_DATA;

void EcologySaveClear(struct EcologyWorldSave *eco);
EcologyWorldSave *EcologySaveGetMutable(SaveData *saveData);
void EcologySaveWriteGeneration(
    struct EcologyWorldSave *eco,
    u32 worldSeed,
    u16 slotCount,
    const u16 *familyIds,
    const u8 *landTimeMasks);
BOOL EcologySaveIsValid(const struct EcologyWorldSave *eco);
u8 EcologySaveLandTimeMaskForFamily(const struct EcologyWorldSave *eco, u8 familyId);

void EcologySaveWriteFlash(struct SAVE_MISC_DATA *saveMiscData, const struct EcologyWorldSave *eco);
u8 EcologySaveVerifyMiscEcology(void *saveData);

#endif

#endif
