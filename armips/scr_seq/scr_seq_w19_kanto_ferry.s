.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
.include "armips/scr_seq/kanto_waters_landings.s"

.equ MSG_OFFER, 6
.equ MSG_BOARDING, 7
.equ MSG_DEST_PROMPT, 8
.equ MSG_DEST_PALLET, 9
.equ MSG_DEST_CINNABAR, 10
.equ MSG_DEST_SEAFOAM, 11
.equ MSG_DECLINE, 12
.equ MSG_NOMONEY, 13

.create "build/kanto_ferry_w19.bin", 0
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    npc_msg MSG_OFFER
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _decline
    hasenoughmoneyimmediate VAR_SPECIAL_RESULT, FERRY_FEE
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _nomoney
    submoneyimmediate FERRY_FEE
    npc_msg MSG_BOARDING
    closemsg
    touchscreen_menu_hide
    npc_msg MSG_DEST_PROMPT
    ListLocalText 1, 1, 0, 0, VAR_SPECIAL_RESULT
    AddListOption MSG_DEST_PALLET, MSG_LIST_HIGHLIGHT, 0
    AddListOption MSG_DEST_CINNABAR, MSG_LIST_HIGHLIGHT, 1
    AddListOption MSG_DEST_SEAFOAM, MSG_LIST_HIGHLIGHT, 2
    ShowList
    closemsg
    touchscreen_menu_show
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _to_pallet
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _to_cinnabar
    goto _to_seafoam
_to_pallet:
    fade_screen 6, 1, 0, RGB_BLACK
    wait_fade
    warp MAP_T01, WARP_DOOR, LAND_PALLET_X, LAND_PALLET_Z, DIR_NORTH
    fade_screen 6, 1, 1, RGB_BLACK
    wait_fade
    releaseall
    end
_to_cinnabar:
    fade_screen 6, 1, 0, RGB_BLACK
    wait_fade
    warp MAP_T09, WARP_DOOR, LAND_CINNABAR_X, LAND_CINNABAR_Z, DIR_SOUTH
    fade_screen 6, 1, 1, RGB_BLACK
    wait_fade
    releaseall
    end
_to_seafoam:
    fade_screen 6, 1, 0, RGB_BLACK
    wait_fade
    warp MAP_W20, WARP_DOOR, LAND_SEAFOAM_X, LAND_SEAFOAM_Z, DIR_NORTH
    fade_screen 6, 1, 1, RGB_BLACK
    wait_fade
    releaseall
    end
_decline:
    npc_msg MSG_DECLINE
    wait_button_or_walk_away
    closemsg
    releaseall
    end
_nomoney:
    npc_msg MSG_NOMONEY
    wait_button_or_walk_away
    closemsg
    releaseall
    end
.close
