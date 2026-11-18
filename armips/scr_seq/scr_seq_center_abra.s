.nds
.thumb
.include "armips/include/scriptmacros.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

.equ ABRA_TRAVEL_FARE, 400
.create "build/center_abra.bin", 0
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    npc_msg 32
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _cancel
    hasenoughmoneyimmediate VAR_SPECIAL_RESULT, ABRA_TRAVEL_FARE
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _money
    closemsg
    fade_screen 6, 1, 0, RGB_BLACK
    wait_fade
    RunNewCommand 6, 0 // Native Fly picker; wait for application exit.
    RunNewCommand 6, 1 // Read and free map args before restoring the field.
    scrcmd_150
    fade_screen 6, 1, 1, RGB_BLACK
    wait_fade
    compare VAR_SPECIAL_RESULT, 1
    goto_if_ne _cancel
    npc_msg 35
    closemsg
    RunNewCommand 6, 2 // Charge only on valid selection; real Teleport task.
    compare VAR_SPECIAL_RESULT, 2
    goto_if_eq _money
    compare VAR_SPECIAL_RESULT, 1
    goto_if_ne _unavailable
    releaseall
    end
_money:
    npc_msg 33
    goto _finish
_cancel:
    npc_msg 34
    goto _finish
_unavailable:
    npc_msg 36
_finish:
    wait_button_or_walk_away
    closemsg
    releaseall
    end
.close

.create "build/center_abra_mon.bin", 0
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    play_cry 63, 0
    npc_msg 37
    wait_cry
    wait_button_or_walk_away
    closemsg
    releaseall
    end
.close
