#include "encounter_overlay.h"

extern void CacheWildLevelCapFromFieldSystem(FieldSystem *fsys);
extern void ApplyWildDistanceLevelCapToMon(struct PartyPokemon *mon);
extern u8 GetWildLevelCapForEncounterBank(u8 bank);
extern u8 RollWildLevel(u8 cap, BOOL *baby);
extern void ApplyWildEncounterLevelAndStage(struct PartyPokemon *mon, u8 level, BOOL baby);
extern void WildMonApplyHeldItemForEncounter(struct PartyPokemon *mon);
extern void WildMonSetRandomHeldItem_hook(struct PartyPokemon *mon, u32 battleType, u32 compoundEyes);
extern u16 WildEncounterFinalize(struct PartyPokemon *mon, u16 species);
extern u16 WildEncounterFinalizeForEncount(struct PartyPokemon *mon, u16 species, u32 method, u32 rod);
extern u16 EcologyApplyGrassSpeciesOverride(u16 species);
extern u16 EcologyApplySpeciesOverrideForMethod(u16 species, u8 method);
extern u16 EcologyRollSpeciesForEncounterBank(u8 bank, u8 method);
extern struct PartyPokemon * CreateEcologyWildMon(u32 method, u32 rod, u32 ivs);
extern u32 SetEncountData_Ecology(struct PartyPokemon *lead, u32 rod, void *info, void *area, u32 method, u32 battler, void *setup);
extern u32 BugContest_GenerateEcologyEncounter(FieldSystem *fsys, struct PartyPokemon *lead, u32 rod, void *gen, u32 method, u32 battler, void *setup);
extern void BugContest_InitEcologyEntries(BugContest *contest);
extern u16 BugContest_JudgeEcologyMon(BugContest *contest, struct PartyPokemon *mon);
extern void BugContest_AssignPrize(BugContest *contest);
extern BOOL EcologyFindHint(u16 species, struct EcologyHint *hint);

const struct EncounterOverlayApi gEncounterOverlayApi __attribute__((section(".encounter_api"))) = {
    ENCOUNTER_OVERLAY_MAGIC,
    CacheWildLevelCapFromFieldSystem,
    ApplyWildDistanceLevelCapToMon,
    GetWildLevelCapForEncounterBank,
    RollWildLevel,
    ApplyWildEncounterLevelAndStage,
    WildMonApplyHeldItemForEncounter,
    WildMonSetRandomHeldItem_hook,
    WildEncounterFinalize,
    WildEncounterFinalizeForEncount,
    EcologyApplyGrassSpeciesOverride,
    EcologyApplySpeciesOverrideForMethod,
    EcologyRollSpeciesForEncounterBank,
    CreateEcologyWildMon,
    SetEncountData_Ecology,
    BugContest_GenerateEcologyEncounter,
    BugContest_InitEcologyEntries,
    BugContest_JudgeEcologyMon,
    BugContest_AssignPrize,
    EcologyFindHint,
};
