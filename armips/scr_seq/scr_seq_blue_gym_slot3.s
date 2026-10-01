.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
// Viridian Gym coord script (scr_seq 743 slot 3): vanilla lockall + 7 Kanto badge check softlocks.
// Mark post-gate state and exit (matches vanilla success path flag).

.create "build/blue_gym_slot3.bin", 0

scr_seq_blue_gym_coord_skip:
    setflag FLAG_UNK_13A
    releaseall
    end

.close
