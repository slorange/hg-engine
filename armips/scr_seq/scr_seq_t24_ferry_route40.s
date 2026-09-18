.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

.equ MAP_W40, 94
.equ WARP_DOOR, 65535

// Landing east of the Route 40 fisherman on walkable sand; face north after warp.
.equ LAND_X, 249
.equ LAND_Z, 277

.create "build/t24_ferry_route40.bin", 0
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    npc_msg 22
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _decline
    hasenoughmoneyimmediate VAR_SPECIAL_RESULT, 200
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _nomoney
    submoneyimmediate 200
    npc_msg 23
    closemsg
    fade_screen 6, 1, 0, RGB_BLACK
    wait_fade
    warp MAP_W40, WARP_DOOR, LAND_X, LAND_Z, DIR_NORTH
    fade_screen 6, 1, 1, RGB_BLACK
    wait_fade
    releaseall
    end
_decline:
    npc_msg 24
    wait_button_or_walk_away
    closemsg
    releaseall
    end
_nomoney:
    npc_msg 25
    wait_button_or_walk_away
    closemsg
    releaseall
    end
.close
