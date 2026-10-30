#include "config.h"
#include "constants/generated/ecology_compat.h"
#include "constants/species.h"
#include "encounter.h"
#include "pokemon.h"
#include "wild_encounter_finalize.h"
#include "wild_level_caps.h"

#ifdef IMPLEMENT_ECOLOGY_GENERATION
#include "ecology/ecology_encounter.h"
#endif

extern u32 space_for_setmondata;

static u8 WildEncountTypeToEcologyMethod(u32 encounterType, u32 rodType)
{
    switch (encounterType) {
    case WILD_ENCOUNTERTYPE_LAND:
        return ECOLOGY_METHOD_LAND;
    case WILD_ENCOUNTERTYPE_SURF:
        return ECOLOGY_METHOD_SURF;
    case WILD_ENCOUNTERTYPE_FISH:
        if (rodType == 1) {
            return ECOLOGY_METHOD_GOOD_ROD;
        }
        if (rodType == 2) {
            return ECOLOGY_METHOD_SUPER_ROD;
        }
        return ECOLOGY_METHOD_OLD_ROD;
    case WILD_ENCOUNTERTYPE_ROCK_SMASH:
        return ECOLOGY_METHOD_ROCK_SMASH;
    case WILD_ENCOUNTERTYPE_HEADBUTT:
        return ECOLOGY_METHOD_HEADBUTT;
    default:
        return ECOLOGY_METHOD_LAND;
    }
}

static u16 WildEncounterApplySpecies(struct PartyPokemon *pp, u16 vanillaTableSpecies, u8 ecologyMethod, BOOL useExplicitMethod)
{
    u16 species;

#ifdef IMPLEMENT_ECOLOGY_GENERATION
    if (useExplicitMethod) {
        species = EcologyApplySpeciesOverrideForMethod(vanillaTableSpecies, ecologyMethod);
    } else {
        species = EcologyApplyGrassSpeciesOverride(vanillaTableSpecies);
    }
#else
    (void)ecologyMethod;
    (void)useExplicitMethod;
    species = vanillaTableSpecies;
#endif

    SetMonData(pp, MON_DATA_SPECIES, &species);
    SetMonData(pp, MON_DATA_FORM, (u8 *)&space_for_setmondata);
    SetMonData(pp, MON_DATA_SPECIES_NAME, NULL);

    return species;
}

static u16 WildEncounterFinishMon(struct PartyPokemon *pp, u16 vanillaTableSpecies, u8 ecologyMethod, BOOL useExplicitMethod)
{
    if (pp == NULL) {
        return vanillaTableSpecies;
    }

    WildEncounterApplySpecies(pp, vanillaTableSpecies, ecologyMethod, useExplicitMethod);
    UpdatePassiveForms(pp);
    ApplyWildDistanceLevelCapToMon(pp);
    ResetPartyPokemonAbility(pp);
    InitBoxMonMoveset(&pp->box);

    return (u16)(GetMonData(pp, MON_DATA_SPECIES, NULL) & 0x07FF);
}

u16 WildEncounterFinalize(struct PartyPokemon *pp, u16 vanillaTableSpecies)
{
    return WildEncounterFinishMon(pp, vanillaTableSpecies, ECOLOGY_METHOD_LAND, FALSE);
}

u16 WildEncounterFinalizeForEncount(
    struct PartyPokemon *pp,
    u16 vanillaTableSpecies,
    u32 encounterType,
    u32 rodType)
{
    u8 method = WildEncountTypeToEcologyMethod(encounterType, rodType);

    return WildEncounterFinishMon(pp, vanillaTableSpecies, method, TRUE);
}
