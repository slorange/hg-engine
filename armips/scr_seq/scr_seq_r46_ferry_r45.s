.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

.equ MAP_R45, 47
.equ WARP_DOOR, 65535

// Landing on north Route 45; face north after warp.
.equ LAND_X, 663
.equ LAND_Z, 199

.create "build/r46_ferry_r45.bin", 0
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    npc_msg 4
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _decline
    hasenoughmoneyimmediate VAR_SPECIAL_RESULT, 200
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _nomoney
    submoneyimmediate 200
    npc_msg 5
    closemsg
    fade_screen 6, 1, 0, RGB_BLACK
    wait_fade
    warp MAP_R45, WARP_DOOR, LAND_X, LAND_Z, DIR_NORTH
    fade_screen 6, 1, 1, RGB_BLACK
    wait_fade
    releaseall
    end
_decline:
    npc_msg 6
    wait_button_or_walk_away
    closemsg
    releaseall
    end
_nomoney:
    npc_msg 7
    wait_button_or_walk_away
    closemsg
    releaseall
    end
.close
