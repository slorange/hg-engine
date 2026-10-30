#include "../include/config.h"

#ifdef IMPLEMENT_ECOLOGY_GENERATION

#include "../include/constants/file.h"
#include "../include/constants/generated/ecology_compat.h"
#include "../include/ecology/ecology_compat_view.h"
#include "../include/ecology/ecology_compat_view.h"
#include "../include/ecology/ecology_generate.h"
#include "../include/ecology/ecology_script.h"
#include "../include/save.h"
#include "../include/types.h"
#include "../include/ecology/ecology_save.h"

extern const EcologyCompatView *gEcologyCompatView;

u32 EcologyGenerateWorldFieldAddr;

static u8 sEcologyGenDebugStage;

typedef bool8 (*EcologyGenerateWorldFn)(
    const EcologyCompatView *view,
    u32 seed,
    u16 *outSlots,
    u8 *outLandSlotTimeMasks,
    u16 outSlotCapacity,
    EcologyGenStats *statsOut);

static bool8 EcologyCallGenerateWorld(
    u32 seed,
    u16 *outSlots,
    u8 *outLandSlotTimeMasks,
    u16 outSlotCapacity)
{
    EcologyGenerateWorldFn fn;

    if (EcologyGenerateWorldFieldAddr == 0 || gEcologyCompatView == NULL) {
        return FALSE;
    }

    fn = (EcologyGenerateWorldFn)(EcologyGenerateWorldFieldAddr | 1u);
    return fn(gEcologyCompatView, seed, outSlots, outLandSlotTimeMasks, outSlotCapacity, NULL);
}

void EcologySetGenDebugStage(u8 stage)
{
    sEcologyGenDebugStage = stage;
}

u8 EcologyGetGenDebugStage(void)
{
    return sEcologyGenDebugStage;
}

static BOOL EcologyGenerateIntoSession(void *saveData, u32 seed)
{
    u16 *slots;
    u8 *landMasks;
    void *compatBlob;
    EcologyWorldSave *eco;
    BOOL ok = FALSE;

    compatBlob = EcologyCompatLoadFromFilesystem();
    if (compatBlob == NULL) {
        sEcologyGenDebugStage = 15;
        return FALSE;
    }
    if (!EcologyCompatBindBlob(compatBlob)) {
        sys_FreeMemoryEz(compatBlob);
        sEcologyGenDebugStage = 16;
        return FALSE;
    }

    slots = (u16 *)sys_AllocMemory(HEAPID_DEFAULT, ECOLOGY_GEN_TOTAL_SLOTS * sizeof(u16));
    landMasks = (u8 *)sys_AllocMemory(HEAPID_DEFAULT, ECOLOGY_GEN_TOTAL_SLOTS * sizeof(u8));
    if (slots == NULL || landMasks == NULL) {
        if (slots != NULL) {
            sys_FreeMemoryEz(slots);
        }
        if (landMasks != NULL) {
            sys_FreeMemoryEz(landMasks);
        }
        EcologyCompatUnbind();
        sys_FreeMemoryEz(compatBlob);
        sEcologyGenDebugStage = 17;
        return FALSE;
    }

    if (EcologyCallGenerateWorld(seed, slots, landMasks, ECOLOGY_GEN_TOTAL_SLOTS)) {
        eco = EcologySaveGetMutable((SaveData *)saveData);
        if (eco != NULL) {
            EcologySaveWriteGeneration(
                eco,
                seed,
                ECOLOGY_GEN_TOTAL_SLOTS,
                slots,
                landMasks);
            ok = EcologySaveIsValid(eco);
            if (!ok) {
                sEcologyGenDebugStage = 20;
            }
        } else {
            sEcologyGenDebugStage = 19;
        }
    } else if (sEcologyGenDebugStage < 22 || sEcologyGenDebugStage > 27) {
        /* EcologyGenerateWorld should set 22–27; 18 = unexpected failure */
        sEcologyGenDebugStage = 18;
    }

    sys_FreeMemoryEz(slots);
    sys_FreeMemoryEz(landMasks);

    if (!ok) {
        EcologyCompatUnbind();
        sys_FreeMemoryEz(compatBlob);
    } else {
        sEcologyGenDebugStage = 21;
    }
    return ok;
}

void EcologyRunNewGameGeneration(void *saveData)
{
    struct PlayerProfile *profile;
    u32 seed;

    if (saveData == NULL) {
        sEcologyGenDebugStage = 12;
        return;
    }

    profile = Sav2_PlayerData_GetProfileAddr(saveData);
    if (profile == NULL) {
        sEcologyGenDebugStage = 14;
        return;
    }

    seed = profile->id;
    if (seed == 0) {
        seed = 1u;
    }

    if (EcologyGenerateIntoSession(saveData, seed)) {
#if defined(ALLOW_SAVE_CHANGES)
        EcologyWorldSave *ecoFlash;

        ecoFlash = EcologySaveGetMutable((SaveData *)saveData);
        if (ecoFlash != NULL) {
            EcologySaveWriteFlash(Sav2_Misc_get(saveData), ecoFlash);
        }
#endif
        sEcologyGenDebugStage = 13;
    }
}

#endif
