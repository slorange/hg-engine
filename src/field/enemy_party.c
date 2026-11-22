#include "config.h"
#include "debug.h"
#include "types.h"

#include "constants/ability.h"
#include "constants/battle_constants.h"
#include "constants/file.h"
#include "constants/game.h"
#include "constants/hold_item_effects.h"
#include "constants/item.h"
#include "constants/moves.h"
#include "constants/species.h"
#include "constants/trainerclass.h"
#include "constants/weather_numbers.h"

#include "bag.h"
#include "battle.h"
#include "pokemon.h"

#ifdef IMPLEMENT_WILD_BERRY_HOLD
#endif
#include "rtc.h"
#include "save.h"
#include "script.h"
#include "encounter_species_gender.h"
#include "player_level_cap.h"
#include "trainer_data.h"

#ifdef DEBUG_BATTLE_SCENARIOS
#include "test_battle.h"
#endif // DEBUG_BATTLE_SCENARIOS

struct BattleSetup LONG_CALL *BattleSetup_New_Tutorial(u32 heapID, FieldSystem *fieldSystem);
int LONG_CALL BattleSetup_GetWildTransitionEffect(struct BattleSetup *setup);
int LONG_CALL BattleSetup_GetWildBattleMusic(struct BattleSetup *setup);
void LONG_CALL *Encounter_New(struct BattleSetup *setup, s32 effect, s32 bgm, u32 *winFlag);

/**
 *  @brief swap two integer values with each other given pointers
 *
 *  @param a first to swap
 *  @param b second to swap
 */
void swap(int *a, int *b)
{
    int temp = *a;
    *a = *b;
    *b = temp;
}

/**
 *  @brief randomize the order of an array size n
 *
 *  @param arr array to randomize
 *  @param n size of array
 */
void randomize(int arr[], int n)
{
    int i;
    for (i = n - 1; i > 0; i--) {
        int j = gf_rand() % (i + 1);
        swap(&arr[i], &arr[j]);
    }
}

extern u32 gLastPokemonLevelForMoneyCalc;

void BuildGeneratedTrainerMovesets(struct PartyPokemon **party, const int *order, int count, u8 badgeCount);
void SetGeneratedTrainerHeldItem(struct PartyPokemon *mon, u8 badgeCount);

#ifdef TRAINER_LEVEL_SCALING

/**
 *  @brief pick a uniform random level in [floor, ceiling] inclusive
 */
static u16 PickTrainerLevelInBand(u8 floor, u8 ceiling)
{
    u8 range;

    if (ceiling <= floor) {
        return ceiling;
    }

    range = ceiling - floor + 1;
    return (u16)(floor + (gf_rand() % range));
}

/**
 *  @brief true for Johto/Kanto Gym Leader trainer classes
 */
static BOOL IsGymLeaderTrainerClass(u8 trainerClass)
{
    switch (trainerClass) {
    case TRAINERCLASS_LEADER_FALKNER:
    case TRAINERCLASS_LEADER_BUGSY:
    case TRAINERCLASS_LEADER_WHITNEY:
    case TRAINERCLASS_LEADER_MORTY:
    case TRAINERCLASS_LEADER_PRYCE:
    case TRAINERCLASS_LEADER_JASMINE:
    case TRAINERCLASS_LEADER_CHUCK:
    case TRAINERCLASS_LEADER_CLAIR:
    case TRAINERCLASS_LEADER_BROCK:
    case TRAINERCLASS_LEADER_MISTY:
    case TRAINERCLASS_LEADER_LT_SURGE:
    case TRAINERCLASS_LEADER_ERIKA:
    case TRAINERCLASS_LEADER_JANINE:
    case TRAINERCLASS_LEADER_SABRINA:
    case TRAINERCLASS_LEADER_BLAINE:
    case TRAINERCLASS_LEADER_BLUE:
        return TRUE;
    default:
        return FALSE;
    }
}



// Class identity is shared by original fights and rematches.
static u8 TrainerEncounterStageContext(u8 trainerClass)
{
    if (IsGymLeaderTrainerClass(trainerClass)) {
        return ENCOUNTER_STAGE_LEADER;
    }
    switch (trainerClass) {
    case TRAINERCLASS_ELITE_FOUR_WILL:
    case TRAINERCLASS_ELITE_FOUR_KAREN:
    case TRAINERCLASS_ELITE_FOUR_KOGA:
    case TRAINERCLASS_ELITE_FOUR_BRUNO:
    case TRAINERCLASS_CHAMPION:
        return ENCOUNTER_STAGE_LEADER;
    default:
        return ENCOUNTER_STAGE_TRAINER;
    }
}

#if defined(TRAINER_SPECIES_STAGE_ADJUST)

#include "encounter_species_stage.h"

#ifdef TRAINER_RANDOM_SPECIES
static void SetGeneratedTrainerEVs(struct PartyPokemon *mon, u8 badgeCount, BOOL gymLeader)
{
    const int statCount = MON_DATA_SPDEF_EV - MON_DATA_HP_EV + 1;
    int total = (gymLeader ? 102 : 51) * badgeCount;
    if (total > 510) {
        total = 510;
    }

    for (int stat = 0; stat < statCount; stat++) {
        u8 ev = total / statCount + (stat < total % statCount);
        SetMonData(mon, MON_DATA_HP_EV + stat, &ev);
    }
}

static void UpgradeGeneratedTrainerIVs(struct PartyPokemon **party, int count, u8 badgeCount, BOOL gymLeader)
{
    enum { statCount = MON_DATA_SPDEF_IV - MON_DATA_HP_IV + 1 };
    int upgrades = gymLeader ? 2 + badgeCount : (int)badgeCount - 7;
    if (upgrades <= 0) {
        return;
    }
    if (upgrades > 18) {
        upgrades = 18;
    }

    struct {
        u8 slot;
        u8 iv;
    } eligible[6 * statCount];
    int remaining = 0;
    for (int i = 0; i < count; i++) {
        for (int stat = 0; stat < statCount; stat++) {
            u8 iv = GetMonData(party[i], MON_DATA_HP_IV + stat, NULL);
            if (iv < 31) {
                eligible[remaining].slot = i * statCount + stat;
                eligible[remaining++].iv = iv;
            }
        }
    }

    // Pick the lowest remaining IV, breaking ties randomly.
    for (int i = 0; i < upgrades && remaining > 0; i++) {
        int pick = 0;
        int ties = 1;
        for (int j = 1; j < remaining; j++) {
            if (eligible[j].iv < eligible[pick].iv) {
                pick = j;
                ties = 1;
            } else if (eligible[j].iv == eligible[pick].iv && gf_rand() % ++ties == 0) {
                pick = j;
            }
        }
        int slot = eligible[pick].slot;
        u8 perfectIV = 31;
        SetMonData(party[slot / statCount], MON_DATA_HP_IV + slot % statCount, &perfectIV);
        eligible[pick] = eligible[--remaining];
    }
}

static const u16 sExtraTrainerSpecies[] = {
    SPECIES_LARVESTA, SPECIES_VOLCARONA, SPECIES_SYLVEON, SPECIES_KLEAVOR,
    SPECIES_WYRDEER, SPECIES_URSALUNA, SPECIES_ANNIHILAPE, SPECIES_FARIGIRAF,
    SPECIES_DUDUNSPARCE,
};

static BOOL IsRandomTrainerSpeciesEligible(u16 species)
{
    if ((species >= SPECIES_ARTICUNO && species <= SPECIES_MOLTRES)
        || (species >= SPECIES_MEWTWO && species <= SPECIES_MEW)
        || (species >= SPECIES_RAIKOU && species <= SPECIES_SUICUNE)
        || (species >= SPECIES_LUGIA && species <= SPECIES_CELEBI)
        || (species >= SPECIES_REGIROCK && species <= SPECIES_DEOXYS)
        || (species >= SPECIES_UXIE && species <= SPECIES_ARCEUS)
        || species == SPECIES_UNOWN || species == SPECIES_SMEARGLE) {
        return FALSE;
    }

    if (species >= SPECIES_BULBASAUR && species <= SPECIES_ARCEUS) {
        return TRUE;
    }
    for (int i = 0; i < NELEMS(sExtraTrainerSpecies); i++) {
        if (species == sExtraTrainerSpecies[i]) {
            return TRUE;
        }
    }
    return FALSE;
}

// Gym subordinate IDs are taken from the Gym events and trainer battle scripts.
static u8 GetTrainerGymClass(int trainerId, u8 trainerClass)
{
    switch (trainerId) {
    case 29:
    case 50:
        return TRAINERCLASS_LEADER_FALKNER;
    case 10:
    case 67:
    case 68:
    case 69:
        return TRAINERCLASS_LEADER_BUGSY;
    case 5:
    case 22:
    case 70:
    case 71:
        return TRAINERCLASS_LEADER_WHITNEY;
    case 46:
    case 89:
    case 493:
    case 494:
        return TRAINERCLASS_LEADER_MORTY;
    case 480:
    case 481:
    case 482:
    case 483:
    case 484:
        return TRAINERCLASS_LEADER_PRYCE;
    case 156:
    case 157:
    case 159:
    case 251:
        return TRAINERCLASS_LEADER_CHUCK;
    case 110:
    case 111:
    case 112:
    case 117:
    case 119:
        return TRAINERCLASS_LEADER_CLAIR;
    case 308:
    case 685:
        return TRAINERCLASS_LEADER_BROCK;
    case 297:
    case 298:
    case 676:
    case 677:
    case 678:
        return TRAINERCLASS_LEADER_MISTY;
    case 232:
    case 337:
    case 396:
        return TRAINERCLASS_LEADER_LT_SURGE;
    case 326:
    case 336:
    case 346:
    case 356:
        return TRAINERCLASS_LEADER_ERIKA;
    case 83:
    case 84:
    case 136:
    case 183:
        return TRAINERCLASS_LEADER_JANINE;
    case 230:
    case 368:
    case 369:
    case 415:
        return TRAINERCLASS_LEADER_SABRINA;
    case 681:
    case 682:
    case 683:
    case 684:
        return TRAINERCLASS_LEADER_BLUE;
    default:
        return trainerClass;
    }
}

static u32 GetTrainerTypeMask(u8 trainerClass)
{
    switch (trainerClass) {
    case TRAINERCLASS_LEADER_FALKNER:
        return (1u << TYPE_FLYING);
    case TRAINERCLASS_LEADER_BUGSY:
        return (1u << TYPE_BUG);
    case TRAINERCLASS_LEADER_WHITNEY:
        return (1u << TYPE_NORMAL) | (1u << TYPE_FAIRY);
    case TRAINERCLASS_LEADER_MORTY:
        return (1u << TYPE_GHOST) | (1u << TYPE_DARK);
    case TRAINERCLASS_LEADER_PRYCE:
        return (1u << TYPE_ICE);
    case TRAINERCLASS_LEADER_JASMINE:
        return (1u << TYPE_STEEL);
    case TRAINERCLASS_LEADER_CHUCK:
        return (1u << TYPE_FIGHTING);
    case TRAINERCLASS_LEADER_CLAIR:
        return (1u << TYPE_DRAGON) | (1u << TYPE_WATER);
    case TRAINERCLASS_LEADER_BROCK:
        return (1u << TYPE_ROCK) | (1u << TYPE_GROUND);
    case TRAINERCLASS_LEADER_MISTY:
        return (1u << TYPE_WATER);
    case TRAINERCLASS_LEADER_LT_SURGE:
        return (1u << TYPE_ELECTRIC);
    case TRAINERCLASS_LEADER_ERIKA:
        return (1u << TYPE_GRASS);
    case TRAINERCLASS_LEADER_JANINE:
        return (1u << TYPE_POISON);
    case TRAINERCLASS_LEADER_SABRINA:
        return (1u << TYPE_PSYCHIC);
    case TRAINERCLASS_LEADER_BLAINE:
        return (1u << TYPE_FIRE);
    case TRAINERCLASS_BUG_CATCHER:
        return (1u << TYPE_BUG);
    case TRAINERCLASS_GUITARIST:
        return (1u << TYPE_ELECTRIC);
    case TRAINERCLASS_BLACK_BELT:
        return (1u << TYPE_FIGHTING);
    case TRAINERCLASS_FIREBREATHER:
        return (1u << TYPE_FIRE);
    case TRAINERCLASS_BIRD_KEEPER_GS:
    case TRAINERCLASS_BIRD_KEEPER:
        return (1u << TYPE_FLYING);
    case TRAINERCLASS_MEDIUM:
        return (1u << TYPE_GHOST);
    case TRAINERCLASS_BOARDER:
    case TRAINERCLASS_SKIER:
        return (1u << TYPE_ICE);
    case TRAINERCLASS_BURGLAR:
    case TRAINERCLASS_TEAM_ROCKET:
    case TRAINERCLASS_TEAM_ROCKET_F:
    case TRAINERCLASS_ROCKET_BOSS:
    case TRAINERCLASS_EXECUTIVE_ARIANA:
    case TRAINERCLASS_EXECUTIVE_ARCHER:
    case TRAINERCLASS_EXECUTIVE_PETREL:
    case TRAINERCLASS_EXECUTIVE_PROTON:
        return (1u << TYPE_FIRE) | (1u << TYPE_POISON) | (1u << TYPE_DARK);
    case TRAINERCLASS_BIKER:
        return (1u << TYPE_POISON) | (1u << TYPE_STEEL);
    case TRAINERCLASS_JUGGLER:
    case TRAINERCLASS_PSYCHIC_M:
    case TRAINERCLASS_PSYCHIC_F:
        return (1u << TYPE_PSYCHIC);
    case TRAINERCLASS_SAGE:
        return (1u << TYPE_PSYCHIC) | (1u << TYPE_GHOST);
    case TRAINERCLASS_HIKER:
        return (1u << TYPE_ROCK) | (1u << TYPE_GROUND);
    case TRAINERCLASS_FISHERMAN:
    case TRAINERCLASS_SWIMMER_M:
    case TRAINERCLASS_SWIMMER_F:
        return (1u << TYPE_WATER);
    case TRAINERCLASS_SAILOR:
        return (1u << TYPE_WATER) | (1u << TYPE_FIGHTING);
    case TRAINERCLASS_ELITE_FOUR_WILL:
        return (1u << TYPE_PSYCHIC);
    case TRAINERCLASS_ELITE_FOUR_KOGA:
        return (1u << TYPE_POISON);
    case TRAINERCLASS_ELITE_FOUR_BRUNO:
        return (1u << TYPE_FIGHTING);
    case TRAINERCLASS_ELITE_FOUR_KAREN:
        return (1u << TYPE_DARK);
    case TRAINERCLASS_CHAMPION:
        return (1u << TYPE_DRAGON) | (1u << TYPE_FLYING);
    case TRAINERCLASS_BEAUTY:
        return (1u << TYPE_FAIRY) | (1u << TYPE_GRASS);
    case TRAINERCLASS_LASS:
        return (1u << TYPE_NORMAL) | (1u << TYPE_FAIRY);
    case TRAINERCLASS_SCIENTIST_GS:
    case TRAINERCLASS_SCIENTIST:
    case TRAINERCLASS_SUPER_NERD:
        return (1u << TYPE_ELECTRIC) | (1u << TYPE_STEEL);
    default:
        return 0;
    }
}

static BOOL IsTrainerFamilyException(u16 species, u8 trainerClass)
{
    switch (species) {
    case SPECIES_VOLTORB:
    case SPECIES_ELECTRODE:
        return trainerClass == TRAINERCLASS_JUGGLER;
    case SPECIES_VULPIX:
    case SPECIES_NINETALES:
        return trainerClass == TRAINERCLASS_LEADER_BROCK;
    case SPECIES_MAREEP:
    case SPECIES_FLAAFFY:
    case SPECIES_AMPHAROS:
        return trainerClass == TRAINERCLASS_LEADER_JASMINE;
    case SPECIES_TOGEPI:
    case SPECIES_TOGETIC:
    case SPECIES_TOGEKISS:
        return trainerClass == TRAINERCLASS_LEADER_MISTY;
    case SPECIES_RHYHORN:
    case SPECIES_RHYDON:
    case SPECIES_RHYPERIOR:
        return trainerClass == TRAINERCLASS_LEADER_BLAINE;
    case SPECIES_SEEL:
    case SPECIES_DEWGONG:
        return trainerClass == TRAINERCLASS_LEADER_PRYCE;
    case SPECIES_VENONAT:
    case SPECIES_VENOMOTH:
        return trainerClass == TRAINERCLASS_LEADER_SABRINA;
    case SPECIES_ODDISH:
    case SPECIES_GLOOM:
    case SPECIES_VILEPLUME:
    case SPECIES_BELLOSSOM:
    case SPECIES_GASTLY:
    case SPECIES_HAUNTER:
    case SPECIES_GENGAR:
        return trainerClass == TRAINERCLASS_ELITE_FOUR_KAREN;
    case SPECIES_PINECO:
    case SPECIES_FORRETRESS:
        return trainerClass == TRAINERCLASS_ELITE_FOUR_KOGA;
    case SPECIES_ONIX:
    case SPECIES_STEELIX:
        return trainerClass == TRAINERCLASS_ELITE_FOUR_BRUNO;
    default:
        return FALSE;
    }
}

static BOOL IsTrainerTypeMatch(u16 species, u32 typeMask, u8 exceptionClass)
{
    if (typeMask == 0 || IsTrainerFamilyException(species, exceptionClass)) {
        return TRUE;
    }

    u32 type1 = PokePersonalParaGet(species, PERSONAL_TYPE_1);
    u32 type2 = PokePersonalParaGet(species, PERSONAL_TYPE_2);
    return (typeMask & ((1u << type1) | (1u << type2))) != 0;
}

static u16 GetTrainerSpeciesAtIndex(u16 index, u8 level, u32 branchRoll, u8 stageContext, u8 exceptionClass)
{
    const u16 dexSize = SPECIES_ARCEUS - SPECIES_BULBASAUR + 1;
    u16 species = index < dexSize ? SPECIES_BULBASAUR + index : sExtraTrainerSpecies[index - dexSize];
    if (!IsRandomTrainerSpeciesEligible(species)) {
        return SPECIES_NONE;
    }
    // Misty's signature line can start at Togepi, which ordinary trainers skip.
    BOOL allowBabies = exceptionClass == TRAINERCLASS_LEADER_MISTY
        && IsTrainerFamilyException(species, exceptionClass);
    species = AdjustEncounterSpeciesForLevel(species, level, branchRoll, stageContext, allowBabies);
    return IsRandomTrainerSpeciesEligible(species) ? species : SPECIES_NONE;
}

static BOOL IsUnusedTrainerSpecies(u16 species, const u16 *usedSpecies, int usedCount)
{
    if (species == SPECIES_NONE) {
        return FALSE;
    }
    for (int i = 0; i < usedCount; i++) {
        if (species == usedSpecies[i]) {
            return FALSE;
        }
    }
    return TRUE;
}

static u16 PickRandomTrainerSpecies(u8 level, u32 branchRoll, u8 stageContext, u32 typeMask, u8 exceptionClass,
    const u16 *usedSpecies, int usedCount)
{
    if (exceptionClass == TRAINERCLASS_KIMONO_GIRL) {
        static const u16 eeveeFamily[] = {
            SPECIES_EEVEE, SPECIES_VAPOREON, SPECIES_JOLTEON, SPECIES_FLAREON, SPECIES_ESPEON,
            SPECIES_UMBREON, SPECIES_LEAFEON, SPECIES_GLACEON, SPECIES_SYLVEON,
        };
        u16 available[NELEMS(eeveeFamily)];
        int count = 0;
        for (u32 i = 0; i < NELEMS(eeveeFamily); i++) {
            u16 species = eeveeFamily[i];
            if (IsUnusedTrainerSpecies(species, usedSpecies, usedCount)) {
                available[count++] = species;
            }
        }
        return count ? available[branchRoll % count] : SPECIES_NONE;
    }

    const u16 poolSize = SPECIES_ARCEUS - SPECIES_BULBASAUR + 1 + NELEMS(sExtraTrainerSpecies);
    u16 fallback = SPECIES_NONE;

    for (int attempt = 0; attempt < 32; attempt++) {
        u16 species = GetTrainerSpeciesAtIndex(gf_rand() % poolSize, level, branchRoll, stageContext, exceptionClass);
        if (IsUnusedTrainerSpecies(species, usedSpecies, usedCount)) {
            if (IsTrainerTypeMatch(species, typeMask, exceptionClass)) {
                return species;
            }
            if (fallback == SPECIES_NONE) {
                fallback = species;
            }
        }
    }

    // Sparse type pools still get a matching species if one exists at this level.
    u16 start = gf_rand() % poolSize;
    for (u16 i = 0; i < poolSize; i++) {
        u16 index = start + i;
        if (index >= poolSize) {
            index -= poolSize;
        }
        u16 species = GetTrainerSpeciesAtIndex(index, level, branchRoll, stageContext, exceptionClass);
        if (IsUnusedTrainerSpecies(species, usedSpecies, usedCount)) {
            if (IsTrainerTypeMatch(species, typeMask, exceptionClass)) {
                return species;
            }
            if (fallback == SPECIES_NONE) {
                fallback = species;
            }
        }
    }
    return fallback;
}
#endif // TRAINER_RANDOM_SPECIES

#endif // TRAINER_SPECIES_STAGE_ADJUST

#endif // TRAINER_LEVEL_SCALING

/**
 *  @brief create the trainer Party from the trainer data file and trainer party file
 *
 *  @param bp battle param
 *  @param num trainer index to read from both ARC_TRAINER_DATA and ARC_TRAINER_PARTY_DATA
 *  @param heapID heap to use for memory usage
 */
void MakeTrainerPokemonParty(struct BATTLE_PARAM *bp, int num, int heapID)
{
    u8 *buf = NULL;
    int i, j;
    u32 rnd_tmp = 136, rnd, seed_tmp;
    u8 pow;

    seed_tmp = gf_get_seed();

    PokeParty_Init(bp->poke_party[num], 6);

    u8 pokecount = bp->trainer_data[num].poke_count;
    u8 randomorder_flag = pokecount & TRAINER_DATA_RANDOM_PARTY_ORDER;
    pokecount &= 0x7f;

#if defined(TRAINER_RANDOM_SPECIES) && defined(TRAINER_LEVEL_SCALING) && defined(TRAINER_SPECIES_STAGE_ADJUST)
    u8 generatedBadgeCount = 0;
    u16 generatedSpecies[6];
    BOOL generateSpecies = (num == BATTLER_ENEMY || num == BATTLER_ENEMY2)
        && (bp->fight_type & BATTLE_TYPE_TRAINER)
        && !(bp->fight_type & (BATTLE_TYPE_LINK | BATTLE_TYPE_FRONTIER | BATTLE_TYPE_TUTORIAL))
        && !(bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_ADDITIONAL_FLAGS);
#endif

    // goal:  get rid of massive switch statement with each individual byte.  make the trainer type a bitfield
    u32 id;
    u32 encounterBranchRoll;
    u16 species = 0, adjustedSpecies = 0, item = 0, ability = 0, level = 0, ball = 0, hp = 0, atk = 0, def = 0, speed = 0, spatk = 0, spdef = 0, ab1 = 0, ab2 = 0;
    u16 offset = 0;
    u16 moves[4];
    u8 ivnums[6];
    u8 evnums[6];
    u8 ppcounts[4];
    u16 *nickname = NULL;
    u8 form_no = 0, abilityslot = 0, nature = 0, ballseal = 0, shinylock = 0, status = 0;
    u32 additionalflags = 0;

#ifdef TRAINER_LEVEL_SCALING
    u8 trainerLevelCap;
    u8 trainerLevelFloor;
    BOOL gymLeaderUsesCap;
    {
        void *saveData = SaveBlock2_get();
        struct PlayerProfile *profile = saveData != NULL ? Sav2_PlayerData_GetProfileAddr(saveData) : NULL;
        u8 badgeCount = profile != NULL ? PlayerProfile_CountBadges(profile) : 0;

#if defined(TRAINER_RANDOM_SPECIES) && defined(TRAINER_SPECIES_STAGE_ADJUST)
        if (generateSpecies) {
            generatedBadgeCount = badgeCount;
            pokecount = 3 + (badgeCount < 3 ? badgeCount : 3);
            if (bp->trainer_id[BATTLER_ENEMY] != 0 && bp->trainer_id[BATTLER_ENEMY2] != 0) {
                pokecount = (pokecount + 1) / 2;
            }
            bp->trainer_data[num].poke_count = pokecount | randomorder_flag;

            u32 playerId = profile != NULL ? profile->id : 0;
            gf_srand(playerId ^ ((u32)bp->trainer_id[num] * 0x9E3779B9u) ^ ((u32)badgeCount * 0x85EBCA6Bu));
        }
#endif
        trainerLevelCap = GetPlayerLevelCapForBadges(badgeCount);
        trainerLevelFloor = trainerLevelCap - 4;
#if defined(TRAINER_GYM_LEADER_CAP_LEVEL)
        gymLeaderUsesCap = IsGymLeaderTrainerClass(bp->trainer_data[num].tr_type);
#else
        gymLeaderUsesCap = FALSE;
#endif
    }
#endif

#if defined(TRAINER_RANDOM_SPECIES) && defined(TRAINER_LEVEL_SCALING) && defined(TRAINER_SPECIES_STAGE_ADJUST)
    if (!generateSpecies)
#endif
    {
        buf = (u8 *)sys_AllocMemory(heapID, sizeof(struct FULL_TRAINER_MON_DATA_STRUCTURE) * 6);
        TT_TrainerPokeDataGet(bp->trainer_id[num], buf);
        nickname = sys_AllocMemory(heapID, 11 * sizeof(u16));
        if (TT_TrainerTypeSexGet(bp->trainer_data[num].tr_type) == 1) {
            rnd_tmp = 120;
        }
    }

#if defined(TRAINER_RANDOM_SPECIES) && defined(TRAINER_LEVEL_SCALING) && defined(TRAINER_SPECIES_STAGE_ADJUST)
    u8 trainerClass = bp->trainer_data[num].tr_type;
    u8 profileClass = GetTrainerGymClass(bp->trainer_id[num], trainerClass);
    u32 typeMask = GetTrainerTypeMask(profileClass);
    // Gym subordinates borrow the type filter but none of the class exceptions.
    u8 exceptionClass = profileClass == trainerClass ? trainerClass : 0;
#endif

    int partyOrder[pokecount];
    if (randomorder_flag) {
        if (gf_rand() % 2 == 0) {
            for (i = 0; i < pokecount; i++) {
                partyOrder[i] = pokecount - 1 - i;
            }
        } else {
            for (i = 0; i < pokecount; i++) {
                partyOrder[i] = i;
            }
        }
    } else {
        for (i = 0; i < pokecount; i++) {
            partyOrder[i] = i;
        }
    }

    if (randomorder_flag && pokecount > 1) {
        int numtimes = gf_rand() % 6 + 1;
        for (i = 0; i < numtimes; i++) {
            randomize(partyOrder, pokecount);
        }
    }

    struct PartyPokemon *mons[pokecount];

    for (i = 0; i < pokecount; i++) {
#if defined(TRAINER_RANDOM_SPECIES) && defined(TRAINER_LEVEL_SCALING) && defined(TRAINER_SPECIES_STAGE_ADJUST)
        if (generateSpecies) {
            level = gymLeaderUsesCap ? trainerLevelCap : PickTrainerLevelInBand(trainerLevelFloor, trainerLevelCap);
            encounterBranchRoll = gf_rand();
            encounterBranchRoll |= (u32)gf_rand() << 16;
            gLastPokemonLevelForMoneyCalc = level;
            species = PickRandomTrainerSpecies((u8)level, encounterBranchRoll,
                TrainerEncounterStageContext(trainerClass), typeMask, exceptionClass, generatedSpecies, i);
            if (species == SPECIES_NONE) {
                // Retain the relative party order of the slots that were built.
                int count = 0;
                for (int slot = 0; slot < pokecount; slot++) {
                    if (partyOrder[slot] < i) {
                        partyOrder[count++] = partyOrder[slot];
                    }
                }
                pokecount = count;
                bp->trainer_data[num].poke_count = pokecount | randomorder_flag;
                break;
            }
            generatedSpecies[i] = species;
            mons[i] = AllocMonZeroed(heapID);
            rnd = gf_rand();
            rnd |= (u32)gf_rand() << 16;
            // PokeParaSet rolls all six IVs when the IV argument exceeds 31.
            PokeParaSet(mons[i], species, level, 32, 1, rnd, 2, 0);
            ApplyEncounterGenderAfterStageAdjust(mons[i]);
            ResetPartyPokemonAbility(mons[i]);
            ChangeToBattleForm(mons[i]);
            SetGeneratedTrainerEVs(mons[i], generatedBadgeCount, IsGymLeaderTrainerClass(trainerClass));
            RecalcPartyPokemonStats(mons[i]);
            continue;
        }
#endif

        mons[i] = AllocMonZeroed(heapID);
        // ivs field
        pow = buf[offset];
        offset++;

        // abilityslot field
        abilityslot = buf[offset];
        offset++;

        // level field
        level = buf[offset] | (buf[offset + 1] << 8);
#ifdef TRAINER_LEVEL_SCALING
        if (gymLeaderUsesCap) {
            level = trainerLevelCap;
        } else {
            level = PickTrainerLevelInBand(trainerLevelFloor, trainerLevelCap);
        }
        /* One seed per slot for stage branches and probability rolls. */
        encounterBranchRoll = (u32)gf_rand() | ((u32)gf_rand() << 16);
#else
        encounterBranchRoll = 0;
#endif
        gLastPokemonLevelForMoneyCalc = level; // ends up being the last level at the end of the loop that we use for the money calc loop default case
        offset += 2;

        // species field
        species = buf[offset] | (buf[offset + 1] << 8);
        offset += 2;
        form_no = (species & 0xF800) >> 11;
        species &= 0x07FF;

        // item field - conditional
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_ITEMS) {
            item = buf[offset] | (buf[offset + 1] << 8);
            offset += 2;
        }

        // moves field - conditional
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_MOVES) {
            for (j = 0; j < 4; j++) {
                moves[j] = buf[offset] | (buf[offset + 1] << 8);
                offset += 2;
            }
        }

        // ability field
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_ABILITY) {
            ability = buf[offset] | (buf[offset + 1] << 8);
            offset += 2;
        }

        // custom ball field
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_BALL) {
            ball = buf[offset] | (buf[offset + 1] << 8);
            offset += 2;
        }

        // ivs and evs fields
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_IV_EV_SET) {
            for (j = 0; j < 6; j++) {
                ivnums[j] = buf[offset];
                if (ivnums[j] > 31) {
                    ivnums[j] = 31;
                }
                offset++;
            }

            for (j = 0; j < 6; j++) {
                evnums[j] = buf[offset];
                offset++;
            }
        }

        // nature field
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_NATURE_SET) {
            nature = buf[offset];
            offset++;
        }

        // shiny lock field
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_SHINY_LOCK) {
            shinylock = buf[offset];
            offset++;
        }

        // reads extra flags from the trainer pokemon file
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_ADDITIONAL_FLAGS) {
            additionalflags = buf[offset] | (buf[offset + 1] << 8) | (buf[offset + 2] << 16) | (buf[offset + 3] << 24);
            offset += 4;

            // status pre-set field
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_STATUS) {
                status = buf[offset] | (buf[offset + 1] << 8) | (buf[offset + 2] << 16) | (buf[offset + 3] << 24);
                offset += 4;
            }

            // custom hp stat field
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_HP) {
                hp = buf[offset] | (buf[offset + 1] << 8);
                offset += 2;
            }

            // custom atk stat field
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_ATK) {
                atk = buf[offset] | (buf[offset + 1] << 8);
                offset += 2;
            }

            // custom def stat field
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_DEF) {
                def = buf[offset] | (buf[offset + 1] << 8);
                offset += 2;
            }

            // custom speed stat field
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_SPEED) {
                speed = buf[offset] | (buf[offset + 1] << 8);
                offset += 2;
            }

            // custom spatk stat field
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_SP_ATK) {
                spatk = buf[offset] | (buf[offset + 1] << 8);
                offset += 2;
            }

            // custom spdef stat field
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_SP_DEF) {
                spdef = buf[offset] | (buf[offset + 1] << 8);
                offset += 2;
            }

            // move PP counts field
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_PP_COUNTS) {
                for (j = 0; j < 4; j++) {
                    ppcounts[j] = buf[offset];
                    offset++;
                }
            }

            // nickname field
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_NICKNAME) {
                for (j = 0; j < 11; j++) {
                    nickname[j] = buf[offset] | (buf[offset + 1] << 8);
                    offset += 2;
                }
            }
        }

        // ball seal field
        ballseal = buf[offset] | (buf[offset + 1] << 8);
        offset += 2;

        // now set mon data
        try_force_gender_maybe(species, form_no, abilityslot, &rnd_tmp);
        rnd = pow + level + species + bp->trainer_id[num];
        gf_srand(rnd);
        for (j = 0; j < bp->trainer_data[num].tr_type; j++) {
            rnd = gf_rand();
        }
        rnd = (rnd << 8) + rnd_tmp;
        pow = pow * 31 / 255;
        PokeParaSet(mons[i], species, level, pow, 1, rnd, 2, 0);
        SetMonData(mons[i], MON_DATA_FORM, &form_no);

        // set default abilities
        adjustedSpecies = PokeOtherFormMonsNoGet(species, form_no);
        ab1 = PokePersonalParaGet(adjustedSpecies, PERSONAL_ABILITY_1);
        ab2 = PokePersonalParaGet(adjustedSpecies, PERSONAL_ABILITY_2);
        if (ab2 != 0) {
            if (abilityslot & 1 || abilityslot == TRAINER_POKEMON_ABILITY_2) {
                SetMonData(mons[i], MON_DATA_ABILITY, (u16 *)&ab2);
            } else {
                SetMonData(mons[i], MON_DATA_ABILITY, (u16 *)&ab1);
            }
        } else {
            SetMonData(mons[i], MON_DATA_ABILITY, (u16 *)&ab1);
        }

        // if abilityslot is 2 force hidden ability with the bit set.  this specifically to cover darmanitan with zen mode switching between forms and such.
        if (abilityslot == TRAINER_POKEMON_ABILITY_HIDDEN) {
            u16 hiddenability = GetMonHiddenAbility(species, form_no);
            SET_MON_HIDDEN_ABILITY_BIT(mons[i]);
            SetMonData(mons[i], MON_DATA_ABILITY, (u16 *)&hiddenability);
        }

        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_ITEMS) {
            SetMonData(mons[i], MON_DATA_HELD_ITEM, &item);
        }
#if !defined(TRAINER_LEVEL_APPROPRIATE_MOVES)
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_MOVES) {
            for (j = 0; j < 4; j++) {
#ifdef BLOCK_LEARNING_UNIMPLEMENTED_MOVES
                if (IsMoveUnimplemented(moves[j])) {
                    moves[j] = MOVE_NONE;
                }
#endif
                SetPartyPokemonMoveAtPos(mons[i], moves[j], j);
            }
        }
#endif
        TrainerCBSet(ballseal, mons[i], heapID);
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_ABILITY) {
            SetMonData(mons[i], MON_DATA_ABILITY, &ability);
        }
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_BALL) {
            SetMonData(mons[i], MON_DATA_POKEBALL, &ball);
        }
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_IV_EV_SET) {
            for (j = 0; j < 6; j++) {
                SetMonData(mons[i], MON_DATA_HP_IV + j, &ivnums[j]);
            }

            for (j = 0; j < 6; j++) {
                SetMonData(mons[i], MON_DATA_HP_EV + j, &evnums[j]);
            }
        }
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_NATURE_SET) {
            u32 pid = GetMonData(mons[i], MON_DATA_PERSONALITY, NULL);
            u8 currentNature = pid % 25;
            pid = pid + nature - currentNature;
            SetMonData(mons[i], MON_DATA_PERSONALITY, &pid);
        }
        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_SHINY_LOCK) {
            u32 pid = GetMonData(mons[i], MON_DATA_PERSONALITY, NULL);
            if (shinylock != 0) {
                do {
                    id = (gf_rand() | (gf_rand() << 16));
                } while (!SHINY_CHECK(id, pid));
                SetMonData(mons[i], MON_DATA_OTID, &id);
            }
        }

        ChangeToBattleForm(mons[i]);

#if defined(TRAINER_LEVEL_SCALING) && defined(TRAINER_SPECIES_STAGE_ADJUST)
        ApplyEncounterStageAdjustToMon(mons[i], (u8)level, encounterBranchRoll,
            TrainerEncounterStageContext(bp->trainer_data[num].tr_type), FALSE);
        ResetPartyPokemonAbility(mons[i]);
#endif

#if defined(TRAINER_LEVEL_SCALING) && defined(TRAINER_LEVEL_APPROPRIATE_MOVES)
        ClearMonMoves(mons[i]);
        InitBoxMonMoveset(&mons[i]->box);
#endif

        ApplyEncounterGenderAfterStageAdjust(mons[i]);

        RecalcPartyPokemonStats(mons[i]); // recalculate stats here

        if (bp->trainer_data[num].data_type & TRAINER_DATA_TYPE_ADDITIONAL_FLAGS) {
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_STATUS) {
                SetMonData(mons[i], MON_DATA_STATUS, &status);
            }
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_HP) {
                SetMonData(mons[i], MON_DATA_MAXHP, &hp);
                SetMonData(mons[i], MON_DATA_HP, &hp);
            }
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_ATK) {
                SetMonData(mons[i], MON_DATA_ATTACK, &atk);
            }
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_DEF) {
                SetMonData(mons[i], MON_DATA_DEFENSE, &def);
            }
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_SPEED) {
                SetMonData(mons[i], MON_DATA_SPEED, &speed);
            }
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_SP_ATK) {
                SetMonData(mons[i], MON_DATA_SPECIAL_ATTACK, &spatk);
            }
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_SP_DEF) {
                SetMonData(mons[i], MON_DATA_SPECIAL_DEFENSE, &spdef);
            }
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_PP_COUNTS) {
                for (j = 0; j < 4; j++) {
                    SetMonData(mons[i], MON_DATA_MOVE1PP + j, &ppcounts[j]);
                }
            }
            if (additionalflags & TRAINER_DATA_EXTRA_TYPE_NICKNAME) {
                u32 one = 1;

                SetMonData(mons[i], MON_DATA_HAS_NICKNAME, &one);
                SetMonData(mons[i], MON_DATA_NICKNAME, nickname);
            }
        }
        TrainerMonHandleFrustration(mons[i]);
    }

#if defined(TRAINER_RANDOM_SPECIES) && defined(TRAINER_LEVEL_SCALING) && defined(TRAINER_SPECIES_STAGE_ADJUST)
    if (generateSpecies) {
        BuildGeneratedTrainerMovesets(mons, partyOrder, pokecount, generatedBadgeCount);
        UpgradeGeneratedTrainerIVs(mons, pokecount, generatedBadgeCount, IsGymLeaderTrainerClass(trainerClass));
        for (i = 0; i < pokecount; i++) {
            TrainerMonHandleFrustration(mons[i]);
            SetGeneratedTrainerHeldItem(mons[i], generatedBadgeCount);
        }
    }
#endif

    for (i = 0; i < pokecount; i++) {
        PokeParty_Add(bp->poke_party[num], mons[partyOrder[i]]);
        sys_FreeMemoryEz(mons[i]);
    }

    if (buf != NULL) {
        sys_FreeMemoryEz(buf);
        sys_FreeMemoryEz(nickname);
    }

    gf_srand(seed_tmp);

#ifdef DEBUG_BATTLE_SCENARIOS
    // Override parties with test scenario if enabled
    TestBattle_OverrideParties(bp);
#endif

    // Change battle forms for player party
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 6; j++) {
            struct PartyPokemon *mon = Party_GetMonByIndex(bp->poke_party[i], j);
            if (mon != NULL) {
                ChangeToBattleForm(mon);
                RecalcPartyPokemonStats(mon);
            }
        }
    }
}

extern u32 space_for_setmondata;

/**
 *  @brief add a PartyPokemon to the "wild battler"'s party
 *
 *  @param inTarget battler whose party to add to
 *  @param encounterInfo various encounter information structure
 *  @param encounterPartyPokemon PartyPokemon to modify and add
 *  @param encounterBattleParam battle param
 *  @return TRUE if PokeParty_Add was successful
 */
BOOL LONG_CALL AddWildPartyPokemon(int inTarget, EncounterInfo *encounterInfo, struct PartyPokemon *encounterPartyPokemon, struct BATTLE_PARAM *encounterBattleParam)
{
    u8 change_form = 0;
    u8 form_no;
    u16 species;

#ifndef IMPLEMENT_WILD_BERRY_HOLD
    int range = 0;

    if (encounterInfo->isEgg == 0 && encounterInfo->ability == ABILITY_COMPOUND_EYES) {
        range = 1;
    }
#endif

    species = GetMonData(encounterPartyPokemon, MON_DATA_SPECIES, NULL);

    if (space_for_setmondata != 0) {
        change_form = 1;
        form_no = space_for_setmondata; //(species & 0xF800) >> 11;
        space_for_setmondata = 0;
    }

#ifdef IMPLEMENT_WILD_BERRY_HOLD
    {
        int range = 0;

        if (encounterInfo->isEgg == 0 && encounterInfo->ability == ABILITY_COMPOUND_EYES) {
            range = 1;
        }
        WildMonSetRandomHeldItem(encounterPartyPokemon, encounterBattleParam->fight_type, range);
    }
#else
    WildMonSetRandomHeldItem(encounterPartyPokemon, encounterBattleParam->fight_type, range);
#endif

    if (species == SPECIES_UNOWN) {
        change_form = 1;
        form_no = GrabAndRegisterUnownForm(encounterInfo);
    } else if (species == SPECIES_DEERLING || species == SPECIES_SAWSBUCK) {
        UpdatePassiveForms(encounterPartyPokemon);
    }

    if (CheckScriptFlag(HIDDEN_ABILITIES_FLAG) == 1) {
        SET_MON_HIDDEN_ABILITY_BIT(encounterPartyPokemon)
        ClearScriptFlag(HIDDEN_ABILITIES_FLAG);
        ResetPartyPokemonAbility(encounterPartyPokemon);
    }

    if (change_form) {
        SetMonData(encounterPartyPokemon, MON_DATA_FORM, (u8 *)&form_no);
        RecalcPartyPokemonStats(encounterPartyPokemon);
        ResetPartyPokemonAbility(encounterPartyPokemon);
        InitBoxMonMoveset(&encounterPartyPokemon->box);
    }

    ChangeToBattleForm(encounterPartyPokemon);

    return PokeParty_Add(encounterBattleParam->poke_party[inTarget], encounterPartyPokemon);
}

void LONG_CALL SetupAndStartTutorialBattle(TaskManager *taskManager)
{
    struct BattleSetup *setup = BattleSetup_New_Tutorial(11, taskManager->fieldSystem);

    struct PartyPokemon *marill = Party_GetMonByIndex(setup->party[BATTLER_PLAYER], 0);

    // move slot 1 is tackle
    u16 data = MOVE_TACKLE;
    SetMonData(marill, MON_DATA_MOVE1, &data);
    data = GetMoveMaxPP(data, 0);
    SetMonData(marill, MON_DATA_MOVE1PP, &data);
    data = 0;
    SetMonData(marill, MON_DATA_MOVE1PPUP, &data);

    // move slot 2 is tail whip
    data = MOVE_TAIL_WHIP;
    SetMonData(marill, MON_DATA_MOVE2, &data);
    data = GetMoveMaxPP(data, 0);
    SetMonData(marill, MON_DATA_MOVE2PP, &data);
    data = 0;
    SetMonData(marill, MON_DATA_MOVE2PPUP, &data);

    // move slot 3 and 4 none
    data = MOVE_NONE;
    SetMonData(marill, MON_DATA_MOVE3, &data);
    SetMonData(marill, MON_DATA_MOVE4, &data);

    void *encounter = Encounter_New(setup, BattleSetup_GetWildTransitionEffect(setup), BattleSetup_GetWildBattleMusic(setup), NULL);

    TaskManager_Call(taskManager, Task_TutorialBattle, encounter);
}
