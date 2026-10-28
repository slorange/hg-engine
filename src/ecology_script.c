#include "../include/config.h"

#ifdef IMPLEMENT_ECOLOGY_GENERATION

#include "../include/constants/file.h"
#include "../include/constants/generated/ecology_compat.h"
#include "../include/ecology/ecology_compat_view.h"
#include "../include/ecology/ecology_generate.h"
#include "../include/ecology/ecology_script.h"
#include "../include/save.h"
#include "../include/types.h"
#include "../include/ecology/ecology_save.h"

static u8 sEcologyGenDebugStage;

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

    if (EcologyGenerateWorld(seed, slots, landMasks, ECOLOGY_GEN_TOTAL_SLOTS, NULL)) {
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

BOOL EcologyEnsureWorldGenerated(void *saveData)
{
    struct PlayerProfile *profile;
    EcologyWorldSave *eco;
    u32 seed;

    if (saveData == NULL) {
        saveData = SaveBlock2_get();
    }
    if (saveData == NULL) {
        sEcologyGenDebugStage = 12;
        return FALSE;
    }

    eco = EcologySaveGetMutable((SaveData *)saveData);
    if (eco != NULL && EcologySaveIsValid(eco)) {
        sEcologyGenDebugStage = 13;
        return TRUE;
    }

    profile = Sav2_PlayerData_GetProfileAddr(saveData);
    if (profile == NULL) {
        sEcologyGenDebugStage = 14;
        return FALSE;
    }

    seed = profile->id;
    if (seed == 0) {
        seed = 1u;
    }

    return EcologyGenerateIntoSession(saveData, seed);
}

#endif
