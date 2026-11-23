#include "../include/config.h"
#include "../include/apricorn_craft.h"
#include "../include/apricorn_tree.h"
#include "../include/abra_travel.h"
#include "../include/game_clock.h"
#include "../include/constants/file.h"
#include "../include/constants/item.h"
#include "../include/ecology/ecology_script.h"
#include "../include/field_pickups.h"
#include "../include/fishing_rod.h"
#include "../include/pokedex.h"
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

BOOL Script_RunNewCmd(SCRIPTCONTEXT *ctx)
{
    u8 sw = ScriptReadByte(ctx);
    u16 UNUSED arg0 = ScriptReadHalfword(ctx);

    switch (sw) {
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
