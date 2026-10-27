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

static BOOL EcologyGenerateIntoSession(void *saveData, u32 seed)
{
    u16 *slots;
    u8 *landMasks;
    void *compatBlob;
    EcologyWorldSave *eco;
    BOOL ok = FALSE;

    compatBlob = EcologyCompatLoadFromFilesystem();
    if (compatBlob == NULL || !EcologyCompatBindBlob(compatBlob)) {
        if (compatBlob != NULL) {
            sys_FreeMemoryEz(compatBlob);
        }
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
        }
    }

    sys_FreeMemoryEz(slots);
    sys_FreeMemoryEz(landMasks);
    EcologyCompatUnbind();
    sys_FreeMemoryEz(compatBlob);
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
        return FALSE;
    }

    eco = EcologySaveGetMutable((SaveData *)saveData);
    if (eco != NULL && EcologySaveIsValid(eco)) {
        return TRUE;
    }

    profile = Sav2_PlayerData_GetProfileAddr(saveData);
    if (profile == NULL) {
        return FALSE;
    }

    seed = profile->id;
    if (seed == 0) {
        seed = 1u;
    }

    return EcologyGenerateIntoSession(saveData, seed);
}

#endif
