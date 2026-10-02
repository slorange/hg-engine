.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Appended to retail scr_seq 932 after badge fanfare (vanilla TM tail replaced by goto).

.equ ITEM_TM007, 335

.equ MSG_PRE_BATTLE, 0
.equ MSG_TM_GRANT, 3

.if GYM_BADGE_COUNT_FIELD_REWARDS == 0
.error "Build via tools/patch_scr_seq_gym_pryce.py (sets GYM_BADGE_COUNT_FIELD_REWARDS)"
.endif

.create "build/pryce_gym_hm_ext.bin", 0

scr_seq_pryce_gym_hm_ext:
.include "armips/include/gym_badge_hm_reward.inc"
_tm_grant:
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_TM_INTRO
    wait_button
    closemsg
    goto_if_no_item_space ITEM_TM007, 1, _bag_full
    play_fanfare SEQ_ME_WAZA
    wait_fanfare
    item_vars ITEM_TM007, 1
    giveitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    setflag FLAG_GOT_TM07_FROM_PRYCE
    npc_msg MSG_TM_GRANT
    wait_button
    closemsg
    releaseall
    end

_bag_full:
    callstd std_bag_is_full
    closemsg
    releaseall
    end

.close
