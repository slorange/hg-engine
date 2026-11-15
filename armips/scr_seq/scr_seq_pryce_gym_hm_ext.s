.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Appended to retail scr_seq 932 after badge fanfare (vanilla TM tail replaced by goto).

.equ TRAINER_LEADER_PRYCE_REMATCH, 716
.equ ITEM_TM007, 334
.equ ITEM_TM072, 399
.equ ITEM_TM014, 341
.equ ITEM_TM013, 340

// data/text/622.txt is compact. Vanilla 0–9; appended choice lines start at 10.
// Decline reuses index 4 (the old post-gift line).
.equ MSG_ALREADY_BEATEN, 4
.equ MSG_TM_CHOICE_TM07, 10
.equ MSG_TM_CHOICE_TM72, 11
.equ MSG_TM_CHOICE_TM14, 12
.equ MSG_TM_CHOICE_TM13, 13
.equ MSG_REMATCH_OFFER, 14
.equ MSG_REMATCH_ACCEPT, 15
.equ MSG_REMATCH_WON, 16
.equ MSG_FAREWELL, 17

.equ BADGES_TM72, 2
.equ BADGES_TM14, 8
.equ BADGES_TM13, 10

.if GYM_BADGE_COUNT_FIELD_REWARDS == 0
.error "Build via tools/patch_scr_seq_gym_pryce.py (sets GYM_BADGE_COUNT_FIELD_REWARDS)"
.endif

.create "build/pryce_gym_hm_ext.bin", 0

scr_seq_pryce_gym_hm_ext:
.include "armips/include/gym_badge_hm_reward.inc"
_tm_grant:
    count_badges VAR_SPECIAL_x8000
    compare VAR_SPECIAL_x8000, BADGES_TM72
    goto_if_lt _only_tm07
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_TM_CHOOSE
    touchscreen_menu_hide
    menu_init 1, 1, 0, 0, VAR_SPECIAL_RESULT
    menu_item_add MSG_TM_CHOICE_TM07, 255, 0
    menu_item_add MSG_TM_CHOICE_TM72, 255, 1
    compare VAR_SPECIAL_x8000, BADGES_TM14
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM14, 255, 2
    compare VAR_SPECIAL_x8000, BADGES_TM13
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM13, 255, 3
_menu_show:
    menu_exec
    touchscreen_menu_show
    closemsg
    switch VAR_SPECIAL_RESULT
    case 0, _pick_tm07
    case 1, _pick_tm72
    case 2, _pick_tm14
    case 3, _pick_tm13
    goto _only_tm07

_only_tm07:
_pick_tm07:
    setvar VAR_SPECIAL_x8004, ITEM_TM007
    goto _give_tm
_pick_tm72:
    setvar VAR_SPECIAL_x8004, ITEM_TM072
    goto _give_tm
_pick_tm14:
    setvar VAR_SPECIAL_x8004, ITEM_TM014
    goto _give_tm
_pick_tm13:
    setvar VAR_SPECIAL_x8004, ITEM_TM013

_give_tm:
    setvar VAR_SPECIAL_x8005, 1
    hasspaceforitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _bag_full
    callstd std_give_item_verbose
    setflag FLAG_GOT_TM07_FROM_PRYCE
    npc_msg MSG_FAREWELL
    wait_button
    closemsg
    releaseall
    end

_bag_full:
    callstd std_bag_is_full
    closemsg
    releaseall
    end

// Vanilla badge-owned branch is retargeted here by patch_scr_seq_gym_pryce.py.
// The old photo script lived in bytes the TM trampoline already overwrites.
_pryce_revisit:
    goto_if_unset FLAG_GOT_TM07_FROM_PRYCE, _tm_grant
    npc_msg MSG_REMATCH_OFFER
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _rematch_declined
    npc_msg MSG_REMATCH_ACCEPT
    closemsg
    trainer_battle TRAINER_LEADER_PRYCE_REMATCH, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_REMATCH_WON
    closemsg
    clearflag FLAG_GOT_TM07_FROM_PRYCE
    goto _tm_grant

_rematch_declined:
    npc_msg MSG_ALREADY_BEATEN
    wait_button
    closemsg
    releaseall
    end

_white_out:
    white_out
    releaseall
    end

.close
