.nds
.thumb
.include "armips/include/scriptmacros.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

.create "build/center_apricorn.bin", 0
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    RunNewCommand 5, 0 // Quote all Apricorns; do not mutate inventory.
    TextNumber 0, VAR_SPECIAL_x8000
    TextNumber 1, VAR_SPECIAL_x8001
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _empty
    compare VAR_SPECIAL_RESULT, 2
    goto_if_eq _money
    compare VAR_SPECIAL_RESULT, 3
    goto_if_eq _space
    compare VAR_SPECIAL_RESULT, 4
    goto_if_eq _unavailable
    npc_msg 25
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _cancel
    RunNewCommand 5, 1 // Recheck and commit the whole exchange atomically.
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _empty
    compare VAR_SPECIAL_RESULT, 2
    goto_if_eq _money
    compare VAR_SPECIAL_RESULT, 3
    goto_if_eq _space
    compare VAR_SPECIAL_RESULT, 4
    goto_if_eq _unavailable
    closemsg
    fade_screen 6, 1, 0, RGB_BLACK
    wait_fade
    wait 30, VAR_SPECIAL_x8002
    fade_screen 6, 1, 1, RGB_BLACK
    wait_fade
    play_se SEQ_SE_DP_REGI
    npc_msg 26
    goto _finish
_empty:
    npc_msg 27
    goto _finish
_money:
    npc_msg 28
    goto _finish
_space:
    npc_msg 29
    goto _finish
_unavailable:
    npc_msg 30
    goto _finish
_cancel:
    npc_msg 31
_finish:
    wait_button_or_walk_away
    closemsg
    releaseall
    end
.close
