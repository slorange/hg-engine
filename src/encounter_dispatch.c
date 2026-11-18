#include "config.h"
#include "encounter_overlay.h"
#include "constants/file.h"
#include "constants/battle_constants.h"
#include "overlay.h"

// Permanent field-table bindings; data outlives temporary encounter code.
u32 LevelUpEvoTablesFieldAddr, SyntheticEvoEdgesFieldAddr, WildLevelCapsFieldAddr;
u32 WildSpeciesHeldCommonFieldAddr, WildSpeciesHeldRareFieldAddr;
extern u8 sWildCapCache[];

const struct EncounterOverlayApi *EncounterOverlay_Open(BOOL *owned)
{
    const struct EncounterOverlayApi *api = (const void *)ENCOUNTER_OVERLAY_ADDRESS;
    *owned = FALSE;
    if (!IsOverlayLoaded(OVERLAY_ENCOUNTER_GENERATION)) {
        if (!HandleLoadOverlay(OVERLAY_ENCOUNTER_GENERATION, 2))
            return NULL;
        *owned = TRUE;
    }
    if (api->magic != ENCOUNTER_OVERLAY_MAGIC) {
        EncounterOverlay_Close(*owned);
        *owned = FALSE;
        return NULL;
    }
    return api;
}

void EncounterOverlay_Close(BOOL owned)
{
    if (owned)
        UnloadOverlayByID(OVERLAY_ENCOUNTER_GENERATION);
}

void CacheWildLevelCapFromFieldSystem(FieldSystem *fsys)
{
    BOOL owned;
    const struct EncounterOverlayApi *api;
    sWildCapCache[0] = 0;
    api = EncounterOverlay_Open(&owned);
    if (api == NULL)
        return;
    api->cacheCap(fsys);
    EncounterOverlay_Close(owned);
}

void ApplyWildDistanceLevelCapToMon(struct PartyPokemon *mon)
{
    BOOL owned;
    const struct EncounterOverlayApi *api;
    api = EncounterOverlay_Open(&owned);
    if (api == NULL)
        return;
    api->applyDistanceCap(mon);
    EncounterOverlay_Close(owned);
}

u8 GetWildLevelCapForEncounterBank(u8 bank)
{
    BOOL owned;
    const struct EncounterOverlayApi *api;
    u8 result;
    api = EncounterOverlay_Open(&owned);
    if (api == NULL)
        return 2;
    result = api->capForBank(bank);
    EncounterOverlay_Close(owned);
    return result;
}

u8 RollWildLevel(u8 cap, BOOL *baby)
{
    BOOL owned;
    const struct EncounterOverlayApi *api;
    u8 result;
    *baby = FALSE;
    api = EncounterOverlay_Open(&owned);
    if (api == NULL)
        return 2;
    result = api->rollLevel(cap, baby);
    EncounterOverlay_Close(owned);
    return result;
}

void ApplyWildEncounterLevelAndStage(struct PartyPokemon *mon, u8 level, BOOL baby)
{
    BOOL owned;
    const struct EncounterOverlayApi *api;
    api = EncounterOverlay_Open(&owned);
    if (api == NULL)
        return;
    api->applyLevelAndStage(mon, level, baby);
    EncounterOverlay_Close(owned);
}

void WildMonApplyHeldItemForEncounter(struct PartyPokemon *mon)
{
    BOOL owned;
    const struct EncounterOverlayApi *api;
    api = EncounterOverlay_Open(&owned);
    if (api == NULL)
        return;
    api->applyHeldItem(mon);
    EncounterOverlay_Close(owned);
}

void WildMonSetRandomHeldItem_hook(struct PartyPokemon *mon, u32 battleType, u32 compoundEyes)
{
    BOOL owned;
    const struct EncounterOverlayApi *api;
    if (battleType & (BATTLE_TYPE_TRAINER | BATTLE_TYPE_FRONTIER))
        return;
    api = EncounterOverlay_Open(&owned);
    if (api == NULL)
        return;
    api->setHeldItem(mon, battleType, compoundEyes);
    EncounterOverlay_Close(owned);
}

u16 WildEncounterFinalize(struct PartyPokemon *mon, u16 species)
{
    BOOL owned;
    const struct EncounterOverlayApi *api;
    u16 result;
    api = EncounterOverlay_Open(&owned);
    if (api == NULL)
        return species;
    result = api->finalize(mon, species);
    EncounterOverlay_Close(owned);
    return result;
}

u16 WildEncounterFinalizeForEncount(struct PartyPokemon *mon, u16 species, u32 method, u32 rod)
{
    BOOL owned;
    const struct EncounterOverlayApi *api;
    u16 result;
    api = EncounterOverlay_Open(&owned);
    if (api == NULL)
        return species;
    result = api->finalizeForEncount(mon, species, method, rod);
    EncounterOverlay_Close(owned);
    return result;
}

u16 EcologyApplyGrassSpeciesOverride(u16 species)
{
    BOOL owned;
    const struct EncounterOverlayApi *api;
    u16 result;
    api = EncounterOverlay_Open(&owned);
    if (api == NULL)
        return species;
    result = api->grassOverride(species);
    EncounterOverlay_Close(owned);
    return result;
}

u16 EcologyApplySpeciesOverrideForMethod(u16 species, u8 method)
{
    BOOL owned;
    const struct EncounterOverlayApi *api;
    u16 result;
    api = EncounterOverlay_Open(&owned);
    if (api == NULL)
        return species;
    result = api->methodOverride(species, method);
    EncounterOverlay_Close(owned);
    return result;
}

u16 EcologyRollSpeciesForEncounterBank(u8 bank, u8 method)
{
    BOOL owned;
    const struct EncounterOverlayApi *api;
    u16 result;
    api = EncounterOverlay_Open(&owned);
    if (api == NULL)
        return 0;
    result = api->rollSpecies(bank, method);
    EncounterOverlay_Close(owned);
    return result;
}

struct PartyPokemon * CreateEcologyWildMon(u32 method, u32 rod, u32 ivs)
{
    BOOL owned;
    const struct EncounterOverlayApi *api;
    struct PartyPokemon * result;
    api = EncounterOverlay_Open(&owned);
    if (api == NULL)
        return NULL;
    result = api->createWild(method, rod, ivs);
    EncounterOverlay_Close(owned);
    return result;
}

u32 SetEncountData_Ecology(struct PartyPokemon *lead, u32 rod, void *info, void *area, u32 method, u32 battler, void *setup)
{
    BOOL owned;
    const struct EncounterOverlayApi *api;
    u32 result;
    api = EncounterOverlay_Open(&owned);
    if (api == NULL)
        return FALSE;
    result = api->generateWild(lead, rod, info, area, method, battler, setup);
    EncounterOverlay_Close(owned);
    return result;
}

u32 BugContest_GenerateEcologyEncounter(FieldSystem *fsys, struct PartyPokemon *lead, u32 rod, void *gen, u32 method, u32 battler, void *setup)
{
    BOOL owned;
    const struct EncounterOverlayApi *api;
    u32 result;
    api = EncounterOverlay_Open(&owned);
    if (api == NULL)
        return FALSE;
    result = api->contestGenerate(fsys, lead, rod, gen, method, battler, setup);
    EncounterOverlay_Close(owned);
    return result;
}

void BugContest_InitEcologyEntries(BugContest *contest)
{
    BOOL owned;
    const struct EncounterOverlayApi *api;
    api = EncounterOverlay_Open(&owned);
    if (api == NULL)
        return;
    api->contestEntries(contest);
    EncounterOverlay_Close(owned);
}

u16 BugContest_JudgeEcologyMon(BugContest *contest, struct PartyPokemon *mon)
{
    BOOL owned;
    const struct EncounterOverlayApi *api;
    u16 result;
    api = EncounterOverlay_Open(&owned);
    if (api == NULL)
        return 0;
    result = api->contestJudge(contest, mon);
    EncounterOverlay_Close(owned);
    return result;
}

void BugContest_AssignPrize(BugContest *contest)
{
    BOOL owned;
    const struct EncounterOverlayApi *api;
    api = EncounterOverlay_Open(&owned);
    if (api == NULL)
        return;
    api->contestPrize(contest);
    EncounterOverlay_Close(owned);
}

