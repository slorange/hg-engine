.nds
.thumb
.include "armips/include/scriptmacros.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

.equ RELEARN_COST, 300
.equ MSG_OFFER, 17
.equ MSG_NO_MONEY, 18
.equ MSG_CHOOSE, 19
.equ MSG_EGG, 20
.equ MSG_NO_MOVES, 21
.equ MSG_SUCCESS, 22
.equ MSG_CANCEL, 23
.equ MSG_PICK_MOVE, 24

.create "build/center_relearner.bin", 0
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    npc_msg MSG_OFFER
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _cancel
    hasenoughmoneyimmediate VAR_SPECIAL_RESULT, RELEARN_COST
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _no_money
    npc_msg MSG_CHOOSE
    closemsg
    fade_screen 6, 1, 0, RGB_BLACK
    wait_fade
    party_select_ui
    get_party_selection VAR_SPECIAL_x8005
    scrcmd_150 // RestoreOverworld
    fade_screen 6, 1, 1, RGB_BLACK
    wait_fade
    compare VAR_SPECIAL_x8005, 255
    goto_if_eq _cancel
    get_partymon_species VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0 // Eggs report species zero in this command.
    goto_if_eq _egg
    scrcmd_466 VAR_SPECIAL_RESULT, VAR_SPECIAL_x8005
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _no_moves
    // PartySelect removed the old message window. Recreate it before CloseMsg,
    // matching the original Blackthorn relearner's transition sequence.
    npc_msg MSG_PICK_MOVE
    closemsg
    fade_screen 6, 1, 0, RGB_BLACK
    wait_fade
    move_relearner_init VAR_SPECIAL_x8005
    move_relearner_get_result VAR_SPECIAL_RESULT
    scrcmd_150
    fade_screen 6, 1, 1, RGB_BLACK
    wait_fade
    compare VAR_SPECIAL_RESULT, 0
    goto_if_ne _cancel
    // The application returns zero only after actually teaching a move.
    submoneyimmediate RELEARN_COST
    play_se SEQ_SE_DP_REGI
    npc_msg MSG_SUCCESS
    goto _finish
_no_money:
    npc_msg MSG_NO_MONEY
    goto _finish
_egg:
    npc_msg MSG_EGG
    goto _finish
_no_moves:
    npc_msg MSG_NO_MOVES
    goto _finish
_cancel:
    npc_msg MSG_CANCEL
_finish:
    wait_button_or_walk_away
    closemsg
    releaseall
    end
.close
