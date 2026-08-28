.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

// MAP_R04 = 12 in include/constants/maps.h
.equ MAP_R04, 12
.equ WARP_DOOR, 65535

// Landing tile: 2 steps north (up) from NPC — keep in sync with patch_zone_event_r04_boost.py.
.equ LAND_X, 1270
.equ LAND_Z, 116

.create "build/r04_boost.bin", 0
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    npc_msg 1
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _decline
    hasenoughmoneyimmediate VAR_SPECIAL_RESULT, 100
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _nomoney
    submoneyimmediate 100
    npc_msg 2
    closemsg
    fade_screen 6, 1, 0, RGB_BLACK
    wait_fade
    warp MAP_R04, WARP_DOOR, LAND_X, LAND_Z, DIR_NORTH
    fade_screen 6, 1, 1, RGB_BLACK
    wait_fade
    releaseall
    end
_decline:
    npc_msg 3
    wait_button_or_walk_away
    closemsg
    releaseall
    end
_nomoney:
    npc_msg 4
    wait_button_or_walk_away
    closemsg
    releaseall
    end
.close
