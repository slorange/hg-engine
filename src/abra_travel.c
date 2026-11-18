#include "abra_travel.h"
#include "center_hub.h"
#include "local_field_data.h"
#include "map_events_internal.h"
#include "task.h"

// Resolve exactly the same outdoor location used by Fly, and independently
// recheck the saved visit flag before accepting the GUI's destination.
BOOL AbraTravel_Resolve(const u16 *spawns, SCRIPT_STATE *flags, unsigned map,
                        Location *destination, Location *special)
{
    unsigned i;
    for (i = 0; i < 30; i++, spawns += 9) {
        if (spawns[3] != map || !(spawns[0] & 0x200)
            || !CheckScriptFlagPassSave(flags, 0x9B0 + (spawns[0] & 0xFF)))
            continue;
        *destination = (Location){spawns[3], -1, spawns[4], spawns[5], 1};
        *special = (Location){spawns[6], -1, spawns[7], spawns[8], 1};
        return TRUE;
    }
    return FALSE;
}

#ifndef ABRA_TRAVEL_HOST_TEST
typedef struct AbraMapArgs {
    u8 scripted, input;
    u16 music;
    u8 caller, scriptedCall, callScript, gender;
    int x, z;
    u16 mapId, mapHeader;
    BOOL selected;
    int cursorX, cursorY;
    u16 destination;
    u8 matrixX, matrixY;
    void *saveData, *inputState;
} AbraMapArgs;
typedef char AbraMapArgsSizeCheck[sizeof(AbraMapArgs) == 0x2C ? 1 : -1];

// First 0x30 bytes are the native Teleport environment. Reuse the actual
// departure effects, then hand off to the native Teleport arrival task.
typedef struct AbraTeleportEnv {
    u32 native[12];
    Location destination;
} AbraTeleportEnv;

extern AbraMapArgs *LONG_CALL AbraTravel_OpenFlyMap(FieldSystem *, int kind);
extern void LONG_CALL AbraTravel_SetNative(SCRIPTCONTEXT *, BOOL (*)(SCRIPTCONTEXT *));
extern BOOL LONG_CALL FieldSystem_ApplicationIsRunning(FieldSystem *);
extern void *LONG_CALL AbraTravel_TaskEnv(TaskManager *);
extern FieldSystem *LONG_CALL AbraTravel_TaskField(TaskManager *);
extern void LONG_CALL AbraTravel_HideFollower(FieldSystem *);
extern int LONG_CALL AbraTravel_TeleportStart(TaskManager *, FieldSystem *, void *);
extern int LONG_CALL AbraTravel_TeleportSpin(TaskManager *, FieldSystem *, void *);
extern int LONG_CALL AbraTravel_TeleportFade(TaskManager *, FieldSystem *, void *);
extern void LONG_CALL AbraTravel_TeleportArrive(TaskManager *, Location *, int kind);
extern LocalFieldData *LONG_CALL CenterHub_SaveLocalGet(void *);
extern void LONG_CALL PlaySE(u16 sound);
extern BOOL LONG_CALL AbraTravel_IsSEPlaying(u16 sound);

static Location sDestination, sSpecial;
static BOOL sHasDestination;

static BOOL AbraTravel_WaitMap(SCRIPTCONTEXT *ctx)
{
    return !FieldSystem_ApplicationIsRunning(ctx->fsys);
}

static BOOL AbraTravel_TeleportTask(TaskManager *task)
{
    AbraTeleportEnv *env = AbraTravel_TaskEnv(task);
    FieldSystem *field = AbraTravel_TaskField(task);
    // Start at native step 2 to omit the party Pokémon cut-in. The nearby
    // static Abra supplies the service; no party Pokémon or badge is required.
    switch (env->native[0]) {
    case 1:
        // Both effects use the SE player: let the purchase finish before
        // native Teleport starts its own sound (SEQ_SE_DP_TELE).
        if (!AbraTravel_IsSEPlaying(1603)) {
            AbraTravel_HideFollower(field);
            env->native[0] = 2;
        }
        break;
    case 2:
        AbraTravel_TeleportStart(task, field, env->native);
        break;
    case 3:
        AbraTravel_TeleportSpin(task, field, env->native);
        break;
    case 4:
        AbraTravel_TeleportFade(task, field, env->native);
        break;
    default:
        // This copies the destination and replaces this task's environment.
        AbraTravel_TeleportArrive(task, &env->destination, 2);
        sys_FreeMemoryEz(env);
        break;
    }
    return FALSE;
}

BOOL AbraTravel_Command(SCRIPTCONTEXT *ctx, unsigned mode)
{
    FieldSystem *field = ctx->fsys;
    AbraMapArgs **app = FieldSysGetAttrAddr(field, 20); // Running application args.
    struct PlayerProfile *profile = Sav2_PlayerData_GetProfileAddr(field->savedata);
    unsigned status = 0; // 0 cancelled/invalid, 1 ready/success, 2 no money, 3 unavailable.

    if (mode == 0) {
        LocalFieldData *local = CenterHub_SaveLocalGet(field->savedata);
        struct SAVE_MISC_DATA *misc = Sav2_Misc_get(field->savedata);
        const CenterHubDoor *door = &gCenterHubDoors[CenterHub_GetOrigin(misc->centerHubOrigin) - 1];
        sHasDestination = FALSE;
        *app = AbraTravel_OpenFlyMap(field, 0);
        // Keep the player marker/cursor at the originating Center's outdoor
        // position. Native region checks use x/z separately: the neutral
        // Indigo region allows Johto<->Kanto in this picker only, without
        // changing visit flags, ordinary Fly, or Indigo's actual map.
        (*app)->mapId = (*app)->mapHeader = door->exterior;
        (*app)->matrixX = local->specialSpawn.x / 32;
        (*app)->matrixY = local->specialSpawn.z / 32;
        (*app)->x = 28 * 32;
        (*app)->z = 6 * 32;
        AbraTravel_SetNative(ctx, AbraTravel_WaitMap);
        return TRUE;
    }
    if (mode == 1) {
        if (*app != NULL) {
            sHasDestination = (*app)->selected && AbraTravel_Resolve(
                (const u16 *)0x020F9E80, SavArray_Flags_get(field->savedata),
                (*app)->destination, &sDestination, &sSpecial);
            sys_FreeMemoryEz(*app);
            *app = NULL;
        }
        status = sHasDestination ? 1 : 0;
    } else if (mode == 2 && sHasDestination) {
        Location destination, special;
        if (!AbraTravel_Resolve((const u16 *)0x020F9E80,
                SavArray_Flags_get(field->savedata), sDestination.mapId, &destination, &special)) {
            status = 0;
        } else if (profile->money < ABRA_TRAVEL_FARE) {
            status = 2;
        } else {
            AbraTeleportEnv *env = sys_AllocMemory(4, sizeof(*env));
            if (env == NULL) {
                status = 3;
            } else {
                LocalFieldData *local = CenterHub_SaveLocalGet(field->savedata);
                memset(env, 0, sizeof(*env));
                env->native[0] = 1; // Payment sound, then native departure step 2.
                env->native[3] = 2;
                env->native[8] = (u32)field->playerAvatar->mapObject;
                env->native[9] = (u32)field;
                env->destination = destination;
                local->specialSpawn = special;
                profile->money -= ABRA_TRAVEL_FARE;
                sHasDestination = FALSE;
                SetScriptVar(0x800C, 1);
                PlaySE(1603); // Standard purchase sound.
                TaskManager_Call(ctx->taskman, AbraTravel_TeleportTask, env);
                return TRUE;
            }
        }
        sHasDestination = FALSE;
    }
    SetScriptVar(0x800C, status);
    return FALSE;
}
#endif
