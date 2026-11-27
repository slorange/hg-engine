#include "config.h"

#ifdef IMPLEMENT_ECOLOGY_GENERATION

#include "constants/ability.h"
#include "constants/battle_constants.h"
#include "constants/encounter_tables.h"
#include "constants/file.h"
#include "constants/maps.h"
#include "constants/generated/ecology_compat.h"
#include "ecology/ecology_compat_access.h"
#include "ecology/ecology_compat_view.h"
#include "ecology/ecology_encounter.h"
#include "ecology/ecology_generate.h"
#include "ecology/ecology_save.h"
#include "encounter_location.h"
#include "encounter_overlay.h"
#include "pokemon.h"
#include "rtc.h"
#include "save.h"
#include "types.h"

u8 LONG_CALL MapHeader_GetWildEncounterBank(u32 mapId);

static BOOL EcologyHintBankHasMethod(u8 bank, u8 method)
{
    // Headbutt availability comes from the ecology location's tree group.
    if (method == ECOLOGY_METHOD_HEADBUTT)
        return TRUE;

    // EncounterData starts with rates for walk, Surf, Rock Smash, then the rods.
    static const u8 rateOffsets[] = {0, 1, 3, 4, 5, 2};
    u8 rate = 0;
    ReadFromNarcMemberByIdPair(&rate, ARC_WILD_ENCOUNTERS, bank, rateOffsets[method], sizeof(rate));
    return rate != 0;
}

BOOL EcologyFindHint(u16 species, struct EcologyHint *hint)
{
    const EcologyWorldSave *eco = EcologySaveGetMutable(SaveBlock2_get());
    u16 slotBases[ECOLOGY_NUM_GROUPS * ECOLOGY_METHOD_COUNT];
    u16 family;
    hint->level = 0;
    if (!EcologySaveIsValid(eco) || eco->compatVersion != ECOLOGY_COMPAT_VERSION
        || !EcologyCompatSessionEnsure()
        || EcologyGenBuildSlotLayout(slotBases) == 0) {
        return FALSE;
    }

    for (family = 0; family < ECOLOGY_NUM_FAMILIES; family++) {
        if (ECO_FAMILY_INFO(family).baseSpecies == species)
            break;
    }
    if (family == ECOLOGY_NUM_FAMILIES)
        return FALSE;

    for (u8 group = 0; group < ECOLOGY_NUM_GROUPS; group++) {
        EcologyGroupInfo info = ECO_GROUPS(group);
        for (u8 method = 0; method < ECOLOGY_METHOD_COUNT; method++) {
            u16 index = group * ECOLOGY_METHOD_COUNT + method;
            u16 base = EcologyGenSlotLayoutBase(group, method, slotBases);
            u8 count = ECO_METHOD_SLOTS(index);
            u8 slot;
            for (slot = 0; slot < count; slot++) {
                if (base + slot < eco->slotCount && eco->familyIds[base + slot] == family)
                    break;
            }
            if (slot == count)
                continue;

            for (u8 i = 0; i < info.encdataCount; i++) {
                u8 bank = gEcologyCompatView->groupEncdataIds[info.encdataOffset + i];
                u8 cap = GetWildLevelCapForEncounterBank(bank);
                // Use the ordinary roll floor so a rare baby roll doesn't mask a badge gate.
                u8 level = (u8)(cap * 9 / 10);
                level = level > 4 ? level - 2 : 2;
                if (hint->level && (level > hint->level
                    || (level == hint->level && method >= hint->method))) {
                    continue;
                }
                if (!EcologyHintBankHasMethod(bank, method))
                    continue;
                for (u16 map = 0; map < MAP_ID_MAX; map++) {
                    if (MapHeader_GetWildEncounterBank(map) == bank) {
                        hint->mapId = map;
                        hint->method = method;
                        hint->level = level;
                        break;
                    }
                }
            }
        }
    }
    return hint->level != 0;
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

static u16 RollEcologySpecies(u8 encBank, u8 method, u8 ability)
{
    s8 groupId;
    u8 capacity;
    u16 layoutIndex;
    u16 base;
    u8 periodBit;
    u8 eligible[ECOLOGY_GEN_MAX_SLOTS_PER_BUCKET];
    u8 eligibleCount;
    u8 favored[ECOLOGY_GEN_MAX_SLOTS_PER_BUCKET];
    u8 favoredCount = 0;
    u8 favoredType = TYPE_NORMAL;
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
    if (!EcologySaveIsValid(eco) || eco->compatVersion != ECOLOGY_COMPAT_VERSION) {
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

    if (ability == ABILITY_STATIC || ability == ABILITY_MAGNET_PULL) {
        if (gf_rand() % 2 == 0) {
            favoredType = ability == ABILITY_STATIC ? TYPE_ELECTRIC : TYPE_STEEL;
        }
    }

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

        if (method == ECOLOGY_METHOD_LAND
            && (ECO_GROUP_FLAGS((u8)groupId) & ECOLOGY_GROUP_FLAG_CAVE_IGNORE_LAND_TIME) == 0) {
            slotMask = EcologySaveLandTimeMaskForFamily(eco, slotFamily);
            if (slotMask != 0 && (slotMask & periodBit) == 0) {
                continue;
            }
        }

        eligible[eligibleCount++] = i;
        if (favoredType != TYPE_NORMAL) {
            species = ECO_FAMILY_INFO(slotFamily).baseSpecies;
            if (species != 0 && (PokePersonalParaGet(species, PERSONAL_TYPE_1) == favoredType
                              || PokePersonalParaGet(species, PERSONAL_TYPE_2) == favoredType)) {
                favored[favoredCount++] = i;
            }
        }
    }

    if (eligibleCount == 0) {
        return 0;
    }

    // Uniform selection among slots eligible at the current time, including the park.
    pickIndex = favoredCount != 0 ? favored[gf_rand() % favoredCount]
                                  : eligible[gf_rand() % eligibleCount];
    familyId = eco->familyIds[(u16)(base + pickIndex)];
    species = ECO_FAMILY_INFO(familyId).baseSpecies;
    if (species == 0) {
        return 0;
    }

    return species;
}

u16 EcologyRollSpeciesForEncounterBank(u8 encBank, u8 method)
{
    return RollEcologySpecies(encBank, method, 0);
}

u16 EcologyApplySpeciesWithLeadAbility(u16 vanillaSpecies, u8 ecologyMethod, u8 ability)
{
    u16 ecologySpecies;
    u16 mapId;

    if (ecologyMethod >= ECOLOGY_METHOD_COUNT) {
        return vanillaSpecies;
    }

    if (!EncounterResolveMapId(&mapId)) {
        return vanillaSpecies;
    }
    ecologySpecies = RollEcologySpecies(MapHeader_GetWildEncounterBank(mapId), ecologyMethod, ability);
    if (ecologySpecies != 0) {
        return ecologySpecies;
    }

    return vanillaSpecies;
}

u16 EcologyApplySpeciesOverrideForMethod(u16 vanillaSpecies, u8 ecologyMethod)
{
    return EcologyApplySpeciesWithLeadAbility(vanillaSpecies, ecologyMethod, 0);
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

#else

#include "encounter_overlay.h"

BOOL EcologyFindHint(UNUSED u16 species, UNUSED struct EcologyHint *hint)
{
    return FALSE;
}

#endif
