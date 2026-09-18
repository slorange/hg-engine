.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

.equ MAP_R44, 46
.equ WARP_DOOR, 65535

// Landing east of the Route 44 bridge hiker; face south after warp.
.equ LAND_X, 626
.equ LAND_Z, 171

.create "build/t30_ferry_r44.bin", 0
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    npc_msg 15
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _decline
    hasenoughmoneyimmediate VAR_SPECIAL_RESULT, 200
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _nomoney
    submoneyimmediate 200
    npc_msg 16
    closemsg
    fade_screen 6, 1, 0, RGB_BLACK
    wait_fade
    warp MAP_R44, WARP_DOOR, LAND_X, LAND_Z, DIR_SOUTH
    fade_screen 6, 1, 1, RGB_BLACK
    wait_fade
    releaseall
    end
_decline:
    npc_msg 17
    wait_button_or_walk_away
    closemsg
    releaseall
    end
_nomoney:
    npc_msg 18
    wait_button_or_walk_away
    closemsg
    releaseall
    end
.close
