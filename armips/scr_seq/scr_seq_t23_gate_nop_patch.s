.nds
.thumb

.include "armips/include/scriptmacros.s"

.create "build/t23_gate_nop_patch.bin", 0

// Open-world: neutralize Azalea coord / rival scripts (release immediately).
    releaseall
    end

.close
