#include "config.h"
#include "debug.h"
#include "types.h"

#include "constants/ability.h"
#include "constants/file.h"
#include "constants/game.h"
#include "constants/hold_item_effects.h"
#include "constants/item.h"
#include "constants/moves.h"
#include "constants/species.h"
#include "constants/weather_numbers.h"

#include "bag.h"
#include "battle.h"
#include "overlay.h"
#include "pokemon.h"
#include "stone_level_evolution.h"
#include "eevee_evolutions.h"
#include "evolution_overlay.h"
#include "rtc.h"
#include "save.h"
#include "script.h"

// top 5 bits are now form bit
// if the form is nonzero, have to set it to that form.  most mons should keep their forms on evolution, but specifically significant gendered mons will need to not

extern u16 gEvolutionSceneOverride[2][2];

/**
 *  @brief get the evolution species for a pokemon.  generalized depending on context
 *         also set form depending on the evolution structure read from armips/data/evodata.s
 *
 *  @param party Party to check through for remoraid and such
 *  @param pokemon PartyPokemon to potentially evolve
 *  @param context EVOCTX_* constant deciding which evolution methods to check
 *  @param usedItem item used on the PartyPokemon, if applicable
 *  @param method_ret pointer to an integer to store the evolution method that was used to evolve
 *  @return the target species to evolev into
 */
u16 GetMonEvolutionInternal(struct Party *party, struct PartyPokemon *pokemon, u8 context, u16 usedItem, int *method_ret)
{
    u16 species;
    u16 heldItem;
    u8 level;
    int i;
    u16 target = SPECIES_NONE;
    u16 friendship;
    u32 pid;
    u8 holdEffect;
    u8 beauty; // for Feebas, but queried unconditionally.
    u16 pid_hi = 0;
    struct Evolution *evoTable;
    int method_local;
    u8 evolutionCount;
    u32 form = GetMonData(pokemon, MON_DATA_FORM, NULL);
    u32 lowkey = 0;

    species = GetMonData(pokemon, MON_DATA_SPECIES, NULL);
    heldItem = GetMonData(pokemon, MON_DATA_HELD_ITEM, NULL);
    pid = GetMonData(pokemon, MON_DATA_PERSONALITY, NULL);
    beauty = GetMonData(pokemon, MON_DATA_BEAUTY, NULL);
    pid_hi = (u16)((pid & 0xFFFF0000) >> 16);
    holdEffect = GetItemData(heldItem, ITEM_PARAM_HOLD_EFFECT, 0);
    level = (u8)GetMonData(pokemon, MON_DATA_LEVEL, NULL);

    if (species != SPECIES_KADABRA && holdEffect == HOLD_EFFECT_NO_EVOLVE && context != EVOCTX_ITEM_USE) {
        return SPECIES_NONE;
    }

    // Spiky-ear Pichu cannot evolve
    if (species == SPECIES_PICHU && form == 1) {
        return SPECIES_NONE;
    }

    if (method_ret == NULL) {
        method_ret = &method_local;
    }

    species = PokeOtherFormMonsNoGet(species, form); // factor in form into species to cover shit like galarian corsola + cap pikachu that can't evolve

    evolutionCount = PlayerEvolutionEntryCount(species);
    evoTable = sys_AllocMemory(3, evolutionCount * sizeof(struct Evolution) + sizeof(u16));
    ReadWholeNarcMemberByIdPair(evoTable, ARC_EVOLUTIONS, species);
    AddEeveeEvolutionEntries(species, evoTable);

    switch (context) {
    case EVOCTX_LEVELUP:
        friendship = (u16)GetMonData(pokemon, MON_DATA_FRIENDSHIP, NULL);
        for (i = 0; i < evolutionCount; i++) {
            switch (evoTable[i].method) {
            case EVO_NONE:
                break;
            case EVO_FRIENDSHIP:
                if (friendship >= FRIENDSHIP_EVOLUTION_THRESHOLD) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_FRIENDSHIP;
                }
                break;
            case EVO_FRIENDSHIP_DAY:
                if (IsNighttime() == 0 && friendship >= FRIENDSHIP_EVOLUTION_THRESHOLD) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_FRIENDSHIP_DAY;
                }
                break;
            case EVO_FRIENDSHIP_NIGHT:
                if (IsNighttime() == 1 && friendship >= FRIENDSHIP_EVOLUTION_THRESHOLD) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_FRIENDSHIP_NIGHT;
                }
                break;
            case EVO_LEVEL:
                if (evoTable[i].param <= level) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_LEVEL;
                }
                break;
            case EVO_TRADE:
                break;
            case EVO_TRADE_ITEM:
                break;
            case EVO_STONE:
                break;
            case EVO_LEVEL_ATK_GT_DEF:
                if (evoTable[i].param <= level && GetMonData(pokemon, MON_DATA_ATTACK, NULL) > GetMonData(pokemon, MON_DATA_DEFENSE, NULL)) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_LEVEL_ATK_GT_DEF;
                }
                break;
            case EVO_LEVEL_ATK_EQ_DEF:
                if (evoTable[i].param <= level && GetMonData(pokemon, MON_DATA_ATTACK, NULL) == GetMonData(pokemon, MON_DATA_DEFENSE, NULL)) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_LEVEL_ATK_EQ_DEF;
                }
                break;
            case EVO_LEVEL_ATK_LT_DEF:
                if (evoTable[i].param <= level && GetMonData(pokemon, MON_DATA_ATTACK, NULL) < GetMonData(pokemon, MON_DATA_DEFENSE, NULL)) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_LEVEL_ATK_LT_DEF;
                }
                break;
            case EVO_LEVEL_PID_LO:
                if (evoTable[i].param <= level && pid_hi % 10 < 5) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_LEVEL_PID_LO;
                }
                break;
            case EVO_LEVEL_PID_HI:
                if (evoTable[i].param <= level && pid_hi % 10 >= 5) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_LEVEL_PID_HI;
                }
                break;
            case EVO_LEVEL_NINJASK:
                if (evoTable[i].param <= level) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_LEVEL_NINJASK;
                }
                break;
            case EVO_LEVEL_SHEDINJA:
                *method_ret = EVO_LEVEL_SHEDINJA;
                break;
            case EVO_BEAUTY:
                if (evoTable[i].param <= beauty) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_BEAUTY;
                }
                break;
            case EVO_STONE_MALE:
                break;
            case EVO_STONE_FEMALE:
                break;
            case EVO_ITEM_DAY:
                if (IsNighttime() == 0 && evoTable[i].param == heldItem) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_ITEM_DAY;
                }
                break;
            case EVO_ITEM_NIGHT:
                if (IsNighttime() == 1 && evoTable[i].param == heldItem) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_ITEM_NIGHT;
                }
                break;
            case EVO_HAS_MOVE:
                if (MonHasMove(pokemon, evoTable[i].param) == TRUE) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_HAS_MOVE;
                }
                break;
            case EVO_OTHER_PARTY_MON:
                if (party != NULL && PartyHasMon(party, evoTable[i].param) == 1) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_OTHER_PARTY_MON;
                }
                break;
            case EVO_LEVEL_MALE:
                if (GetMonData(pokemon, MON_DATA_GENDER, NULL) == POKEMON_GENDER_MALE && evoTable[i].param <= level) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_LEVEL_MALE;
                }
                break;
            case EVO_LEVEL_FEMALE:
                if (GetMonData(pokemon, MON_DATA_GENDER, NULL) == POKEMON_GENDER_FEMALE && evoTable[i].param <= level) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_LEVEL_FEMALE;
                }
                break;
            case EVO_MAGNETIC_FIELD: // Route 10 (kanto power plant outside)
            {
                u32 location = gFieldSysPtr->location->mapId;

                if (location == 18) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_MAGNETIC_FIELD;
                }
            } break;
            case EVO_MOSSY_ROCK: // mossy rock at ilex+viridian forests
            {
                u32 location = gFieldSysPtr->location->mapId;

                if (location == 117 || location == 147) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_MOSSY_ROCK;
                }
            } break;
            case EVO_ICY_ROCK: // icy rock at ice path+seafoam islands
            {
                u32 location = gFieldSysPtr->location->mapId;

                if (location == 239 || location == 456) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_ICY_ROCK;
                }
            } break;

            case EVO_LEVEL_DAY:
                if (IsNighttime() == 0 && evoTable[i].param <= level) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_LEVEL_DAY;
                }
                break;
            case EVO_LEVEL_NIGHT:
                if (IsNighttime() == 1 && evoTable[i].param <= level) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_LEVEL_NIGHT;
                }
                break;
            case EVO_LEVEL_DUSK: {
                struct RTCTime time;
                GF_RTC_CopyTime(&time);

                if (time.hour == 17 && evoTable[i].param <= level) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_LEVEL_DUSK;
                }
            } break;
            case EVO_LEVEL_RAIN:
                if (evoTable[i].param <= level) {
                    u32 weather = Fsys_GetWeather_HandleDiamondDust(gFieldSysPtr, gFieldSysPtr->location->mapId);

                    switch (weather) {
                    case WEATHER_SYS_RAIN:
                    case WEATHER_SYS_HEAVY_RAIN:
                    case WEATHER_SYS_THUNDER:
                        target = evoTable[i].target & 0x7FF;
                        *method_ret = EVO_LEVEL_RAIN;
                    }
                }
                break;
            case EVO_HAS_MOVE_TYPE: {
                int k;

                for (k = 0; k < 4; k++) {
                    if (GetMoveData(GetMonData(pokemon, MON_DATA_MOVE1 + k, NULL), MOVE_DATA_TYPE) == evoTable[i].param && friendship >= FRIENDSHIP_EVOLUTION_THRESHOLD) {
                        target = evoTable[i].target & 0x7FF;
                        *method_ret = EVO_HAS_MOVE_TYPE;
                        break;
                    }
                }
            } break;
            case EVO_LEVEL_DARK_TYPE_MON_IN_PARTY:
                if (evoTable[i].param <= level && party != NULL) {
                    for (int k = 0; k < 6; k++) {
                        if (!CheckIfMonsAreEqual(pokemon, Party_GetMonByIndex(party, k)) // make sure that pancham doesn't satisfy its own requirement
                            && (GetMonData(Party_GetMonByIndex(party, k), MON_DATA_TYPE_1, NULL) == TYPE_DARK || GetMonData(Party_GetMonByIndex(party, k), MON_DATA_TYPE_2, NULL) == TYPE_DARK)) // if either type is dark then set evolution
                        {
                            target = evoTable[i].target & 0x7FF;
                            *method_ret = EVO_LEVEL_DARK_TYPE_MON_IN_PARTY;
                            break;
                        }
                    }
                }
                break;
            case EVO_LEVEL_NATURE_LOW_KEY:
                lowkey = 1;
                FALLTHROUGH;
            case EVO_LEVEL_NATURE_AMPED:
                if (evoTable[i].param <= level) {
                    // toxel evolution disrespects nature mints
                    u32 nature = GetNatureFromPersonality(GetMonData(pokemon, MON_DATA_PERSONALITY, NULL));
                    switch (nature) {
                    case NATURE_ADAMANT:
                    case NATURE_BRAVE:
                    case NATURE_DOCILE:
                    case NATURE_HARDY:
                    case NATURE_HASTY:
                    case NATURE_IMPISH:
                    case NATURE_JOLLY:
                    case NATURE_LAX:
                    case NATURE_NAIVE:
                    case NATURE_NAUGHTY:
                    case NATURE_QUIRKY:
                    case NATURE_RASH:
                    case NATURE_SASSY:
                        if (lowkey == 0) // for the amped evo method
                        {
                            target = evoTable[i].target & 0x7FF;
                            *method_ret = EVO_LEVEL_NATURE_AMPED;
                        }
                        break;
                    default:
                        if (lowkey == 1) // for the lowkey evo method
                        {
                            target = evoTable[i].target & 0x7FF;
                            *method_ret = EVO_LEVEL_NATURE_LOW_KEY;
                        }
                        break;
                    }
                }
                break;
            case EVO_AMOUNT_OF_CRITICAL_HITS: // needs to hit an amount of critical hits in a battle in one go.  need to log critical hits somewhere else
                if (GET_MON_CRITICAL_HIT_EVOLUTION_BIT(pokemon)) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_AMOUNT_OF_CRITICAL_HITS;
                }
                break;
            case EVO_HURT_IN_BATTLE_AMOUNT: {
                u32 hp = GetMonData(pokemon, MON_DATA_HP, NULL), maxhp = GetMonData(pokemon, MON_DATA_MAXHP, NULL);

                if (hp && (maxhp - hp) >= evoTable[i].param) // if the mon has evoTable[i].param hp less than its max
                {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_HURT_IN_BATTLE_AMOUNT;
                }
            } break;
            }
            if (target != SPECIES_NONE) {
                break;
            }
        }
        break;
    case EVOCTX_TRADE:
        for (i = 0; i < evolutionCount; i++) {
            switch (evoTable[i].method) {
            case EVO_TRADE:
                target = evoTable[i].target & 0x7FF;
                *method_ret = EVO_TRADE;
                break;
            case EVO_TRADE_ITEM:
                if (heldItem == evoTable[i].param) {
                    target = evoTable[i].target & 0x7FF;
                    *method_ret = EVO_TRADE_ITEM;
                }
                break;
                // case EVO_TRADE_SPECIFIC_MON: // need to figure out how to deduce tradedSpecies
                //     if (tradedSpecies == evoTable[i].param) {
                //         target = evoTable[i].target & 0x7FF;
                //         *method_ret = EVO_TRADE_SPECIFIC_MON;
                //     }
                //     break;
            }
            if (target != SPECIES_NONE) {
                break;
            }
        }
        break;
    case EVOCTX_ITEM_CHECK:
    case EVOCTX_ITEM_USE:
        for (i = 0; i < evolutionCount; i++) {
            if (evoTable[i].method == EVO_STONE && usedItem == evoTable[i].param) {
                target = evoTable[i].target & 0x7FF;
                *method_ret = 0;
                break;
            }
            if (evoTable[i].method == EVO_STONE_MALE && GetMonData(pokemon, MON_DATA_GENDER, NULL) == POKEMON_GENDER_MALE && usedItem == evoTable[i].param) {
                target = evoTable[i].target & 0x7FF;
                *method_ret = 0;
                break;
            }
            if (evoTable[i].method == EVO_STONE_FEMALE && GetMonData(pokemon, MON_DATA_GENDER, NULL) == POKEMON_GENDER_FEMALE && usedItem == evoTable[i].param) {
                target = evoTable[i].target & 0x7FF;
                *method_ret = 0;
                break;
            }
            if (evoTable[i].method == EVO_TRADE_ITEM && usedItem == evoTable[i].param) {
                target = evoTable[i].target & 0x7FF;
                *method_ret = 0;
                break;
            }
            if (evoTable[i].method == EVO_TRADE_ITEM && heldItem == evoTable[i].param && usedItem == ITEM_LINKING_CORD) {
                target = evoTable[i].target & 0x7FF;
                *method_ret = 0;
                break;
            }
        }
        // Explicit item evolutions above take priority and retain their normal rules.
        if (target == SPECIES_NONE && !GetMonData(pokemon, MON_DATA_IS_EGG, NULL)) {
            for (i = 0; i < evolutionCount; i++) {
                u8 required = StoneLevelEvolutionRequirement(usedItem, &evoTable[i]);
                if (required != 0 && level >= required) {
                    target = evoTable[i].target & 0x07FF;
                    *method_ret = 0;
                    break;
                }
            }
        }
#if defined(IMPLEMENT_LEVEL_CAP) && defined(ALLOW_LEVEL_CAP_EVOLVE)
        if ((level == 100 || level == GetLevelCap()) && usedItem == ITEM_RARE_CANDY)
#else
        if (level == 100 && usedItem == ITEM_RARE_CANDY)
#endif
        {
            species = GetMonEvolutionInternal(party, pokemon, EVOCTX_LEVELUP, usedItem, NULL);
            if (species) {
                target = species;
                *method_ret = 0;
            }
        }
        break;
    }

    if (target) {
        u32 form = (evoTable[i].target & 0xF800) >> 11;

        if (form) {
            gEvolutionSceneOverride[0][0] = GetMonData(pokemon, MON_DATA_SPECIES, NULL);
            gEvolutionSceneOverride[0][1] = GetMonData(pokemon, MON_DATA_FORM, NULL);
            gEvolutionSceneOverride[1][0] = target;
            gEvolutionSceneOverride[1][1] = form;
        } else {
            memset(gEvolutionSceneOverride, 0, sizeof(gEvolutionSceneOverride));
        }
    }
    sys_FreeMemoryEz(evoTable);

    return target;
}

static u8 GetStoneLevelEvolutionRequirementInternal(struct PartyPokemon *mon, u16 item)
{
    struct {
        struct Evolution entries[MAX_EVOS_PER_POKE];
        u16 terminator;
    } table;
    u16 species;
    u32 form;
    int i;
    // Avoid NARC reads for unrelated item checks in the party menu.
    if (StoneLevelEvolutionItemType(item) == TYPE_NONE) {
        return 0;
    }
    if (GetMonData(mon, MON_DATA_IS_EGG, NULL)) {
        return 0;
    }
    species = GetMonData(mon, MON_DATA_SPECIES, NULL);
    form = GetMonData(mon, MON_DATA_FORM, NULL);
    species = PokeOtherFormMonsNoGet(species, form);
    ReadWholeNarcMemberByIdPair(&table, ARC_EVOLUTIONS, species);
    for (i = 0; i < MAX_EVOS_PER_POKE; i++) {
        u8 required = StoneLevelEvolutionRequirement(item, &table.entries[i]);
        if (required != 0) {
            return required;
        }
    }
    return 0;
}

static void PartyMenu_PrintEvoStoneCompatStringInternal(struct PartyMenu *partyMenu, u8 slot, u8 compatibility)
{
    struct Window *window = &partyMenu->windows[slot * 5 + PARTY_MENU_WINDOW_ID_MON1_COMPAT];
    struct PartyPokemon *mon = Party_GetMonByIndex(partyMenu->args->party, slot);
    String *string;
    u8 required = compatibility ? GetStoneLevelEvolutionRequirementInternal(mon, partyMenu->args->itemId) : 0;
    FillWindowPixelBuffer(window, 0);
    if (required != 0 && GetMonData(mon, MON_DATA_LEVEL, NULL) < required) {
        // HGSS character codes: L, V, then decimal digits and the terminator.
        u16 label[6] = { 0x0136, 0x0140, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF };
        u8 index = 2;
        if (required >= 10) {
            label[index++] = 0x0121 + required / 10;
        }
        label[index] = 0x0121 + required % 10;
        string = String_New(6, HEAP_ID_PARTY_MENU);
        CopyU16ArrayToString(string, label);
    } else {
        string = NewString_ReadMsgData(partyMenu->msgData, compatibility ? 162 : 161);
    }
    AddTextPrinterParameterizedWithColor(window, 0, string, 0, 0,
        TEXT_SPEED_NOTRANSFER, MAKE_TEXT_COLOR(15, 14, 0), NULL);
    String_Delete(string);
    ScheduleWindowCopyToVram(window);
}

const struct EvolutionOverlayApi gEvolutionOverlayApi __attribute__((section(".evolution_api"), used)) = {
    GetMonEvolutionInternal,
    GetStoneLevelEvolutionRequirementInternal,
    PartyMenu_PrintEvoStoneCompatStringInternal,
};
