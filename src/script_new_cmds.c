#include "../include/config.h"
#include "../include/apricorn_craft.h"
#include "../include/abra_travel.h"
#include "../include/game_clock.h"
#include "../include/constants/file.h"
#include "../include/ecology/ecology_script.h"
#include "../include/field_pickups.h"
#include "../include/fishing_rod.h"
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
#define SCRIPT_NEW_CMD_MAX 256

BOOL Script_RunNewCmd(SCRIPTCONTEXT *ctx)
{
    u8 sw = ScriptReadByte(ctx);
    u16 UNUSED arg0 = ScriptReadHalfword(ctx);

    switch (sw) {
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
