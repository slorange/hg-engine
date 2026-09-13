.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/soundeffects.s"
// Violet Gym — elevator (scr_seq 859 slot 5).
// Vanilla always opened with Falkner's TM/Roost line (msg 6) before violet_gym_elevator.

.create "build/falkner_gym_slot5.bin", 0

scr_seq_falkner_gym_elevator_use:
    play_se SEQ_SE_DP_SELECT
    lockall
    violet_gym_elevator
    releaseall
    end

.close
