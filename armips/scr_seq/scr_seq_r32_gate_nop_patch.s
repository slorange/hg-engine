.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

.create "build/r32_gate_nop_patch.bin", 0

// Neutralize walk-past / coord gate scripts (release immediately).
    releaseall
    end

.close
