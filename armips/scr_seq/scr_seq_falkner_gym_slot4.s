.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/vars.s"
// Violet Gym — upper-floor elevator pad (scr_seq 859 slot 4 / obj script 4).

.create "build/falkner_gym_slot4.bin", 0

scr_seq_falkner_gym_elevator_upper:
    setvar VAR_TEMP_x4000, 0
    violet_gym_elevator
    end

.close
