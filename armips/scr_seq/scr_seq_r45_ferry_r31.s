.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

.equ MAP_R31, 35
.equ WARP_DOOR, 65535

// Landing south of the Route 31 Dark Cave entrance; face south after warp.
.equ LAND_X, 565
.equ LAND_Z, 270

.create "build/r45_ferry_r31.bin", 0
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    npc_msg 3
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _decline
    hasenoughmoneyimmediate VAR_SPECIAL_RESULT, 200
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _nomoney
    submoneyimmediate 200
    npc_msg 4
    closemsg
    fade_screen 6, 1, 0, RGB_BLACK
    wait_fade
    warp MAP_R31, WARP_DOOR, LAND_X, LAND_Z, DIR_SOUTH
    fade_screen 6, 1, 1, RGB_BLACK
    wait_fade
    releaseall
    end
_decline:
    npc_msg 5
    wait_button_or_walk_away
    closemsg
    releaseall
    end
_nomoney:
    npc_msg 6
    wait_button_or_walk_away
    closemsg
    releaseall
    end
.close
