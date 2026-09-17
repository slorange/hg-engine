#include "config.h"
#include "constants/encounter_tables.h"
#include "constants/generated/wild_level_caps.h"
#include "constants/save_arrays.h"
#include "debug.h"
#include "local_field_data.h"
#include "pokemon.h"
#include "save.h"
#include "script.h"
#include "encounter_species_stage.h"
#include "types.h"

#define VAR_PLAYER_START_CITY 0x4031
#define WLC_DEBUG_MAGIC 0x43444C57u

enum {
    WLC_FAIL_NONE = 0,
    WLC_FAIL_LOCATION_NULL = 1,
    WLC_FAIL_ENCBANK_NA = 2,
    WLC_FAIL_ENCBANK_RANGE = 3,
    WLC_FAIL_START_CITY = 4,
    WLC_FAIL_CAP_ZERO = 5,
    WLC_FAIL_CAP_BELOW_MIN = 6,
};

typedef struct WildLevelCapCache {
    u8 valid;
    u8 cap;
    u8 failReason;
    u8 encBank;
    u16 mapId;
} WildLevelCapCache;

typedef struct WildLevelCapDebug {
    u32 magic;
    u8 failReason;
    u8 cachedCap;
    u8 appliedLevel;
    u8 usedCachedCap;
    u16 mapId;
    u8 encBank;
    u8 startCityVar;
    u8 startCityIndex;
    u8 pad;
    u32 argFsys;
    u32 persistFsys;
    u32 resolvedFsys;
    u32 gFieldSysPtrVal;
} WildLevelCapDebug;

extern const u8 sWildLevelCaps[WILD_LEVEL_CAP_NUM_START_CITIES][WILD_LEVEL_CAP_NUM_ENCOUNTER_AREAS];
extern FieldSystem *sPersistFieldSysPtr;
// Runtime address of field-overlay sLevelUpEvoTablesData (patched in build/output.bin).
u32 LevelUpEvoTablesFieldAddr = 0;
u32 SyntheticEvoEdgesFieldAddr = 0;
extern WildLevelCapDebug sWildLevelCapDebug;
extern WildLevelCapCache sWildCapCache;

u8 LONG_CALL MapHeader_GetWildEncounterBank(u32 mapId);

static void TouchWildLevelCapDebug(void)
{
    sWildLevelCapDebug.magic = WLC_DEBUG_MAGIC;
}

static void ClearCachedWildLevelCap(void)
{
    sWildCapCache.valid = FALSE;
}

static FieldSystem *ResolveFieldSystem(void)
{
    if (gFieldSysPtr != NULL) {
        return gFieldSysPtr;
    }

    return sPersistFieldSysPtr;
}

// SaveBlock2_get() stays valid during battle; fsys->savedata/location often do not.
static BOOL ResolveMapId(u16 *mapIdOut)
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

    fsys = ResolveFieldSystem();
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

static u8 ResolveStartCityIndex(u8 startCityVar)
{
    if (startCityVar < WILD_LEVEL_CAP_NUM_START_CITIES) {
        return startCityVar;
    }

    return 0;
}

static u8 ComputeWildLevelCap(u8 *failReason)
{
    u8 startCityVar;
    u8 startCityIndex;
    u8 encBank;
    u8 cap;
    u16 mapId;

    TouchWildLevelCapDebug();
    sWildLevelCapDebug.mapId = 0;
    sWildLevelCapDebug.encBank = ENCDATA_NA;
    sWildLevelCapDebug.startCityVar = 0;
    sWildLevelCapDebug.startCityIndex = 0;

    if (!ResolveMapId(&mapId)) {
        *failReason = WLC_FAIL_LOCATION_NULL;
        return WILD_LEVEL_CAP_MIN;
    }

    startCityVar = (u8)GetScriptVar(VAR_PLAYER_START_CITY);
    startCityIndex = ResolveStartCityIndex(startCityVar);

    encBank = MapHeader_GetWildEncounterBank(mapId);

    sWildLevelCapDebug.mapId = mapId;
    sWildLevelCapDebug.encBank = encBank;
    sWildLevelCapDebug.startCityVar = startCityVar;
    sWildLevelCapDebug.startCityIndex = startCityIndex;

    if (encBank == ENCDATA_NA) {
        *failReason = WLC_FAIL_ENCBANK_NA;
        return WILD_LEVEL_CAP_MIN;
    }

    if (encBank >= WILD_LEVEL_CAP_NUM_ENCOUNTER_AREAS) {
        *failReason = WLC_FAIL_ENCBANK_RANGE;
        return WILD_LEVEL_CAP_MIN;
    }

    if (startCityIndex >= WILD_LEVEL_CAP_NUM_START_CITIES) {
        *failReason = WLC_FAIL_START_CITY;
        return WILD_LEVEL_CAP_MIN;
    }

    cap = sWildLevelCaps[startCityIndex][encBank];

    if (cap == 0) {
        *failReason = WLC_FAIL_CAP_ZERO;
        return WILD_LEVEL_CAP_MIN;
    }

    if (cap < WILD_LEVEL_CAP_MIN) {
        *failReason = WLC_FAIL_CAP_BELOW_MIN;
        return WILD_LEVEL_CAP_MIN;
    }

    *failReason = WLC_FAIL_NONE;
    return cap;
}

// Encounter levels never go below 2 (no wild level 1).
#define WILD_ENCOUNTER_LEVEL_MIN 2
#define WILD_LEVEL_BABY_SPLIT_MIN_CAP 10
#define WILD_LEVEL_BABY_ROLL_PERCENT 15
#define WILD_LEVEL_BABY_MAX 7

static u8 RollWildLevelUniform(u8 lo, u8 hi)
{
    u8 span;

    if (hi <= lo) {
        return lo;
    }

    span = hi - lo + 1;
    return lo + (u8)(gf_rand() % span);
}

static u8 RollWildLevelAdultBand(u8 cap)
{
    u8 adultLo;

    adultLo = (u8)(((u16)cap * 9u) / 10u);
    if (adultLo >= 2) {
        adultLo = (u8)(adultLo - 2);
    }
    if (adultLo < WILD_ENCOUNTER_LEVEL_MIN) {
        adultLo = WILD_ENCOUNTER_LEVEL_MIN;
    }
    if (adultLo > cap) {
        adultLo = cap;
    }

    return RollWildLevelUniform(adultLo, cap);
}

static u8 RollWildLevel(u8 cap)
{
    if (cap <= WILD_ENCOUNTER_LEVEL_MIN) {
        return WILD_ENCOUNTER_LEVEL_MIN;
    }

    if (cap < WILD_LEVEL_BABY_SPLIT_MIN_CAP) {
        return RollWildLevelAdultBand(cap);
    }

    if ((gf_rand() % 100) < WILD_LEVEL_BABY_ROLL_PERCENT) {
        return RollWildLevelUniform(WILD_ENCOUNTER_LEVEL_MIN, WILD_LEVEL_BABY_MAX);
    }

    return RollWildLevelAdultBand(cap);
}

#ifdef DEBUG_WILD_LEVEL_CAP_LEVELS
static u8 DiagnosticWildLevel(u8 failReason, u8 cap)
{
    switch (failReason) {
    case WLC_FAIL_LOCATION_NULL:
        return 4;
    case WLC_FAIL_ENCBANK_NA:
        return 5;
    case WLC_FAIL_ENCBANK_RANGE:
        return 6;
    case WLC_FAIL_START_CITY:
        return 7;
    case WLC_FAIL_CAP_ZERO:
        return 8;
    case WLC_FAIL_CAP_BELOW_MIN:
        return 9;
    case WLC_FAIL_NONE:
        return cap;
    default:
        return 10;
    }
}
#endif

static u8 ChooseWildLevel(u8 failReason, u8 cap, u8 encBank, u8 usedCachedCap, u16 mapId)
{
#ifdef DEBUG_WILD_LEVEL_CAP_LEVELS
    (void)encBank;
    (void)usedCachedCap;
    (void)mapId;
    return DiagnosticWildLevel(failReason, cap);
#elif defined(DEBUG_WILD_LEVEL_CAP_EXACT)
    if (failReason != WLC_FAIL_NONE || cap < WILD_LEVEL_CAP_MIN) {
        return WILD_LEVEL_CAP_MIN;
    }
    return cap;
#else
    if (failReason != WLC_FAIL_NONE) {
        return WILD_LEVEL_CAP_MIN;
    }
    return RollWildLevel(cap);
#endif
}

static void ApplyWildSpeciesStageForLevel(struct PartyPokemon *pp, u8 level)
{
    u16 species;
    u16 adjusted;
    u32 formZero = 0;

    if (LevelUpEvoTablesFieldAddr == 0 || SyntheticEvoEdgesFieldAddr == 0) {
        return;
    }

    species = (u16)GetMonData(pp, MON_DATA_SPECIES, NULL);
    adjusted = AdjustEncounterSpeciesForLevel(species, level);

    if (adjusted == species) {
        return;
    }

    SetMonData(pp, MON_DATA_SPECIES, &adjusted);
    SetMonData(pp, MON_DATA_SPECIES_NAME, NULL);
    SetMonData(pp, MON_DATA_FORM, &formZero);
}

static void SetWildMonLevel(struct PartyPokemon *pp, u8 level)
{
    u16 species;
    u32 exp;

    species = (u16)GetMonData(pp, MON_DATA_SPECIES, NULL);
    exp = PokeLevelExpGet(species, level);
    SetMonData(pp, MON_DATA_EXPERIENCE, &exp);
    SetMonData(pp, MON_DATA_LEVEL, &level);
    pp->party.level = level;
}

// Called from WildEncSingle / WildWaterEncSingle while FieldSystem is still valid.
void CacheWildLevelCapFromFieldSystem(FieldSystem *fsysArg)
{
    FieldSystem *fsys;
    u8 failReason;

    TouchWildLevelCapDebug();
    sWildLevelCapDebug.argFsys = (u32)fsysArg;
    sWildLevelCapDebug.persistFsys = (u32)sPersistFieldSysPtr;
    sWildLevelCapDebug.gFieldSysPtrVal = (u32)gFieldSysPtr;

    fsys = ResolveFieldSystem();
    sWildLevelCapDebug.resolvedFsys = (u32)fsys;

    sWildCapCache.cap = ComputeWildLevelCap(&failReason);
    sWildCapCache.failReason = failReason;
    sWildCapCache.mapId = sWildLevelCapDebug.mapId;
    sWildCapCache.encBank = sWildLevelCapDebug.encBank;
    sWildCapCache.valid = (failReason == WLC_FAIL_NONE);

    sWildLevelCapDebug.failReason = failReason;
    sWildLevelCapDebug.cachedCap = sWildCapCache.cap;

#ifdef DEBUG_WILD_LEVEL_CAPS
    debug_printf(
        "WLC cache arg=%08X resolved=%08X map=%u enc=%u start=%u idx=%u cap=%u fail=%u\n",
        sWildLevelCapDebug.argFsys,
        sWildLevelCapDebug.resolvedFsys,
        sWildLevelCapDebug.mapId,
        sWildLevelCapDebug.encBank,
        sWildLevelCapDebug.startCityVar,
        sWildLevelCapDebug.startCityIndex,
        sWildCapCache.cap,
        failReason);
#endif
}

static u8 GetWildLevelCapForCurrentMap(u8 *usedCachedCap, u8 *failReason, u8 *encBank)
{
    u8 cap;

    if (sWildCapCache.valid && sWildCapCache.failReason == WLC_FAIL_NONE) {
        *usedCachedCap = TRUE;
        *failReason = WLC_FAIL_NONE;
        *encBank = sWildCapCache.encBank;
        sWildLevelCapDebug.mapId = sWildCapCache.mapId;
        sWildLevelCapDebug.encBank = sWildCapCache.encBank;
        return sWildCapCache.cap;
    }

    *usedCachedCap = FALSE;
    cap = ComputeWildLevelCap(failReason);
    *encBank = sWildLevelCapDebug.encBank;
    return cap;
}

// Called from modify_species_encounter_data (normal wilds only — not _rare / roamers).
void ApplyWildDistanceLevelCapToMon(struct PartyPokemon *pp)
{
    u8 cap;
    u8 level;
    u8 encBank;
    u8 usedCachedCap;
    u8 failReason;

    if (pp == NULL) {
        return;
    }

    TouchWildLevelCapDebug();
    cap = GetWildLevelCapForCurrentMap(&usedCachedCap, &failReason, &encBank);
    level = ChooseWildLevel(failReason, cap, encBank, usedCachedCap, sWildLevelCapDebug.mapId);
    // Stage adjust needs field-overlay rodata; skip safely if build-time patch missing.
    ApplyWildSpeciesStageForLevel(pp, level);
    SetWildMonLevel(pp, level);
    RecalcPartyPokemonStats(pp);

    sWildLevelCapDebug.usedCachedCap = usedCachedCap;
    sWildLevelCapDebug.appliedLevel = level;
    sWildLevelCapDebug.cachedCap = cap;
    sWildLevelCapDebug.failReason = failReason;

#ifdef DEBUG_WILD_LEVEL_CAPS
    debug_printf(
        "WLC apply cached=%u cap=%u lvl=%u fail=%u map=%u enc=%u\n",
        usedCachedCap,
        cap,
        level,
        failReason,
        sWildLevelCapDebug.mapId,
        sWildLevelCapDebug.encBank);
#endif

    ClearCachedWildLevelCap();
}
