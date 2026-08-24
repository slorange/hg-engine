.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

.create "build/a012/2_226", 0

scrdef scr_seq_R29R0101_000
scrdef scr_seq_R29R0101_001
scrdef scr_seq_R29R0101_002
scrdef_end

// Walk-past gate: Route 46 requires 2 badges.
scr_seq_R29R0101_000:
    scrcmd_609
    lockall
    count_badges VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 2
    goto_if_ge _pass
    faceplayer
    npc_msg 2
    apply_movement obj_player, _player_step_back
    wait_movement
    wait_button_or_walk_away
    closemsg
    releaseall
    end

_pass:
    releaseall
    end

scr_seq_R29R0101_001:
    simple_npc_msg 0
    end

scr_seq_R29R0101_002:
    simple_npc_msg 1
    end

.align 4

_player_step_back:
    step 13, 1
    step 1, 1
    step_end

.close
