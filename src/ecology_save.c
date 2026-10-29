#include "../include/config.h"

#if defined(ALLOW_SAVE_CHANGES) && defined(IMPLEMENT_ECOLOGY_GENERATION)

#include "../include/ecology/ecology_save.h"

#include "../include/constants/file.h"
#include "../include/constants/generated/ecology_compat.h"
#include "../include/save.h"
#include "../include/types.h"

static struct EcologyWorldSave *sEcologySession;

void EcologySaveClear(struct EcologyWorldSave *eco)
{
    u32 i;

    if (eco == NULL) {
        return;
    }

    eco->magic = 0;
    eco->compatVersion = 0;
    eco->worldSeed = 0;
    eco->slotCount = 0;
    eco->reserved = 0;

    for (i = 0; i < ECOLOGY_GEN_TOTAL_SLOTS; i++) {
        eco->familyIds[i] = 0;
        eco->landTimeMasks[i] = 0;
    }
}

void EcologySaveWriteGeneration(
    struct EcologyWorldSave *eco,
    u32 worldSeed,
    u16 slotCount,
    const u16 *familyIds,
    const u8 *landTimeMasks)
{
    u32 i;
    u16 count;

    if (eco == NULL || familyIds == NULL) {
        return;
    }

    count = slotCount;
    if (count > ECOLOGY_GEN_TOTAL_SLOTS) {
        count = ECOLOGY_GEN_TOTAL_SLOTS;
    }

    eco->magic = ECOLOGY_SAVE_MAGIC;
    eco->compatVersion = ECOLOGY_COMPAT_VERSION;
    eco->worldSeed = worldSeed;
    eco->slotCount = count;
    eco->reserved = 0;

    for (i = 0; i < count; i++) {
        eco->familyIds[i] = familyIds[i];
        eco->landTimeMasks[i] = (landTimeMasks != NULL) ? landTimeMasks[i] : 0;
    }

    for (i = count; i < ECOLOGY_GEN_TOTAL_SLOTS; i++) {
        eco->familyIds[i] = 0;
        eco->landTimeMasks[i] = 0;
    }
}

EcologyWorldSave *EcologySaveGetMutable(SaveData *saveData)
{
    (void)saveData;
    if (sEcologySession == NULL) {
        sEcologySession = (struct EcologyWorldSave *)sys_AllocMemory(
            HEAPID_DEFAULT, sizeof(struct EcologyWorldSave));
        if (sEcologySession != NULL) {
            EcologySaveClear(sEcologySession);
        }
    }
    return sEcologySession;
}

BOOL EcologySaveIsValid(const struct EcologyWorldSave *eco)
{
    if (eco == NULL) {
        return FALSE;
    }
    if (eco->magic != ECOLOGY_SAVE_MAGIC) {
        return FALSE;
    }
    if (eco->slotCount == 0 || eco->slotCount > ECOLOGY_GEN_TOTAL_SLOTS) {
        return FALSE;
    }
    if (eco->compatVersion != ECOLOGY_COMPAT_VERSION) {
        return FALSE;
    }
    return TRUE;
}

#endif
