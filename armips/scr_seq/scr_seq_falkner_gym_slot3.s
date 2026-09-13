.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Violet Gym — elevator gate NPC (scr_seq 859 slot 3).

// data/text/558.txt: index 10 = Sprout Tower hint (skip blank index 9).
.equ MSG_SPROUT_TOWER_HINT, 10

.create "build/falkner_gym_slot3.bin", 0

scr_seq_falkner_gym_elevator_gate:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    goto_if_set FLAG_HIDE_VIOLET_GYM_GYM_GUY_BEFORE_SPROUT, _allow_pass
    npc_msg MSG_SPROUT_TOWER_HINT
    wait_button
    closemsg
    releaseall
    end

_allow_pass:
    releaseall
    end

.close
