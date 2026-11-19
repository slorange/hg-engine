#include "config.h"
#include "constants/ability.h"
#include "constants/generated/ecology_compat.h"
#include "constants/species.h"
#include "encounter.h"
#include "pokemon.h"
#include "save.h"
#include "wild_encounter_finalize.h"
#include "wild_level_caps.h"

#ifdef IMPLEMENT_ECOLOGY_GENERATION
#include "ecology/ecology_encounter.h"
#endif

extern u32 space_for_setmondata;

void ApplyWildDistanceLevelCapWithLeadAbility(struct PartyPokemon *pp, u8 ability);
#ifdef IMPLEMENT_ECOLOGY_GENERATION
u16 EcologyApplySpeciesWithLeadAbility(u16 vanillaSpecies, u8 method, u8 ability);
#endif

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

static u16 WildEncounterApplySpecies(struct PartyPokemon *pp, u16 vanillaTableSpecies, u8 ecologyMethod, BOOL useExplicitMethod, u8 ability)
{
    u16 species;

#ifdef IMPLEMENT_ECOLOGY_GENERATION
    if (useExplicitMethod) {
        species = EcologyApplySpeciesWithLeadAbility(vanillaTableSpecies, ecologyMethod, ability);
    } else {
        species = EcologyApplyGrassSpeciesOverride(vanillaTableSpecies);
    }
#else
    (void)ecologyMethod;
    (void)ability;
    (void)useExplicitMethod;
    species = vanillaTableSpecies;
#endif

    SetMonData(pp, MON_DATA_SPECIES, &species);
    SetMonData(pp, MON_DATA_FORM, (u8 *)&space_for_setmondata);
    SetMonData(pp, MON_DATA_SPECIES_NAME, NULL);

    return species;
}

// Vanilla wild setup uses OTID 0; catch stamps player OT without changing PID — set player OT here so shinies match after catch.
static void WildEncounterApplyPlayerOtId(struct PartyPokemon *pp)
{
    void *saveData;
    struct PlayerProfile *profile;
    u32 otId;

    if (pp == NULL) {
        return;
    }

    saveData = SaveBlock2_get();
    if (saveData == NULL) {
        return;
    }

    profile = Sav2_PlayerData_GetProfileAddr(saveData);
    if (profile == NULL) {
        return;
    }

    otId = profile->id;
    SetMonData(pp, MON_DATA_OTID, &otId);
}

static void ApplyLeadPersonality(struct PartyPokemon *pp, struct PartyPokemon *lead, u8 ability, u32 ivs)
{
    u16 species = GetMonData(pp, MON_DATA_SPECIES, NULL);
    s32 nature = -1;
    s32 gender = -1;
    u32 personality;
    u32 form;
    u32 heldItem;

    if (ability == ABILITY_SYNCHRONIZE && gf_rand() % 2 == 0) {
        nature = GetMonNature(lead);
    }
    if (ability == ABILITY_CUTE_CHARM) {
        u32 ratio = PokePersonalParaGet(species, PERSONAL_GENDER_RATIO);
        u32 leadGender = GetMonData(lead, MON_DATA_GENDER, NULL);

        if (ratio > 0 && ratio < 254 && leadGender <= POKEMON_GENDER_FEMALE && gf_rand() % 3 != 0) {
            gender = leadGender == POKEMON_GENDER_FEMALE ? POKEMON_GENDER_MALE : POKEMON_GENDER_FEMALE;
        }
    }
    if (nature < 0 && gender < 0) {
        return;
    }

    // Build with the new PID so the encrypted data and calculated stats agree.
    do {
        personality = gf_rand() | (gf_rand() << 16);
    } while ((nature >= 0 && GetNatureFromPersonality(personality) != nature)
          || (gender >= 0 && PokeSexGetMonsNo(species, personality) != gender));

    form = GetMonData(pp, MON_DATA_FORM, NULL);
    heldItem = GetMonData(pp, MON_DATA_HELD_ITEM, NULL);
    PokeParaSet(pp, species, GetMonData(pp, MON_DATA_LEVEL, NULL), ivs, TRUE, personality, 0, 0);
    SetMonData(pp, MON_DATA_FORM, &form);
    SetMonData(pp, MON_DATA_HELD_ITEM, &heldItem);
    UpdatePassiveForms(pp);
    RecalcPartyPokemonStats(pp);
}

static u16 WildEncounterFinishMon(struct PartyPokemon *pp, u16 vanillaTableSpecies, u8 ecologyMethod,
                                  BOOL useExplicitMethod, struct PartyPokemon *lead, u8 ability, u32 ivs)
{
    if (pp == NULL) {
        return vanillaTableSpecies;
    }

    WildEncounterApplySpecies(pp, vanillaTableSpecies, ecologyMethod, useExplicitMethod, ability);
    UpdatePassiveForms(pp);
    ApplyWildDistanceLevelCapWithLeadAbility(pp, ability);
    if (lead != NULL) {
        ApplyLeadPersonality(pp, lead, ability, ivs);
    }
    WildEncounterApplyPlayerOtId(pp);
    ResetPartyPokemonAbility(pp);
    ClearMonMoves(pp);
    InitBoxMonMoveset(&pp->box);

    return (u16)(GetMonData(pp, MON_DATA_SPECIES, NULL) & 0x07FF);
}

u16 WildEncounterFinalize(struct PartyPokemon *pp, u16 vanillaTableSpecies)
{
    return WildEncounterFinishMon(pp, vanillaTableSpecies, ECOLOGY_METHOD_LAND, FALSE, NULL, 0, 0);
}

u16 WildEncounterFinalizeWithLead(struct PartyPokemon *pp, u16 vanillaTableSpecies, u32 encounterType,
                                  u32 rodType, struct PartyPokemon *lead, u8 ability, u32 ivs)
{
    u8 method = WildEncountTypeToEcologyMethod(encounterType, rodType);

    return WildEncounterFinishMon(pp, vanillaTableSpecies, method, TRUE, lead, ability, ivs);
}

u16 WildEncounterFinalizeForEncount(struct PartyPokemon *pp, u16 vanillaTableSpecies, u32 encounterType, u32 rodType)
{
    return WildEncounterFinalizeWithLead(pp, vanillaTableSpecies, encounterType, rodType, NULL, 0, 0);
}
