#include "config.h"
#include "constants/ability.h"
#include "constants/generated/ecology_compat.h"
#include "constants/encounter_tables.h"
#include "constants/species.h"
#include "encounter.h"
#include "encounter_location.h"
#include "pokemon.h"
#include "roamer.h"
#include "save.h"
#include "wild_encounter_finalize.h"
#include "wild_level_caps.h"

#ifdef IMPLEMENT_ECOLOGY_GENERATION
#include "ecology/ecology_script.h"
#include "ecology/ecology_encounter.h"
#endif

extern u32 space_for_setmondata;

void ApplyWildDistanceLevelCapWithLeadAbility(struct PartyPokemon *pp, u8 ability);
void ApplyWildEncounterLevelAndStage(struct PartyPokemon *pp, u8 level, BOOL babyRoll);
u8 LONG_CALL MapHeader_GetWildEncounterBank(u32 mapId);
BOOL LONG_CALL UnownRoamer_TryEncounter(u16 map, u8 *form);
void LONG_CALL UnownRoamer_PrepareMon(struct PartyPokemon *mon, u8 form);
void LONG_CALL UnownRoamer_RestoreCondition(struct PartyPokemon *mon, u8 form);
#ifdef IMPLEMENT_ECOLOGY_GENERATION
u16 EcologyApplySpeciesWithLeadAbility(u16 vanillaSpecies, u8 method, u8 ability);
#endif

struct UnownEncounterPool {
    u8 firstBank;
    u8 lastBank;
    u8 guaranteed;
    u8 formCount;
    char letters[11];
};

#define UNOWN_POOL_ENTRY(first, last, always, letters) \
    { ENCDATA_##first, ENCDATA_##last, always, sizeof(letters) - 1, letters }
#define UNOWN_POOL(bank, letters) UNOWN_POOL_ENTRY(bank, bank, FALSE, letters)
#define UNOWN_RANGE(first, last, letters) UNOWN_POOL_ENTRY(first, last, FALSE, letters)
#define ALPH_LETTERS "AHILNOPRSUW"

static const struct UnownEncounterPool sUnownPools[] = {
    UNOWN_POOL_ENTRY(D24R0205_RUINS_OF_ALPH_INSIDE_MAIN_ROOM,
        D24R0217_RUINS_OF_ALPH_INSIDE_LADDER_ROOM, TRUE, ALPH_LETTERS),
    UNOWN_POOL(D24R0101_RUINS_OF_ALPH_OUTSIDE, ALPH_LETTERS),
    UNOWN_RANGE(D42R0102_DARK_CAVE_ROUTE_31_ENTRANCE, D42R0101_DARK_CAVE_ROUTE_45_ENTRANCE, "DARK"),
    UNOWN_RANGE(D25R0101_UNION_CAVE_1F, D25R0103_UNION_CAVE_B2F, "UNIO"),
    UNOWN_RANGE(D26R0102_SLOWPOKE_WELL_1F, D26R0103_SLOWPOKE_WELL_B2F, "SLOW"),
    UNOWN_POOL(D36R0101_ILEX_FOREST, "ILEX"),
    UNOWN_RANGE(D15R0102_SPROUT_TOWER_2F, D15R0103_SPROUT_TOWER_3F, "GROW"),
    UNOWN_RANGE(D18R0101_BURNED_TOWER_1F, D18R0102_BURNED_TOWER_B1F, "FIRE"),
    UNOWN_RANGE(D17R0102_BELL_TOWER_2F, D17R0109_BELL_TOWER_9F, "BEL"),
    UNOWN_POOL(D17R0112_BELL_TOWER_10F, "BEL"),
    UNOWN_RANGE(D38R0101_MT_MORTAR_WATERFALL_ROOM, D38R0104_MT_MORTAR_B1F, "MORTA"),
    UNOWN_POOL(T29_LAKE_OF_RAGE, "RAGE"),
    UNOWN_RANGE(D39R0101_ICE_PATH_1F, D39R0104_ICE_PATH_B3F, "ICE"),
    UNOWN_POOL(D44R0102_DRAGONS_DEN, "DRAGON"),
    UNOWN_RANGE(D40R0101_WHIRL_ISLANDS_1F, D40R0102_WHIRL_ISLANDS_B1F, "WHIRL"),
    UNOWN_POOL(D40R0104_WHIRL_ISLANDS_B2F, "WHIRL"),
    UNOWN_POOL(D40R0106_WHIRL_ISLANDS_B3F_LEDGE_OVERLOOKING_LUGIA_ROOM, "WHIRL"),
    UNOWN_RANGE(D02R0101_MT_MOON_1F, D02R0102_MT_MOON_2F, "MON"),
    UNOWN_RANGE(D02R0103_MT_MOON_OUTSIDE_AREA, D02R0104_MT_MOON_OUTSIDE_CLEFAIRY_ACTIVE, "MON"),
    UNOWN_RANGE(D05R0101_ROCK_TUNNEL_1F, D05R0102_ROCK_TUNNEL_B1F, "ROCK"),
    UNOWN_POOL(D01R0101_DIGLETTS_CAVE, "DIG"),
    UNOWN_RANGE(D11R0101_SEAFOAM_ISLANDS_1F, D11R0105_SEAFOAM_ISLANDS_B4F, "FROST"),
    UNOWN_POOL(D43R0101_VICTORY_ROAD_1F, "VICTORY"),
    UNOWN_RANGE(D43R0102_VICTORY_ROAD_2F, D43R0103_VICTORY_ROAD_3F, "VICTORY"),
    UNOWN_POOL(D45R0101_TOHJO_FALLS, "TOHJ"),
    UNOWN_POOL(T09_CINNABAR_ISLAND, "MAG"),
    UNOWN_RANGE(D03R0101_CERULEAN_CAVE_1F, D03R0103_CERULEAN_CAVE_B2F, "Z"),
    UNOWN_RANGE(D41R0105_MT_SILVER_MOLTRES_ROOM, D41R0107_MT_SILVER_4F, "Q"),
    UNOWN_RANGE(T31_MT_SILVER_OUTSIDE_POKEMON_CENTER, D41R0102_MT_SILVER_TOP_SNOWY_AREA, "Q"),
};

static u16 RollUniform(u16 limit)
{
    u16 roll;
    do {
        roll = gf_rand();
    } while (roll >= (0x10000 / limit) * limit);
    return roll % limit;
}

static BOOL TryPickUnownForm(u8 method, BOOL useExplicitMethod, struct PartyPokemon *lead,
                             BOOL allowRoamer, u8 *form)
{
    u16 mapId;
    if ((method >= ECOLOGY_METHOD_OLD_ROD && method <= ECOLOGY_METHOD_SUPER_ROD)
        || !EncounterResolveMapId(&mapId)) {
        return FALSE;
    }
    if (allowRoamer && method == ECOLOGY_METHOD_LAND && UnownRoamer_TryEncounter(mapId, form)) {
        return TRUE;
    }
    u8 bank = MapHeader_GetWildEncounterBank(mapId);
    for (u32 i = 0; i < sizeof(sUnownPools) / sizeof(sUnownPools[0]); i++) {
        const struct UnownEncounterPool *pool = &sUnownPools[i];
        if (bank < pool->firstBank || bank > pool->lastBank) {
            continue;
        }
        if (pool->guaranteed) {
            if (method != ECOLOGY_METHOD_LAND) {
                return FALSE;
            }
        } else {
            // The legacy finalizer does not know the actual encounter method.
            if (!useExplicitMethod) {
                return FALSE;
            }
            BOOL unownLead = lead != NULL && !GetMonData(lead, MON_DATA_IS_EGG, NULL)
                && GetMonData(lead, MON_DATA_SPECIES, NULL) == SPECIES_UNOWN;
            if (RollUniform(100) >= (unownLead ? 50 : 5)) {
                return FALSE;
            }
        }
        *form = pool->letters[RollUniform(pool->formCount)] - 'A';
        return TRUE;
    }
    return FALSE;
}

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
                                  BOOL useExplicitMethod, struct PartyPokemon *lead, u8 ability, u32 ivs,
                                  BOOL allowRoamer)
{
    if (pp == NULL) {
        return vanillaTableSpecies;
    }

    u8 form;
    BOOL roaming = FALSE;
#ifdef IMPLEMENT_ECOLOGY_GENERATION
    EcologyRefreshForEncounter();
#endif
    if (TryPickUnownForm(ecologyMethod, useExplicitMethod, lead, allowRoamer, &form)) {
        u16 species = SPECIES_UNOWN;
        roaming = form >= UNOWN_ROAMER_FIRST_FORM;
        SetMonData(pp, MON_DATA_SPECIES, &species);
        SetMonData(pp, MON_DATA_FORM, &form);
        SetMonData(pp, MON_DATA_SPECIES_NAME, NULL);
    } else {
        WildEncounterApplySpecies(pp, vanillaTableSpecies, ecologyMethod, useExplicitMethod, ability);
    }
    UpdatePassiveForms(pp);
    if (roaming) {
        UnownRoamer_PrepareMon(pp, form);
        ApplyWildEncounterLevelAndStage(pp, UNOWN_ROAMER_LEVEL, FALSE);
        UnownRoamer_RestoreCondition(pp, form);
    } else {
        ApplyWildDistanceLevelCapWithLeadAbility(pp, ability);
        if (lead != NULL) {
            ApplyLeadPersonality(pp, lead, ability, ivs);
        }
    }
    WildEncounterApplyPlayerOtId(pp);
    ResetPartyPokemonAbility(pp);
    ClearMonMoves(pp);
    InitBoxMonMoveset(&pp->box);

    return (u16)(GetMonData(pp, MON_DATA_SPECIES, NULL) & 0x07FF);
}

u16 WildEncounterFinalize(struct PartyPokemon *pp, u16 vanillaTableSpecies)
{
    return WildEncounterFinishMon(pp, vanillaTableSpecies, ECOLOGY_METHOD_LAND, FALSE, NULL, 0, 0, FALSE);
}

u16 WildEncounterFinalizeWithLead(struct PartyPokemon *pp, u16 vanillaTableSpecies, u32 encounterType,
                                  u32 rodType, struct PartyPokemon *lead, u8 ability, u32 ivs, BOOL allowRoamer)
{
    u8 method = WildEncountTypeToEcologyMethod(encounterType, rodType);

    return WildEncounterFinishMon(pp, vanillaTableSpecies, method, TRUE, lead, ability, ivs, allowRoamer);
}

u16 WildEncounterFinalizeForEncount(struct PartyPokemon *pp, u16 vanillaTableSpecies, u32 encounterType, u32 rodType)
{
    return WildEncounterFinalizeWithLead(pp, vanillaTableSpecies, encounterType, rodType, NULL, 0, 0, FALSE);
}
