#include "../include/config.h"

#ifdef IMPLEMENT_ECOLOGY_GENERATION

#include "../include/constants/encounter_tables.h"
#include "../include/constants/generated/ecology_compat.h"
#include "../include/constants/save_arrays.h"
#include "../include/ecology/ecology_compat_access.h"
#include "../include/ecology/ecology_compat_view.h"
#include "../include/ecology/ecology_encounter.h"
#include "../include/ecology/ecology_generate.h"
#include "../include/ecology/ecology_save.h"
#include "../include/local_field_data.h"
#include "../include/pokemon.h"
#include "../include/rtc.h"
#include "../include/save.h"
#include "../include/types.h"

extern FieldSystem *gFieldSysPtr;
extern FieldSystem *sPersistFieldSysPtr;

u8 LONG_CALL MapHeader_GetWildEncounterBank(u32 mapId);

static FieldSystem *EcologyResolveFieldSystem(void)
{
    if (gFieldSysPtr != NULL) {
        return gFieldSysPtr;
    }
    return sPersistFieldSysPtr;
}

static BOOL EcologyResolveMapId(u16 *mapIdOut)
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

    fsys = EcologyResolveFieldSystem();
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

static s8 EcologyFindGroupForEncBank(u8 encBank)
{
    u8 groupId;

    if (gEcologyCompatView == NULL) {
        return -1;
    }

    for (groupId = 0; groupId < ECOLOGY_NUM_GROUPS; groupId++) {
        EcologyGroupInfo group = ECO_GROUPS(groupId);
        u8 i;

        for (i = 0; i < group.encdataCount; i++) {
            u16 encdataId = gEcologyCompatView->groupEncdataIds[group.encdataOffset + i];

            if (encdataId == encBank) {
                return (s8)groupId;
            }
        }
    }

    return -1;
}

static u8 EcologyWildParamToTimeBit(TimeOfDayWildParam param)
{
    switch (param) {
    case TIMEOFDAY_WILD_MORN:
        return ECOLOGY_TIME_MORNING;
    case TIMEOFDAY_WILD_DAY:
        return ECOLOGY_TIME_DAY;
    case TIMEOFDAY_WILD_NITE:
        return ECOLOGY_TIME_NIGHT;
    default:
        return ECOLOGY_TIME_ALL;
    }
}

static u16 EcologyRollAssignedSpecies(u8 method)
{
    u16 mapId;
    u8 encBank;
    s8 groupId;
    u8 capacity;
    u16 layoutIndex;
    u16 base;
    u8 periodBit;
    u8 eligible[ECOLOGY_GEN_MAX_SLOTS_PER_BUCKET];
    u8 eligibleCount;
    u8 pickIndex;
    u16 familyId;
    u16 species;
    u8 i;
    u16 slotBases[ECOLOGY_NUM_GROUPS * ECOLOGY_METHOD_COUNT];
    const EcologyWorldSave *eco;

    if (method >= ECOLOGY_METHOD_COUNT) {
        return 0;
    }

    eco = EcologySaveGetMutable(SaveBlock2_get());
    if (eco == NULL || !EcologySaveIsValid(eco)) {
        return 0;
    }
    if (!EcologyCompatSessionEnsure()) {
        return 0;
    }
    if (gEcologyCompatView == NULL) {
        return 0;
    }

    if (EcologyGenBuildSlotLayout(slotBases) == 0) {
        return 0;
    }

    if (!EcologyResolveMapId(&mapId)) {
        return 0;
    }

    encBank = MapHeader_GetWildEncounterBank(mapId);
    if (encBank == ENCDATA_NA) {
        return 0;
    }

    groupId = EcologyFindGroupForEncBank(encBank);
    if (groupId < 0) {
        return 0;
    }

    layoutIndex = (u16)((u16)groupId * (u16)ECOLOGY_METHOD_COUNT + (u16)method);
    capacity = ECO_METHOD_SLOTS(layoutIndex);
    if (capacity == 0) {
        return 0;
    }
    if (capacity > ECOLOGY_GEN_MAX_SLOTS_PER_BUCKET) {
        capacity = ECOLOGY_GEN_MAX_SLOTS_PER_BUCKET;
    }

    base = EcologyGenSlotLayoutBase((u8)groupId, method, slotBases);

    periodBit = EcologyWildParamToTimeBit(GF_RTC_GetTimeOfDayWildParam());
    eligibleCount = 0;

    for (i = 0; i < capacity; i++) {
        u16 slotIndex = (u16)(base + i);
        u16 slotFamily;
        u8 slotMask;

        if (slotIndex >= eco->slotCount) {
            continue;
        }

        slotFamily = eco->familyIds[slotIndex];
        if (slotFamily == ECOLOGY_SAVE_FAMILY_EMPTY || slotFamily >= ECOLOGY_NUM_FAMILIES) {
            continue;
        }

        if (method == ECOLOGY_METHOD_LAND) {
            slotMask = EcologySaveLandTimeMaskForFamily(eco, slotFamily);
            if (slotMask != 0 && (slotMask & periodBit) == 0) {
                continue;
            }
        }

        eligible[eligibleCount++] = i;
    }

    if (eligibleCount == 0) {
        return 0;
    }

    pickIndex = eligible[gf_rand() % eligibleCount];
    familyId = eco->familyIds[(u16)(base + eligible[pickIndex])];
    species = ECO_FAMILY_INFO(familyId).baseSpecies;
    if (species == 0) {
        return 0;
    }

    return species;
}

u16 EcologyApplySpeciesOverrideForMethod(u16 vanillaSpecies, u8 ecologyMethod)
{
    u16 ecologySpecies;

    if (ecologyMethod >= ECOLOGY_METHOD_COUNT) {
        return vanillaSpecies;
    }

    ecologySpecies = EcologyRollAssignedSpecies(ecologyMethod);
    if (ecologySpecies != 0) {
        return ecologySpecies;
    }

    return vanillaSpecies;
}

u16 EcologyApplyGrassSpeciesOverride(u16 vanillaSpecies)
{
    u8 methodScratch;
    u8 method;

    methodScratch = EcologyActiveMethodRef;
    if (methodScratch == 0) {
        return vanillaSpecies;
    }
    EcologyActiveMethodRef = 0;
    method = (u8)(methodScratch - 1u);

    return EcologyApplySpeciesOverrideForMethod(vanillaSpecies, method);
}

#endif
