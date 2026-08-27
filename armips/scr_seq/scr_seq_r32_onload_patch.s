.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

.create "build/r32_onload_patch.bin", 0

// Route 32 OnLoad (slot 0 / scriptId 1): force post-Zephyr-badge gate state.
    setflag FLAG_UNK_226
    setflag FLAG_UNK_228
    end

.close
