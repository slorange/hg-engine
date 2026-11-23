#include "../include/config.h"
#include "../include/constants/file.h"
#include "../include/constants/maps.h"
#include "../include/constants/roamer.h"
#include "../include/constants/species.h"
#include "../include/battle_controller_player.h"
#include "../include/debug.h"
#include "../include/map_events_internal.h"
#include "../include/message.h"
#include "../include/roamer.h"
#include "../include/pokedex.h"
#include "../include/save.h"
#include "../include/script.h"
#include "../include/types.h"

/* In order to change the adjacent routes we would need to hook
 * https://github.com/pret/pokeheartgold/blob/d72700a52ad27ddf47847009a85b4bc9c85fa283/src/field_roamer.c#L256
 */
#ifdef EXPAND_ROAMERS
static const u32 sRoamerLocations[ROAMER_LOC_COUNT] = {
    // Johto
    MAP_R29,
    MAP_R30,
    MAP_R31,
    MAP_R32,
    MAP_R33,
    MAP_R34,
    MAP_R35,
    MAP_R36,
    MAP_R37,
    MAP_R38,
    MAP_R39,
    MAP_R42,
    MAP_R43,
    MAP_R44,
    MAP_R45,
    MAP_R46,

    // Kanto
    MAP_R01,
    MAP_R02,
    MAP_R03,
    MAP_R04,
    MAP_R05,
    MAP_R06,
    MAP_R07,
    MAP_R08,
    MAP_R09,
    MAP_R10,
    MAP_R11,
    MAP_R12,
    MAP_R13,
    MAP_R14,
    MAP_R15,
    MAP_R16,
    MAP_R17,
    MAP_R18,
    MAP_W19,
    MAP_W20,
    MAP_W21,
    MAP_R22,
    MAP_R24,
    MAP_R26,
    MAP_R28,
};

void LONG_CALL RoamerLocationSetRandom(void *roamerSave, u8 roamer_idx, u32 last_loc)
{
    u32 roamer_cur_loc, roamer_test_loc;
    u8 loc_min, loc_num;
    u8 loc_cur_rand;

    roamer_cur_loc = sRoamerLocations[Roamer_GetLocation(roamerSave, roamer_idx)];
    if (roamer_idx == ROAMER_RAIKOU || roamer_idx == ROAMER_ENTEI) {
        loc_num = ROAMER_LOC_JOHTO_COUNT;
        loc_min = ROAMER_LOC_JOHTO_START;
    } else {
        loc_num = ROAMER_LOC_KANTO_COUNT;
        loc_min = ROAMER_LOC_KANTO_START;
    }
    do {
        loc_cur_rand = (gf_rand() % loc_num) + loc_min;
        roamer_test_loc = sRoamerLocations[loc_cur_rand];
    } while (roamer_test_loc == last_loc || roamer_test_loc == roamer_cur_loc);
    ApplyRoamerLocation(roamerSave, roamer_idx, loc_cur_rand, roamer_test_loc);
}

void LONG_CALL Save_CreateRoamerByID(SaveData *saveData, u8 idx)
{
    void *profile;
    void *roamerSave = EncDataSave_GetSaveDataPtr(saveData);
    Roamer *roamerStats = Roamers_GetRoamMonStats(roamerSave, idx);
    struct PartyPokemon *mon;
    u16 species;
    u8 level;

    switch (idx) {
    case ROAMER_RAIKOU:
        species = SPECIES_RAIKOU;
        level = 40;
        break;
    case ROAMER_ENTEI:
        species = SPECIES_ENTEI;
        level = 40;
        break;
    case ROAMER_LATIAS:
        species = SPECIES_LATIAS;
        level = 35;
        break;
    case ROAMER_LATIOS:
        species = SPECIES_LATIOS;
        level = 35;
        break;
    default:
        GF_ASSERT(FALSE);
        return;
    }

    SetRoamerData(roamerStats, ROAMER_DATA_SPECIES, species);
    SetRoamerData(roamerStats, ROAMER_DATA_LEVEL, level);

    profile = Sav2_PlayerData_GetProfileAddr(saveData);
    mon = AllocMonZeroed(4);
    ZeroMonData(mon);
    PokeParaSet(mon, species, level, 32, FALSE, 0, OT_ID_PRESET, PlayerProfile_GetTrainerID_VisibleHalf(profile));
    SetRoamerData(roamerStats, ROAMER_DATA_STATUS, 0);
    SetRoamerData(roamerStats, ROAMER_DATA_ACTIVE, TRUE);
    SetRoamerData(roamerStats, ROAMER_DATA_IVS, GetMonData(mon, MON_DATA_IVS_WORD, NULL));
    SetRoamerData(roamerStats, ROAMER_DATA_PERSONALITY, GetMonData(mon, MON_DATA_PERSONALITY, NULL));
    SetRoamerData(roamerStats, ROAMER_DATA_HP, GetMonData(mon, MON_DATA_MAXHP, NULL));
    sys_FreeMemoryEz(mon);
    RoamerLocationSetRandom(roamerSave, idx, PlayerLocationHistoryGetBack(roamerSave));
}

u8 LONG_CALL SpeciesToRoamerIdx(u16 species)
{
    switch (species) {
    case SPECIES_RAIKOU:
        return ROAMER_RAIKOU;
    case SPECIES_ENTEI:
        return ROAMER_ENTEI;
    case SPECIES_LATIOS:
        return ROAMER_LATIOS;
    case SPECIES_LATIAS:
        return ROAMER_LATIAS;
    default:
        GF_ASSERT(FALSE);
        return ROAMER_MAX;
    }
}
#endif

// Keep these form-specific roamers separate from the native species-based slots.
static const u8 sUnownRoamerMaps[2][16] = {
    { MAP_R29, MAP_R30, MAP_R31, MAP_R32, MAP_R33, MAP_R34, MAP_R35, MAP_R36,
      MAP_R37, MAP_R38, MAP_R39, MAP_R42, MAP_R43, MAP_R44, MAP_R45, MAP_R46 },
    { MAP_R01, MAP_R02, MAP_R03, MAP_R04, MAP_R05, MAP_R06, MAP_R07, MAP_R08,
      MAP_R09, MAP_R10, MAP_R11, MAP_R13, MAP_R14, MAP_R15, MAP_R16, MAP_R17 },
};

enum {
    UNOWN_ROAMER_KNOCKED_OUT = 255,
    ALPH_PUZZLE_FIRST_FLAG = 2423,
    ALPH_PUZZLE_LAST_FLAG = 2426,
};

void LONG_CALL UpdateNativeRoamerLocationHistory(void *roamerSave, u32 map);
void LONG_CALL CopyWildBattleResultToField(struct BattleSetup *setup, FieldSystem *field);
BOOL LONG_CALL Save_VarsFlags_CheckFlagInArray(struct ScriptState *flags, u16 id);

static BOOL AllAlphPuzzlesSolved(void *save)
{
    struct ScriptState *flags = SavArray_Flags_get(save);
    for (u16 id = ALPH_PUZZLE_FIRST_FLAG; id <= ALPH_PUZZLE_LAST_FLAG; id++) {
        if (!Save_VarsFlags_CheckFlagInArray(flags, id)) {
            return FALSE;
        }
    }
    return TRUE;
}

static void MoveUnownRoamer(u8 *route)
{
    if (*route == 0 || *route > 16) {
        *route = 1 + gf_rand() % 16;
    } else {
        u8 next = 1 + gf_rand() % 15;
        *route = next + (next >= *route);
    }
}

static void UpdateUnownRoamerRoutes(void *save, struct SAVE_MISC_DATA *misc, u16 map)
{
    if (misc->unownRoamerLastMap == map + 1) {
        return;
    }
    if (misc->unownRoamerLastMap == 0 && !AllAlphPuzzlesSolved(save)) {
        return;
    }

    misc->unownRoamerLastMap = map + 1;
    const struct Save_DexData *dex = SaveData_GetDexPtr(save);
    for (u8 i = 0; i < 2; i++) {
        if (misc->unownRoamerRoute[i] != UNOWN_ROAMER_KNOCKED_OUT
            && !Pokedex_HasCaughtUnownForm(dex, UNOWN_ROAMER_FIRST_FORM + i)) {
            MoveUnownRoamer(&misc->unownRoamerRoute[i]);
        }
    }
}

void UnownRoamer_UpdateLocation(void *roamerSave, u32 map)
{
    UpdateNativeRoamerLocationHistory(roamerSave, map);
    void *save = SaveBlock2_get();
    if (save != NULL) {
        UpdateUnownRoamerRoutes(save, Sav2_Misc_get(save), map);
    }
}

BOOL LONG_CALL UnownRoamer_TryEncounter(u16 map, u8 *form)
{
    for (u8 region = 0; region < 2; region++) {
        for (u8 i = 0; i < 16; i++) {
            if (sUnownRoamerMaps[region][i] != map) {
                continue;
            }
            void *save = SaveBlock2_get();
            if (save == NULL) {
                return FALSE;
            }
            struct SAVE_MISC_DATA *misc = Sav2_Misc_get(save);
            if (misc->unownRoamerLastMap == 0) {
                UpdateUnownRoamerRoutes(save, misc, map);
            }
            u8 letter = UNOWN_ROAMER_FIRST_FORM + region;
            if (misc->unownRoamerRoute[region] != i + 1
                || Pokedex_HasCaughtUnownForm(SaveData_GetDexPtr(save), letter)
                || (gf_rand() & 1) == 0) {
                return FALSE;
            }
            *form = letter;
            return TRUE;
        }
    }
    return FALSE;
}

void LONG_CALL UnownRoamer_PrepareMon(struct PartyPokemon *mon, u8 form)
{
    struct UnownRoamerBattleState *state =
        &Sav2_Misc_get(SaveBlock2_get())->unownRoamerBattle[form - UNOWN_ROAMER_FIRST_FORM];
    if (!state->initialized) {
        u32 low = gf_rand();
        state->personality = low | (gf_rand() << 16);
        state->initialized = TRUE;
    }

    SetMonPersonality(mon, state->personality);
    // Derive consistent IVs from the saved personality without enlarging the save.
    u32 ivs = state->personality * 0x6C078965u + 1;
    for (u8 i = 0; i < 6; i++) {
        u8 iv = (ivs >> (i * 5)) & 31;
        SetMonData(mon, MON_DATA_HP_IV + i, &iv);
    }
}

void LONG_CALL UnownRoamer_RestoreCondition(struct PartyPokemon *mon, u8 form)
{
    const struct UnownRoamerBattleState *state =
        &Sav2_Misc_get(SaveBlock2_get())->unownRoamerBattle[form - UNOWN_ROAMER_FIRST_FORM];
    if (state->hp != 0) {
        u32 maxHp = GetMonData(mon, MON_DATA_MAXHP, NULL);
        u16 hp = state->hp < maxHp ? state->hp : maxHp;
        u32 status = state->status;
        SetMonData(mon, MON_DATA_HP, &hp);
        SetMonData(mon, MON_DATA_STATUS, &status);
    }
}

void UnownRoamer_FinishBattle(struct BattleSetup *setup, FieldSystem *field)
{
    const int outcome = setup->winFlag;
    struct Party *opponents = setup->party[1];
    if (opponents != NULL && opponents->count == 1) {
        struct PartyPokemon *mon = Party_GetMonByIndex(opponents, 0);
        if (GetMonData(mon, MON_DATA_SPECIES, NULL) == SPECIES_UNOWN) {
            u32 form = GetMonData(mon, MON_DATA_FORM, NULL);
            if (form >= UNOWN_ROAMER_FIRST_FORM && form < UNOWN_ROAMER_FIRST_FORM + 2) {
                struct SAVE_MISC_DATA *misc = Sav2_Misc_get(field->savedata);
                u8 index = form - UNOWN_ROAMER_FIRST_FORM;
                u8 *route = &misc->unownRoamerRoute[index];
                struct UnownRoamerBattleState *state = &misc->unownRoamerBattle[index];
                u16 hp = GetMonData(mon, MON_DATA_HP, NULL);
                if (outcome == BATTLE_OUTCOME_WIN && hp == 0) {
                    *route = UNOWN_ROAMER_KNOCKED_OUT;
                    state->hp = 0;
                    state->status = 0;
                } else if (outcome != BATTLE_OUTCOME_MON_CAUGHT) {
                    state->hp = hp;
                    state->status = GetMonData(mon, MON_DATA_STATUS, NULL);
                    MoveUnownRoamer(route);
                }
            }
        }
    }
    CopyWildBattleResultToField(setup, field);
}

void UnownRoamer_RecordLeagueClear(HallOfFame *hof, struct Party *party, struct RTCDate *date)
{
    Save_HOF_RecordParty(hof, party, date);
    void *save = SaveBlock2_get();
    if (save == NULL) {
        return;
    }
    struct SAVE_MISC_DATA *misc = Sav2_Misc_get(save);
    for (u8 i = 0; i < 2; i++) {
        if (misc->unownRoamerRoute[i] == UNOWN_ROAMER_KNOCKED_OUT) {
            MoveUnownRoamer(&misc->unownRoamerRoute[i]);
        }
    }
}
