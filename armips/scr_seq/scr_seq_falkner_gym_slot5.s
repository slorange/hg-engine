.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Violet Gym — lower-floor elevator (scr_seq 859 slot 5; engine scripts 10201/10202).
// Vanilla gated on Zephyr Badge + TM51 line; open-world uses setvar + elevator only.

.create "build/falkner_gym_slot5.bin", 0

scr_seq_falkner_gym_elevator_lower:
    play_se SEQ_SE_DP_SELECT
    lockall
    setvar VAR_TEMP_x4000, 0
    violet_gym_elevator
    releaseall
    end

.close
