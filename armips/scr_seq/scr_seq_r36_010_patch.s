.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

.create "build/r36_010_patch.bin", 0

// Route 36 OnLoad: hide Sudowoodo on every map load (existing saves OK).
    setflag FLAG_HIDE_ROUTE_36_SUDOWOODO
    goto_if_set FLAG_ENGAGING_STATIC_POKEMON, _cleanup
    end

_cleanup:
    hide_person 4
    clearflag FLAG_ENGAGING_STATIC_POKEMON
    end

.close
