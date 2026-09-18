.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

.equ MAP_T24, 75
.equ WARP_DOOR, 65535

// Landing west of the Cianwood fisherman on walkable sand; face west (left) after warp.
.equ LAND_X, 190
.equ LAND_Z, 360

.create "build/w40_ferry_cianwood.bin", 0
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    npc_msg 13
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _decline
    hasenoughmoneyimmediate VAR_SPECIAL_RESULT, 200
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _nomoney
    submoneyimmediate 200
    npc_msg 14
    closemsg
    fade_screen 6, 1, 0, RGB_BLACK
    wait_fade
    warp MAP_T24, WARP_DOOR, LAND_X, LAND_Z, DIR_WEST
    fade_screen 6, 1, 1, RGB_BLACK
    wait_fade
    releaseall
    end
_decline:
    npc_msg 15
    wait_button_or_walk_away
    closemsg
    releaseall
    end
_nomoney:
    npc_msg 16
    wait_button_or_walk_away
    closemsg
    releaseall
    end
.close
