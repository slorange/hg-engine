// Host-side regression tests for the actual shared stage-selection headers.
#include <assert.h>
extern int puts(const char *);
extern int printf(const char *, ...);
extern int fflush(void *);
#include "encounter_species_stage.h"
#include "constants/trainerclass.h"

static u16 nextRandom;
u16 gf_rand(void) { return nextRandom; }
/* ACTUAL_WILD_LEVEL_ROLL */
/* ACTUAL_TRAINER_CONTEXT */

static u16 stage(u16 species, u8 level, u32 seed, u8 context, BOOL babies)
{
    return AdjustEncounterSpeciesForLevel(species, level, seed, context, babies);
}

static void check(u16 source, u8 level, u16 expected, u8 context, BOOL babies)
{
    for (u32 seed = 0; seed < 100; seed++) {
        u16 got = stage(source, level, seed, context, babies);
        if (got != expected) {
            printf("FAIL source=%u level=%u seed=%u context=%u babies=%u expected=%u got=%u\n",
                source, level, seed, context, babies, expected, got);
            fflush(NULL);
        }
        assert(got == expected);
    }
}

static void rate(u16 source, u16 evolved, u8 level, u8 context, double expected)
{
    u32 hits = 0;
    for (u32 seed = 0; seed < 20000; seed++) {
        if (stage(source, level, seed, context, FALSE) == evolved) hits++;
    }
    double fraction = hits / 20000.0;
    assert(fraction > expected - 0.025 && fraction < expected + 0.025);
}

int main(void)
{
    const u8 wild = ENCOUNTER_STAGE_WILD, trainer = ENCOUNTER_STAGE_TRAINER, leader = ENCOUNTER_STAGE_LEADER;
    // Level-up and move-known boundaries, including authored finals devolving.
    const u16 moves[][3] = {
        {SPECIES_LICKITUNG, SPECIES_LICKILICKY, 30},
        {SPECIES_TANGELA, SPECIES_TANGROWTH, 32},
        {SPECIES_AIPOM, SPECIES_AMBIPOM, 28},
        {SPECIES_YANMA, SPECIES_YANMEGA, 33},
        {SPECIES_STANTLER, SPECIES_WYRDEER, 31},
        {SPECIES_GIRAFARIG, SPECIES_FARIGIRAF, 32},
        {SPECIES_DUNSPARCE, SPECIES_DUDUNSPARCE, 32},
        {SPECIES_PRIMEAPE, SPECIES_ANNIHILAPE, 35},
    };
    for (u8 c = wild; c <= leader; c++) {
        check(SPECIES_MAMOSWINE, 21, SPECIES_SWINUB, c, FALSE);
        check(SPECIES_MAMOSWINE, 22, SPECIES_PILOSWINE, c, FALSE);
        check(SPECIES_SWINUB, 35, SPECIES_PILOSWINE, c, FALSE);
        check(SPECIES_SWINUB, 36, SPECIES_MAMOSWINE, c, FALSE);
        for (u16 i = 0; i < NELEMS(moves); i++) {
            check(moves[i][1], moves[i][2] - 1, moves[i][0], c, FALSE);
            check(moves[i][0], moves[i][2], moves[i][1], c, FALSE);
        }
    }
    // Wild item endpoints and probability, with five-level source-stage delay.
    check(SPECIES_ARCANINE, 15, SPECIES_GROWLITHE, wild, FALSE);
    check(SPECIES_GROWLITHE, 60, SPECIES_ARCANINE, wild, FALSE);
    rate(SPECIES_GROWLITHE, SPECIES_ARCANINE, 30, wild, 1.0 / 3.0);
    check(SPECIES_POLITOED, 30, SPECIES_POLIWHIRL, wild, FALSE);
    check(SPECIES_URSALUNA, 35, SPECIES_URSARING, wild, FALSE);
    check(SPECIES_URSARING, 60, SPECIES_URSALUNA, wild, FALSE);
    check(SPECIES_SEADRA, 36, SPECIES_SEADRA, wild, FALSE); // Horsea evolves at 32; start is 37.
    check(SPECIES_SEADRA, 60, SPECIES_KINGDRA, wild, FALSE);
    // Trainer curves use absolute level, even for a stage reached above 15.
    check(SPECIES_GROWLITHE, 15, SPECIES_GROWLITHE, trainer, FALSE);
    rate(SPECIES_GROWLITHE, SPECIES_ARCANINE, 30, trainer, 0.6);
    rate(SPECIES_POLIWAG, SPECIES_POLITOED, 30, trainer, 0.3);
    check(SPECIES_GROWLITHE, 40, SPECIES_ARCANINE, trainer, FALSE);
    check(SPECIES_GROWLITHE, 25, SPECIES_ARCANINE, leader, FALSE);
    // Friendship and trainer-only items are excluded even for authored wild finals.
    check(SPECIES_CROBAT, 100, SPECIES_GOLBAT, wild, FALSE);
    check(SPECIES_BLISSEY, 100, SPECIES_CHANSEY, wild, FALSE);
    check(SPECIES_ALAKAZAM, 100, SPECIES_KADABRA, wild, FALSE);
    check(SPECIES_RHYPERIOR, 100, SPECIES_RHYDON, wild, FALSE);
    check(SPECIES_ELECTIVIRE, 100, SPECIES_ELECTABUZZ, wild, FALSE);
    check(SPECIES_MAGMORTAR, 100, SPECIES_MAGMAR, wild, FALSE);
    check(SPECIES_PORYGON_Z, 100, SPECIES_PORYGON, wild, FALSE);
    check(SPECIES_ONIX, 60, SPECIES_STEELIX, wild, FALSE);
    check(SPECIES_DUSCLOPS, 60, SPECIES_DUSKNOIR, wild, FALSE);
    check(SPECIES_GOLBAT, 15, SPECIES_ZUBAT, trainer, FALSE);
    rate(SPECIES_CHANSEY, SPECIES_BLISSEY, 20, trainer, 0.5);
    check(SPECIES_GOLBAT, 25, SPECIES_CROBAT, trainer, FALSE);
    check(SPECIES_CHANSEY, 20, SPECIES_BLISSEY, leader, FALSE);
    rate(SPECIES_PORYGON, SPECIES_PORYGON_Z, 30, trainer, 0.36);
    // Each excluded baby has an allowed floor, while baby rolls retain the root.
    for (u16 i = 0; i < sSyntheticEvoEdgesData.babyCount; i++) {
        u16 baby = sSyntheticEvoEdgesData.babies[i];
        u16 normal = stage(baby, 5, 0, wild, FALSE);
        assert(!IsEncounterBaby(normal));
        assert(stage(baby, 5, 0, wild, TRUE) == baby);
        assert(stage(normal, 5, 0, wild, TRUE) == baby);
        assert(!IsEncounterBaby(stage(baby, 5, 0, trainer, FALSE)));
    }
    check(SPECIES_BONSLY, 16, SPECIES_SUDOWOODO, wild, TRUE);
    check(SPECIES_MIME_JR, 24, SPECIES_MR_MIME, wild, TRUE);
    // Branches remain stable for a seed, diverse across seeds, and context-filtered.
    BOOL sylveonSeen = FALSE, kleavorSeen = FALSE, politoedSeen = FALSE;
    for (u32 seed = 0; seed < 10000; seed++) {
        u16 eevee = stage(SPECIES_EEVEE, 60, seed, wild, FALSE);
        assert(eevee != SPECIES_ESPEON && eevee != SPECIES_UMBREON && eevee != SPECIES_SYLVEON);
        assert(eevee == stage(SPECIES_SYLVEON, 60, seed, wild, FALSE));
        sylveonSeen |= stage(SPECIES_EEVEE, 40, seed, trainer, FALSE) == SPECIES_SYLVEON;
        kleavorSeen |= stage(SPECIES_SCYTHER, 60, seed, wild, FALSE) == SPECIES_KLEAVOR;
        politoedSeen |= stage(SPECIES_POLIWAG, 60, seed, wild, FALSE) == SPECIES_POLITOED;
        u16 kirlia = stage(SPECIES_KIRLIA, 30, seed, wild, FALSE);
        assert(kirlia == SPECIES_GALLADE || kirlia == SPECIES_GARDEVOIR);
        u16 snorunt = stage(SPECIES_SNORUNT, 42, seed, wild, FALSE);
        assert(snorunt == SPECIES_FROSLASS || snorunt == SPECIES_GLALIE);
        u16 nincada = stage(SPECIES_NINCADA, 20, seed, wild, FALSE);
        assert(nincada == SPECIES_NINJASK || nincada == SPECIES_SHEDINJA);
    }
    assert(sylveonSeen && kleavorSeen && politoedSeen);
    // Explicit baby flag: level alone never grants the exception.
    BOOL babyRoll;
    nextRandom = 0;
    assert(RollWildLevel(60, &babyRoll) == 2 && babyRoll);
    RollWildLevel(9, &babyRoll);
    assert(!babyRoll);
    nextRandom = 99;
    RollWildLevel(60, &babyRoll);
    assert(!babyRoll);
    assert(TrainerEncounterStageContext(TRAINERCLASS_LEADER_FALKNER) == leader);
    assert(TrainerEncounterStageContext(TRAINERCLASS_LEADER_BLUE) == leader);
    assert(TrainerEncounterStageContext(TRAINERCLASS_ELITE_FOUR_WILL) == leader);
    assert(TrainerEncounterStageContext(TRAINERCLASS_CHAMPION) == leader);
    assert(TrainerEncounterStageContext(TRAINERCLASS_YOUNGSTER) == trainer);
    puts("PASS: actual C stage boundaries, baby exception, context classification, branches, and statistical evolution rates.");
    return 0;
}

