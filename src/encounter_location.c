#include "encounter_location.h"
#include "constants/save_arrays.h"
#include "local_field_data.h"
#include "save.h"
#include "script.h"

extern FieldSystem *sPersistFieldSysPtr;

FieldSystem *EncounterResolveFieldSystem(void)
{
    if (gFieldSysPtr != NULL) {
        return gFieldSysPtr;
    }

    return sPersistFieldSysPtr;
}

// SaveBlock2_get() stays valid during battle; fsys->savedata/location often do not.
BOOL EncounterResolveMapId(u16 *mapIdOut)
{
    SaveData *saveData = SaveBlock2_get();
    LocalFieldData *localFieldData;
    FieldSystem *fsys;

    if (saveData != NULL) {
        localFieldData = (LocalFieldData *)SaveArray_Get(saveData, SAVE_LOCAL_FIELD_DATA);
        if (localFieldData != NULL) {
            *mapIdOut = (u16)localFieldData->currentPosition.mapId;
            return TRUE;
        }
    }

    fsys = EncounterResolveFieldSystem();
    if (fsys == NULL) {
        return FALSE;
    }

    if (fsys->savedata != NULL) {
        localFieldData = (LocalFieldData *)SaveArray_Get(fsys->savedata, SAVE_LOCAL_FIELD_DATA);
        if (localFieldData != NULL) {
            *mapIdOut = (u16)localFieldData->currentPosition.mapId;
            return TRUE;
        }
    }

    if (fsys->location != NULL) {
        *mapIdOut = (u16)fsys->location->mapId;
        return TRUE;
    }

    return FALSE;
}

