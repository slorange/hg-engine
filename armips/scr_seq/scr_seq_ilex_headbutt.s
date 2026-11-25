.nds
.thumb
.include "armips/include/scriptmacros.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

.create "build/ilex_headbutt.bin", 0
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    npc_msg 69
    wait_ab_press
    count_badges VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 4
    goto_if_ge tutor_unlocked
    npc_msg 72
    wait_ab_press
    closemsg
    releaseall
    end

tutor_unlocked:
    // The build patch links this jump to the original tutoring offer.
    goto tutor_unlocked
.close
