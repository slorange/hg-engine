#include "../include/config.h"
#include "../include/apricorn_craft.h"
#include "../include/apricorn_tree.h"
#include "../include/abra_travel.h"
#include "../include/game_clock.h"
#include "../include/constants/file.h"
#include "../include/constants/item.h"
#include "../include/constants/species.h"
#include "../include/ecology/ecology_script.h"
#include "../include/encounter_overlay.h"
#include "../include/field_pickups.h"
#include "../include/fishing_rod.h"
#include "../include/pokedex.h"
#include "../include/player_level_cap.h"
#include "../include/pokemon.h"
#include "../include/repel.h"
#include "../include/roamer.h"
#include "../include/save.h"
#include "../include/script.h"
#include "../include/types.h"

#define SCRIPT_NEW_CMD_REPEL_USE             0
#define SCRIPT_NEW_CMD_FISHING_ROD_COUNT     1
#define SCRIPT_NEW_CMD_FISHING_ROD_REMAINING 2
#define SCRIPT_NEW_CMD_GIVE_JOHTO_BADGE       3
#define SCRIPT_NEW_CMD_ECOLOGY_GENERATE       4
#define SCRIPT_NEW_CMD_APRICORN_CRAFT         5
#define SCRIPT_NEW_CMD_ABRA_TRAVEL            6
#define SCRIPT_NEW_CMD_CENTER_REST            7
#define SCRIPT_NEW_CMD_FIELD_PICKUP           8
#define SCRIPT_NEW_CMD_APRICORN_TREE          9
#define SCRIPT_NEW_CMD_UNOWN_RESEARCH       10
#define SCRIPT_NEW_CMD_GYM_POKEMON_HINT      11
#define SCRIPT_NEW_CMD_CLAIR_POKEMON_HINT    12
#define SCRIPT_NEW_CMD_BROCK_POKEMON_HINT    13
#define SCRIPT_NEW_CMD_FALKNER_POKEMON_HINT 14
#define SCRIPT_NEW_CMD_BUGSY_POKEMON_HINT 15
#define SCRIPT_NEW_CMD_WHITNEY_POKEMON_HINT 16
#define SCRIPT_NEW_CMD_MORTY_POKEMON_HINT 17
#define SCRIPT_NEW_CMD_PRYCE_POKEMON_HINT 18
#define SCRIPT_NEW_CMD_JASMINE_POKEMON_HINT 19
#define SCRIPT_NEW_CMD_CHUCK_POKEMON_HINT 20
#define SCRIPT_NEW_CMD_MISTY_POKEMON_HINT 21
#define SCRIPT_NEW_CMD_ERIKA_POKEMON_HINT 22
#define SCRIPT_NEW_CMD_JANINE_POKEMON_HINT 23
#define SCRIPT_NEW_CMD_SABRINA_POKEMON_HINT 24
#define SCRIPT_NEW_CMD_BLAINE_POKEMON_HINT 25
#define SCRIPT_NEW_CMD_MAX 256

extern BOOL LONG_CALL FieldSystem_ApricornTree_HasFruit(FieldSystem *, LocalMapObject *);
extern int LONG_CALL FieldSystem_ApricornTree_GetApricorn(FieldSystem *, LocalMapObject *);

static void CheckApricornHarvest(FieldSystem *field)
{
    LocalMapObject **tree = FieldSysGetAttrAddr(field, SCRIPTENV_LAST_TALKED);
    u16 *result = GetVarPointer(field, 0x800C);
    // 0 = empty, 1 = ready, 2 = Bag full. The animation marks the tree picked.
    *result = 0;
    if (tree == NULL || !FieldSystem_ApricornTree_HasFruit(field, *tree))
        return;

    int colour = FieldSystem_ApricornTree_GetApricorn(field, *tree);
    u16 item = ITEM_RED_APRICORN + colour;
    if (colour == APRICORN_TYPE_PURPLE - 1)
        item = ITEM_PURPLE_APRICORN;
    else if (colour == APRICORN_TYPE_GREY - 1)
        item = ITEM_GREY_APRICORN;
    *GetVarPointer(field, 0x8004) = item;
    u16 quantity = 3 + gf_rand() % 3;
    *GetVarPointer(field, 0x8005) = quantity;
    *result = Bag_HasSpaceForItem(Sav2_Bag_get(field->savedata), item, quantity, HEAPID_WORLD) ? 1 : 2;
}

static void FindGymPokemonHint(u16 species)
{
    struct EcologyHint hint;
    BOOL owned;
    const struct EncounterOverlayApi *api = EncounterOverlay_Open(&owned);
    SetScriptVar(0x800C, 0);
    if (api == NULL)
        return;
    BOOL found = api->findHint(species, &hint);
    EncounterOverlay_Close(owned);
    if (!found)
        return;

    u8 badges = 0;
    if (hint.level > GetLevelCap()) {
        while (badges < 16 && hint.level > GetPlayerLevelCapForBadges(badges))
            badges++;
        if (hint.level > GetPlayerLevelCapForBadges(badges))
            badges = 17; // Hall of Fame required.
    }
    SetScriptVar(0x8000, hint.mapId);
    SetScriptVar(0x8001, badges);
    SetScriptVar(0x800C, hint.method + 1);
}

// Order matches Surge's consecutive wild hint labels in message bank 485.
static const u16 sSurgeHintSpecies[] = {
    SPECIES_PIKACHU, SPECIES_MAGNEMITE, SPECIES_VOLTORB, SPECIES_ELECTABUZZ,
    SPECIES_CHINCHOU, SPECIES_MAREEP, SPECIES_ELECTRIKE, SPECIES_PLUSLE,
    SPECIES_MINUN, SPECIES_SHINX, SPECIES_PACHIRISU,
};

// Order matches the consecutive hint labels in Clair's message bank (631).
static const u16 sClairHintSpecies[] = {
    SPECIES_DRATINI, SPECIES_TRAPINCH, SPECIES_SWABLU, SPECIES_BAGON, SPECIES_GIBLE,
    SPECIES_TENTACOOL, SPECIES_HORSEA, SPECIES_MAGIKARP, SPECIES_LAPRAS,
    SPECIES_TOTODILE, SPECIES_FEEBAS,
};

// Order matches the consecutive hint labels in Brock's message bank (462).
static const u16 sBrockHintSpecies[] = {
    SPECIES_SANDSHREW, SPECIES_DIGLETT, SPECIES_GEODUDE, SPECIES_ONIX,
    SPECIES_CUBONE, SPECIES_RHYHORN, SPECIES_OMANYTE, SPECIES_KABUTO,
    SPECIES_AERODACTYL, SPECIES_SUDOWOODO, SPECIES_WOOPER, SPECIES_GLIGAR,
    SPECIES_SHUCKLE, SPECIES_SWINUB, SPECIES_CORSOLA, SPECIES_PHANPY,
    SPECIES_LARVITAR, SPECIES_NOSEPASS, SPECIES_ARON, SPECIES_NUMEL,
    SPECIES_TRAPINCH, SPECIES_LILEEP, SPECIES_ANORITH, SPECIES_CRANIDOS,
    SPECIES_SHIELDON, SPECIES_HIPPOPOTAS,
};

// Candidate order matches each Gym message bank.
static const u16 sFalknerHintSpecies[] = {
    SPECIES_PIDGEY, SPECIES_SPEAROW, SPECIES_ZUBAT, SPECIES_FARFETCHD,
    SPECIES_DODUO, SPECIES_SCYTHER, SPECIES_AERODACTYL, SPECIES_HOOTHOOT,
    SPECIES_LEDYBA, SPECIES_NATU, SPECIES_HOPPIP, SPECIES_YANMA,
    SPECIES_MURKROW, SPECIES_GLIGAR, SPECIES_DELIBIRD, SPECIES_MANTINE,
    SPECIES_SKARMORY, SPECIES_TAILLOW, SPECIES_WINGULL, SPECIES_SWABLU,
    SPECIES_TROPIUS, SPECIES_STARLY, SPECIES_COMBEE, SPECIES_DRIFLOON,
    SPECIES_CHATOT,
};

static const u16 sBugsyHintSpecies[] = {
    SPECIES_CATERPIE, SPECIES_WEEDLE, SPECIES_PARAS, SPECIES_VENONAT,
    SPECIES_SCYTHER, SPECIES_PINSIR, SPECIES_LEDYBA, SPECIES_SPINARAK,
    SPECIES_YANMA, SPECIES_PINECO, SPECIES_SHUCKLE, SPECIES_HERACROSS,
    SPECIES_WURMPLE, SPECIES_SURSKIT, SPECIES_NINCADA, SPECIES_VOLBEAT,
    SPECIES_ILLUMISE, SPECIES_ANORITH, SPECIES_KRICKETOT, SPECIES_BURMY,
    SPECIES_COMBEE, SPECIES_SKORUPI,
};

static const u16 sWhitneyHintSpecies[] = {
    SPECIES_PIDGEY, SPECIES_SPEAROW, SPECIES_MEOWTH, SPECIES_DODUO,
    SPECIES_KANGASKHAN, SPECIES_TAUROS, SPECIES_EEVEE, SPECIES_PORYGON,
    SPECIES_HOOTHOOT, SPECIES_TOGEPI, SPECIES_AIPOM, SPECIES_DUNSPARCE,
    SPECIES_TEDDIURSA, SPECIES_SMEARGLE, SPECIES_MILTANK, SPECIES_RALTS,
    SPECIES_WHISMUR, SPECIES_SPINDA, SPECIES_SWABLU, SPECIES_CASTFORM,
    SPECIES_KECLEON, SPECIES_STARLY, SPECIES_GLAMEOW, SPECIES_CHATOT,
    SPECIES_MUNCHLAX,
};

static const u16 sMortyHintSpecies[] = {
    SPECIES_GASTLY, SPECIES_MURKROW, SPECIES_MISDREAVUS, SPECIES_SNEASEL,
    SPECIES_HOUNDOUR, SPECIES_POOCHYENA, SPECIES_SABLEYE, SPECIES_CARVANHA,
    SPECIES_SHUPPET, SPECIES_DUSKULL, SPECIES_ABSOL, SPECIES_DRIFLOON,
    SPECIES_STUNKY, SPECIES_SPIRITOMB,
};

static const u16 sPryceHintSpecies[] = {
    SPECIES_JYNX, SPECIES_LAPRAS, SPECIES_SNEASEL, SPECIES_SWINUB,
    SPECIES_DELIBIRD, SPECIES_SNORUNT, SPECIES_SPHEAL, SPECIES_SNOVER,
};

static const u16 sJasmineHintSpecies[] = {
    SPECIES_MAGNEMITE, SPECIES_SKARMORY, SPECIES_MAWILE, SPECIES_ARON,
    SPECIES_BELDUM, SPECIES_SHIELDON, SPECIES_BRONZOR,
};

static const u16 sChuckHintSpecies[] = {
    SPECIES_MANKEY, SPECIES_MACHOP, SPECIES_HERACROSS, SPECIES_TYROGUE,
    SPECIES_MAKUHITA, SPECIES_MEDITITE, SPECIES_RIOLU, SPECIES_CROAGUNK,
};

static const u16 sMistyHintSpecies[] = {
    SPECIES_SQUIRTLE, SPECIES_PSYDUCK, SPECIES_POLIWAG, SPECIES_SLOWPOKE,
    SPECIES_SHELLDER, SPECIES_HORSEA, SPECIES_STARYU, SPECIES_LAPRAS,
    SPECIES_OMANYTE, SPECIES_KABUTO, SPECIES_TOTODILE, SPECIES_CHINCHOU,
    SPECIES_WOOPER, SPECIES_CORSOLA, SPECIES_REMORAID, SPECIES_MUDKIP,
    SPECIES_LOTAD, SPECIES_SURSKIT, SPECIES_WAILMER, SPECIES_CORPHISH,
    SPECIES_SPHEAL, SPECIES_RELICANTH, SPECIES_PIPLUP, SPECIES_BUIZEL,
    SPECIES_FINNEON,
};

static const u16 sErikaHintSpecies[] = {
    SPECIES_BULBASAUR, SPECIES_ODDISH, SPECIES_PARAS, SPECIES_BELLSPROUT,
    SPECIES_EXEGGCUTE, SPECIES_TANGELA, SPECIES_CHIKORITA, SPECIES_HOPPIP,
    SPECIES_SUNKERN, SPECIES_TREECKO, SPECIES_LOTAD, SPECIES_SEEDOT,
    SPECIES_SHROOMISH, SPECIES_ROSELIA, SPECIES_CACNEA, SPECIES_LILEEP,
    SPECIES_TROPIUS, SPECIES_TURTWIG, SPECIES_CHERUBI, SPECIES_CARNIVINE,
    SPECIES_SNOVER,
};

static const u16 sJanineHintSpecies[] = {
    SPECIES_BULBASAUR, SPECIES_WEEDLE, SPECIES_EKANS, SPECIES_NIDORAN_F,
    SPECIES_NIDORAN_M, SPECIES_ZUBAT, SPECIES_ODDISH, SPECIES_VENONAT,
    SPECIES_BELLSPROUT, SPECIES_TENTACOOL, SPECIES_GRIMER, SPECIES_GASTLY,
    SPECIES_KOFFING, SPECIES_SPINARAK, SPECIES_QWILFISH, SPECIES_ROSELIA,
    SPECIES_GULPIN, SPECIES_SEVIPER, SPECIES_STUNKY, SPECIES_SKORUPI,
    SPECIES_CROAGUNK,
};

static const u16 sSabrinaHintSpecies[] = {
    SPECIES_ABRA, SPECIES_SLOWPOKE, SPECIES_DROWZEE, SPECIES_EXEGGCUTE,
    SPECIES_MR_MIME, SPECIES_JYNX, SPECIES_NATU, SPECIES_UNOWN,
    SPECIES_WOBBUFFET, SPECIES_GIRAFARIG, SPECIES_RALTS, SPECIES_MEDITITE,
    SPECIES_SPOINK, SPECIES_LUNATONE, SPECIES_SOLROCK, SPECIES_BALTOY,
    SPECIES_CHIMECHO, SPECIES_WYNAUT, SPECIES_BELDUM, SPECIES_BRONZOR,
};

static const u16 sBlaineHintSpecies[] = {
    SPECIES_CHARMANDER, SPECIES_VULPIX, SPECIES_GROWLITHE, SPECIES_PONYTA,
    SPECIES_MAGMAR, SPECIES_CYNDAQUIL, SPECIES_SLUGMA, SPECIES_HOUNDOUR,
    SPECIES_TORCHIC, SPECIES_NUMEL, SPECIES_TORKOAL, SPECIES_CHIMCHAR,
};

static u16 GymHintResearchSource(u16 species)
{
    switch (species) {
    case SPECIES_KECLEON:
    case SPECIES_DELIBIRD:
    case SPECIES_SPINDA:
    case SPECIES_CHATOT:
    case SPECIES_DUNSPARCE:
    case SPECIES_WYNAUT:
    case SPECIES_TYROGUE:
    case SPECIES_TOGEPI:
    case SPECIES_RIOLU:
    case SPECIES_EEVEE:
    case SPECIES_LAPRAS:
    case SPECIES_MUNCHLAX:
    case SPECIES_SPIRITOMB:
    case SPECIES_BULBASAUR:
    case SPECIES_CHARMANDER:
    case SPECIES_SQUIRTLE:
    case SPECIES_CHIKORITA:
    case SPECIES_CYNDAQUIL:
    case SPECIES_TOTODILE:
    case SPECIES_TREECKO:
    case SPECIES_TORCHIC:
    case SPECIES_MUDKIP:
    case SPECIES_TURTWIG:
    case SPECIES_CHIMCHAR:
    case SPECIES_PIPLUP:
        return 8;
    case SPECIES_OMANYTE:
        return ITEM_HELIX_FOSSIL;
    case SPECIES_KABUTO:
        return ITEM_DOME_FOSSIL;
    case SPECIES_AERODACTYL:
        return ITEM_OLD_AMBER;
    case SPECIES_LILEEP:
        return ITEM_ROOT_FOSSIL;
    case SPECIES_ANORITH:
        return ITEM_CLAW_FOSSIL;
    case SPECIES_CRANIDOS:
        return ITEM_SKULL_FOSSIL;
    case SPECIES_SHIELDON:
        return ITEM_ARMOR_FOSSIL;
    default:
        return 0;
    }
}

static void FindGymHintForChoice(u16 choice, const u16 *speciesList, u16 count)
{
    if (choice >= count) {
        SetScriptVar(0x800C, 0);
        return;
    }
    u16 species = speciesList[choice];
    SetScriptVar(0x8005, species);
    u16 research = GymHintResearchSource(species);
    if (research) {
        SetScriptVar(0x800C, research == 8 ? 8 : 9);
        SetScriptVar(0x8000, research);
        return;
    }
    switch (species) {
    case SPECIES_SMEARGLE:
    case SPECIES_WOBBUFFET:
        SetScriptVar(0x800C, 10); // Goldenrod Game Corner.
        return;
    case SPECIES_PORYGON:
    case SPECIES_CASTFORM:
        SetScriptVar(0x800C, 11); // Celadon Game Corner.
        return;
    }
    FindGymPokemonHint(species);
}

BOOL Script_RunNewCmd(SCRIPTCONTEXT *ctx)
{
    u8 sw = ScriptReadByte(ctx);
    u16 UNUSED arg0 = ScriptReadHalfword(ctx);

    switch (sw) {
    case SCRIPT_NEW_CMD_GYM_POKEMON_HINT:
        FindGymHintForChoice(VarGet(ctx->fsys, arg0), sSurgeHintSpecies, NELEMS(sSurgeHintSpecies));
        break;
    case SCRIPT_NEW_CMD_CLAIR_POKEMON_HINT:
        FindGymHintForChoice(VarGet(ctx->fsys, arg0), sClairHintSpecies, NELEMS(sClairHintSpecies));
        break;
    case SCRIPT_NEW_CMD_BROCK_POKEMON_HINT:
        FindGymHintForChoice(VarGet(ctx->fsys, arg0), sBrockHintSpecies, NELEMS(sBrockHintSpecies));
        break;
    case SCRIPT_NEW_CMD_FALKNER_POKEMON_HINT:
        FindGymHintForChoice(VarGet(ctx->fsys, arg0), sFalknerHintSpecies, NELEMS(sFalknerHintSpecies));
        break;
    case SCRIPT_NEW_CMD_BUGSY_POKEMON_HINT:
        FindGymHintForChoice(VarGet(ctx->fsys, arg0), sBugsyHintSpecies, NELEMS(sBugsyHintSpecies));
        break;
    case SCRIPT_NEW_CMD_WHITNEY_POKEMON_HINT:
        FindGymHintForChoice(VarGet(ctx->fsys, arg0), sWhitneyHintSpecies, NELEMS(sWhitneyHintSpecies));
        break;
    case SCRIPT_NEW_CMD_MORTY_POKEMON_HINT:
        FindGymHintForChoice(VarGet(ctx->fsys, arg0), sMortyHintSpecies, NELEMS(sMortyHintSpecies));
        break;
    case SCRIPT_NEW_CMD_PRYCE_POKEMON_HINT:
        FindGymHintForChoice(VarGet(ctx->fsys, arg0), sPryceHintSpecies, NELEMS(sPryceHintSpecies));
        break;
    case SCRIPT_NEW_CMD_JASMINE_POKEMON_HINT:
        FindGymHintForChoice(VarGet(ctx->fsys, arg0), sJasmineHintSpecies, NELEMS(sJasmineHintSpecies));
        break;
    case SCRIPT_NEW_CMD_CHUCK_POKEMON_HINT:
        FindGymHintForChoice(VarGet(ctx->fsys, arg0), sChuckHintSpecies, NELEMS(sChuckHintSpecies));
        break;
    case SCRIPT_NEW_CMD_MISTY_POKEMON_HINT:
        FindGymHintForChoice(VarGet(ctx->fsys, arg0), sMistyHintSpecies, NELEMS(sMistyHintSpecies));
        break;
    case SCRIPT_NEW_CMD_ERIKA_POKEMON_HINT:
        FindGymHintForChoice(VarGet(ctx->fsys, arg0), sErikaHintSpecies, NELEMS(sErikaHintSpecies));
        break;
    case SCRIPT_NEW_CMD_JANINE_POKEMON_HINT:
        FindGymHintForChoice(VarGet(ctx->fsys, arg0), sJanineHintSpecies, NELEMS(sJanineHintSpecies));
        break;
    case SCRIPT_NEW_CMD_SABRINA_POKEMON_HINT:
        FindGymHintForChoice(VarGet(ctx->fsys, arg0), sSabrinaHintSpecies, NELEMS(sSabrinaHintSpecies));
        break;
    case SCRIPT_NEW_CMD_BLAINE_POKEMON_HINT:
        FindGymHintForChoice(VarGet(ctx->fsys, arg0), sBlaineHintSpecies, NELEMS(sBlaineHintSpecies));
        break;
    case SCRIPT_NEW_CMD_UNOWN_RESEARCH: {
        void *save = ctx->fsys->savedata;
        u8 count = Pokedex_CountCaughtUnown(SaveData_GetDexPtr(save));
        u16 result = count;
        if (arg0 != 0) {
            result = count == 28 && Bag_AddItem(Sav2_Bag_get(save), ITEM_TM010, 1, HEAPID_WORLD);
        }
        SetScriptVar(0x800C, result);
        break;
    }
    case SCRIPT_NEW_CMD_APRICORN_TREE:
        CheckApricornHarvest(ctx->fsys);
        break;
    case SCRIPT_NEW_CMD_FIELD_PICKUP:
        FieldPickup_Run(ctx, arg0);
        break;
    case SCRIPT_NEW_CMD_CENTER_REST:
#ifdef IMPLEMENT_ACCELERATED_GAME_CLOCK
        SetScriptVar(0x800C, GameClock_RestUntilHour(GetScriptVar(arg0)));
#else
        SetScriptVar(0x800C, FALSE);
#endif
        break;
    case SCRIPT_NEW_CMD_ABRA_TRAVEL:
        return AbraTravel_Command(ctx, arg0);
    case SCRIPT_NEW_CMD_APRICORN_CRAFT: {
        u16 total, feeHundreds;
        u16 status = ApricornCraft_Run(ctx->fsys->savedata, arg0 != 0, &total, &feeHundreds);
        SetScriptVar(0x8000, total);
        SetScriptVar(0x8001, feeHundreds);
        SetScriptVar(0x800C, status);
        break;
    }
    case SCRIPT_NEW_CMD_REPEL_USE:;
#ifdef IMPLEMENT_REUSABLE_REPELS
        u16 most_recent_repel = Repel_GetMostRecent();
        SetScriptVar(arg0, most_recent_repel);
        Repel_Use(most_recent_repel, HEAPID_MAIN_HEAP);
#endif
        break;

    case SCRIPT_NEW_CMD_FISHING_ROD_COUNT:
        SetScriptVar(arg0, CountCaughtWaterTypeFamilies(ctx->fsys->savedata));
        break;

    case SCRIPT_NEW_CMD_FISHING_ROD_REMAINING:
        SetScriptVar(arg0, FishingRod_RemainingForNextTier(ctx->fsys->savedata));
        break;

    case SCRIPT_NEW_CMD_GIVE_JOHTO_BADGE: {
        u16 badgeId = arg0;
        struct PlayerProfile *profile = Sav2_PlayerData_GetProfileAddr(ctx->fsys->savedata);

        if (badgeId < 8) {
            profile->johtoBadges |= (u8)(1u << badgeId);
        } else if (badgeId < 16) {
            profile->kantoBadges |= (u8)(1u << (badgeId - 8));
        }
        break;
    }

#ifdef IMPLEMENT_ECOLOGY_GENERATION
    case SCRIPT_NEW_CMD_ECOLOGY_GENERATE:
        EcologyRunNewGameGeneration(ctx->fsys->savedata);
        break;
#endif

    default:
        break;
    }

    return FALSE;
}

#ifdef EXPAND_ROAMERS
BOOL LONG_CALL ScrCmd_CreateRoamer(SCRIPTCONTEXT *ctx)
{
    u8 roamerNo = ScriptReadByte(ctx);
    Save_CreateRoamerByID(ctx->fsys->savedata, roamerNo);
    return FALSE;
}
#endif // EXPAND_ROAMERS
