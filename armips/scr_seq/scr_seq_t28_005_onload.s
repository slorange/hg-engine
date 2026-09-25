.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/vars.s"

.create "build/t28_005_patch.bin", 0

// Mahogany Town OnLoad when OPENWORLD_STORY_SKIP_AND_STARTING_ITEMS: rocket flags set at Mom intro
// (openworld_story_skip_flags.inc). Only map-local cleanup here.
    hide_person 0
    hide_person 2
    end

.close
