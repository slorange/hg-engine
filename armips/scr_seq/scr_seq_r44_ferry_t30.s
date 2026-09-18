.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

.equ MAP_T30, 89
.equ WARP_DOOR, 65535

// Landing west of the Blackthorn Ice Path hiker; face south after warp.
.equ LAND_X, 691
.equ LAND_Z, 166

.create "build/r44_ferry_t30.bin", 0
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    npc_msg 7
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _decline
    hasenoughmoneyimmediate VAR_SPECIAL_RESULT, 200
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _nomoney
    submoneyimmediate 200
    npc_msg 8
    closemsg
    fade_screen 6, 1, 0, RGB_BLACK
    wait_fade
    warp MAP_T30, WARP_DOOR, LAND_X, LAND_Z, DIR_SOUTH
    fade_screen 6, 1, 1, RGB_BLACK
    wait_fade
    releaseall
    end
_decline:
    npc_msg 9
    wait_button_or_walk_away
    closemsg
    releaseall
    end
_nomoney:
    npc_msg 10
    wait_button_or_walk_away
    closemsg
    releaseall
    end
.close
