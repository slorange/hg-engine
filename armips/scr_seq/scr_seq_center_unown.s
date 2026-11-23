.nds
.thumb
.include "armips/include/scriptmacros.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

.create "build/center_unown.bin", 0
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    RunNewCommand 10, 0
    compare VAR_SPECIAL_RESULT, 28
    goto_if_eq _complete
    buffer_int 0, VAR_SPECIAL_RESULT
    npc_msg 46
    wait_button_or_walk_away
    npc_msg 49
    goto _finish
_complete:
    npc_msg 50
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _cancel
    RunNewCommand 10, 1
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _full
    npc_msg 51
    goto _finish
_full:
    npc_msg 52
    goto _finish
_cancel:
    closemsg
    releaseall
    end
_finish:
    wait_button_or_walk_away
    closemsg
    releaseall
    end
.close
