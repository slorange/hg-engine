.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
.include "armips/scr_seq/kanto_waters_landings.s"

.equ MSG_OFFER, 22
.equ MSG_BOARDING, 23
.equ MSG_DEST_PROMPT, 24
.equ MSG_DEST_PALLET, 25
.equ MSG_DEST_CINNABAR, 26
.equ MSG_DEST_SEAFOAM, 27
.equ MSG_DEST_FUCHSIA, 28
.equ MSG_DECLINE, 29
.equ MSG_NOMONEY, 30

.create "build/kanto_ferry_t09_cinnabar.bin", 0
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
    AddListOption MSG_DEST_SEAFOAM, MSG_LIST_HIGHLIGHT, 1
    AddListOption MSG_DEST_FUCHSIA, MSG_LIST_HIGHLIGHT, 2
    ShowList
    closemsg
    touchscreen_menu_show
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _to_pallet
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _to_seafoam
    goto _to_fuchsia
_to_pallet:
    fade_screen 6, 1, 0, RGB_BLACK
    wait_fade
    warp MAP_T01, WARP_DOOR, LAND_PALLET_X, LAND_PALLET_Z, DIR_NORTH
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
_to_fuchsia:
    fade_screen 6, 1, 0, RGB_BLACK
    wait_fade
    warp MAP_W19, WARP_DOOR, LAND_FUCHSIA_X, LAND_FUCHSIA_Z, DIR_NORTH
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
