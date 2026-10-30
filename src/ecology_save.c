#include "../include/config.h"

#if defined(ALLOW_SAVE_CHANGES) && defined(IMPLEMENT_ECOLOGY_GENERATION)

#include "../include/ecology/ecology_save.h"

#include "../include/constants/file.h"
#include "../include/constants/generated/ecology_compat.h"
#include "../include/ecology/ecology_compat_access.h"
#include "../include/ecology/ecology_compat_view.h"
#include "../include/save.h"
#include "../include/types.h"

extern const EcologyCompatView *gEcologyCompatView;

static struct EcologyWorldSave *sEcologySession;

static u8 EcologySaveFamilyFromSlot(u16 familyId)
{
    if (familyId == 0xFFFF) {
        return ECOLOGY_SAVE_FAMILY_EMPTY;
    }
    if (familyId >= ECOLOGY_NUM_FAMILIES) {
        return ECOLOGY_SAVE_FAMILY_EMPTY;
    }
    return (u8)familyId;
}

static void EcologySaveRebuildLandTimeSparse(struct EcologyWorldSave *eco)
{
    u8 n = 0;
    u32 i;

    eco->landTimeSparseCount = 0;

    if (eco == NULL) {
        return;
    }

    for (i = 0; i < eco->slotCount; i++) {
        u8 familyId = eco->familyIds[i];
        u8 mask;
        u8 j;

        if (familyId == ECOLOGY_SAVE_FAMILY_EMPTY || familyId >= ECOLOGY_NUM_FAMILIES) {
            continue;
        }

        if (gEcologyCompatView == NULL) {
            continue;
        }
        mask = ECO_FAMILY_INFO(familyId).landTimeMask;
        if (mask == 0) {
            continue;
        }

        for (j = 0; j < n; j++) {
            if (eco->landTimeSparse[j].familyId == familyId) {
                break;
            }
        }
        if (j < n) {
            continue;
        }
        if (n >= ECOLOGY_SAVE_LAND_TIME_SPARSE_MAX) {
            continue;
        }

        eco->landTimeSparse[n].familyId = familyId;
        eco->landTimeSparse[n].landTimeMask = mask;
        n++;
    }

    eco->landTimeSparseCount = n;
}

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
    eco->landTimeSparseCount = 0;

    for (i = 0; i < ECOLOGY_GEN_TOTAL_SLOTS; i++) {
        eco->familyIds[i] = ECOLOGY_SAVE_FAMILY_EMPTY;
    }

    for (i = 0; i < ECOLOGY_SAVE_LAND_TIME_SPARSE_MAX; i++) {
        eco->landTimeSparse[i].familyId = ECOLOGY_SAVE_FAMILY_EMPTY;
        eco->landTimeSparse[i].landTimeMask = 0;
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

    (void)landTimeMasks;

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
        eco->familyIds[i] = EcologySaveFamilyFromSlot(familyIds[i]);
    }

    for (i = count; i < ECOLOGY_GEN_TOTAL_SLOTS; i++) {
        eco->familyIds[i] = ECOLOGY_SAVE_FAMILY_EMPTY;
    }

    EcologySaveRebuildLandTimeSparse(eco);
}

u8 EcologySaveLandTimeMaskForFamily(const struct EcologyWorldSave *eco, u8 familyId)
{
    u8 i;

    if (eco == NULL) {
        return 0;
    }
    if (familyId == ECOLOGY_SAVE_FAMILY_EMPTY || familyId >= ECOLOGY_NUM_FAMILIES) {
        return 0;
    }

    for (i = 0; i < eco->landTimeSparseCount; i++) {
        if (eco->landTimeSparse[i].familyId == familyId) {
            return eco->landTimeSparse[i].landTimeMask;
        }
    }
    return 0;
}

EcologyWorldSave *EcologySaveGetMutable(SaveData *saveData)
{
    struct SAVE_MISC_DATA *misc;

    if (sEcologySession == NULL) {
        sEcologySession = (struct EcologyWorldSave *)sys_AllocMemory(
            HEAPID_DEFAULT, sizeof(struct EcologyWorldSave));
        if (sEcologySession != NULL) {
            EcologySaveClear(sEcologySession);
        }
    }

    if (sEcologySession != NULL && saveData != NULL) {
        misc = Sav2_Misc_get(saveData);
        if (misc != NULL && !EcologySaveIsValid(sEcologySession)
            && EcologySaveIsValid(&misc->ecologyWorldSave)) {
            memcpy(
                sEcologySession,
                (void *)&misc->ecologyWorldSave,
                sizeof(struct EcologyWorldSave));
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
    if (eco->landTimeSparseCount > ECOLOGY_SAVE_LAND_TIME_SPARSE_MAX) {
        return FALSE;
    }
    return TRUE;
}

void EcologySaveWriteFlash(
    struct SAVE_MISC_DATA *saveMiscData,
    const struct EcologyWorldSave *eco)
{
    if (saveMiscData == NULL || eco == NULL) {
        return;
    }
    memcpy(
        &saveMiscData->ecologyWorldSave,
        (void *)eco,
        sizeof(struct EcologyWorldSave));
}

u8 EcologySaveVerifyMiscEcology(void *saveData)
{
    struct SAVE_MISC_DATA *misc;
    struct PlayerProfile *profile;
    u32 expectSeed;
    const struct EcologyWorldSave *eco;

    if (saveData == NULL) {
        return 1;
    }
    misc = Sav2_Misc_get(saveData);
    profile = Sav2_PlayerData_GetProfileAddr(saveData);
    if (misc == NULL || profile == NULL) {
        return 1;
    }

    eco = &misc->ecologyWorldSave;
    if (!EcologySaveIsValid(eco)) {
        return 2;
    }

    expectSeed = profile->id;
    if (expectSeed == 0) {
        expectSeed = 1u;
    }
    if (eco->worldSeed != expectSeed) {
        return 5;
    }
    return 0;
}

#endif
