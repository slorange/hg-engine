.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Violet Gym — trainer hint NPC (scr_seq 859 slot 2).

// data/text/558.txt: blank line between each entry.
.equ MSG_ALREADY_BEATEN, 8

.create "build/falkner_gym_slot2.bin", 0

scr_seq_falkner_gym_trainer_hint:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    CheckBadge BADGE_ZEPHYR, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _has_badge
    releaseall
    end

_has_badge:
    npc_msg MSG_ALREADY_BEATEN
    wait_button
    closemsg
    releaseall
    end

.close
