#ifndef ENCOUNTER_OVERLAY_H
#define ENCOUNTER_OVERLAY_H
#include "wild_level_caps.h"
#include "wild_encounter_finalize.h"
#include "wild_berry_hold.h"
#include "setencount_ecology.h"
#include "ecology/ecology_encounter.h"
#include "bug_contest_ecology.h"

#define ENCOUNTER_OVERLAY_ADDRESS 0x023C0400u
#define ENCOUNTER_OVERLAY_MAGIC 0x454E4301u

struct EcologyHint {
    u16 mapId;
    u8 method;
    u8 level;
};

struct EncounterOverlayApi {
    u32 magic;
    void (*cacheCap)(FieldSystem *fsys); // CacheWildLevelCapFromFieldSystem
    void (*applyDistanceCap)(struct PartyPokemon *mon); // ApplyWildDistanceLevelCapToMon
    u8 (*capForBank)(u8 bank); // GetWildLevelCapForEncounterBank
    u8 (*rollLevel)(u8 cap, BOOL *baby); // RollWildLevel
    void (*applyLevelAndStage)(struct PartyPokemon *mon, u8 level, BOOL baby); // ApplyWildEncounterLevelAndStage
    void (*applyHeldItem)(struct PartyPokemon *mon); // WildMonApplyHeldItemForEncounter
    void (*setHeldItem)(struct PartyPokemon *mon, u32 battleType, u32 compoundEyes); // WildMonSetRandomHeldItem_hook
    u16 (*finalize)(struct PartyPokemon *mon, u16 species); // WildEncounterFinalize
    u16 (*finalizeForEncount)(struct PartyPokemon *mon, u16 species, u32 method, u32 rod); // WildEncounterFinalizeForEncount
    u16 (*grassOverride)(u16 species); // EcologyApplyGrassSpeciesOverride
    u16 (*methodOverride)(u16 species, u8 method); // EcologyApplySpeciesOverrideForMethod
    u16 (*rollSpecies)(u8 bank, u8 method); // EcologyRollSpeciesForEncounterBank
    struct PartyPokemon * (*createWild)(u32 method, u32 rod, u32 ivs); // CreateEcologyWildMon
    u32 (*generateWild)(struct PartyPokemon *lead, u32 rod, void *info, void *area, u32 method, u32 battler, void *setup); // SetEncountData_Ecology
    u32 (*contestGenerate)(FieldSystem *fsys, struct PartyPokemon *lead, u32 rod, void *gen, u32 method, u32 battler, void *setup); // BugContest_GenerateEcologyEncounter
    void (*contestEntries)(BugContest *contest); // BugContest_InitEcologyEntries
    u16 (*contestJudge)(BugContest *contest, struct PartyPokemon *mon); // BugContest_JudgeEcologyMon
    void (*contestPrize)(BugContest *contest); // BugContest_AssignPrize
    BOOL (*findHint)(u16 species, struct EcologyHint *hint);
};

const struct EncounterOverlayApi *EncounterOverlay_Open(BOOL *owned);
void EncounterOverlay_Close(BOOL owned);
#endif
