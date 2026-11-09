.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Cerulean Gym Misty — Leader talk script (scr_seq 760 slot 0 = script 1, MAP_T04GYM0101).

.equ TRAINER_LEADER_MISTY, 254
.equ TRAINER_LEADER_MISTY_REMATCH, 721
.equ ITEM_TM003, 330
.equ ITEM_TM018, 345
.equ ITEM_TM055, 382

.equ SCORE_EVENT_BADGE_GET, 22

// data/text 469 (msgenc index).
.equ MSG_PRE_BATTLE, 8
.equ MSG_POST_BATTLE, 9
.equ MSG_RECEIVED_BADGE, 10
.equ MSG_ALREADY_BEATEN, 13
.equ MSG_TM_CHOICE_TM03, 17
.equ MSG_TM_CHOICE_TM18, 18
.equ MSG_TM_CHOICE_TM55, 19
.equ MSG_REMATCH_OFFER, 20
.equ MSG_REMATCH_ACCEPT, 21
.equ MSG_REMATCH_WON, 22
.equ MSG_FAREWELL, 23

.equ BADGES_TM55, 4

.if GYM_BADGE_COUNT_FIELD_REWARDS == 0
.error "Build via tools/patch_scr_seq_gym_misty.py (sets GYM_BADGE_COUNT_FIELD_REWARDS)"
.endif

.create "build/misty_gym_slot0.bin", 0

scr_seq_misty_gym_leader:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    goto_if_set FLAG_GOT_TM03_FROM_MISTY, _rematch_offer
    CheckBadge BADGE_CASCADE, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _already_beaten
    npc_msg MSG_PRE_BATTLE
    closemsg
    trainer_battle TRAINER_LEADER_MISTY, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_POST_BATTLE
    wait_button
    closemsg
    GiveBadge BADGE_CASCADE
    addvar VAR_UNK_4135, 1
    add_special_game_stat SCORE_EVENT_BADGE_GET
    buffer_players_name 0
    npc_msg MSG_RECEIVED_BADGE
    wait_button
    closemsg
    play_fanfare SEQ_ME_BADGE
    wait_fanfare
.include "armips/include/gym_badge_hm_reward.inc"
_tm_grant:
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_TM_CHOOSE
    touchscreen_menu_hide
    count_badges VAR_SPECIAL_x8000
    menu_init 1, 1, 0, 0, VAR_SPECIAL_RESULT
    menu_item_add MSG_TM_CHOICE_TM03, 255, 0
    menu_item_add MSG_TM_CHOICE_TM18, 255, 1
    compare VAR_SPECIAL_x8000, BADGES_TM55
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM55, 255, 2
_menu_show:
    menu_exec
    touchscreen_menu_show
    closemsg
    switch VAR_SPECIAL_RESULT
    case 0, _pick_tm03
    case 1, _pick_tm18
    goto _pick_tm55

_pick_tm03:
    setvar VAR_SPECIAL_x8004, ITEM_TM003
    goto _give_tm
_pick_tm18:
    setvar VAR_SPECIAL_x8004, ITEM_TM018
    goto _give_tm
_pick_tm55:
    setvar VAR_SPECIAL_x8004, ITEM_TM055

_give_tm:
    setvar VAR_SPECIAL_x8005, 1
    hasspaceforitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _bag_full
    callstd std_give_item_verbose
    setflag FLAG_GOT_TM03_FROM_MISTY
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

_already_beaten:
    goto_if_unset FLAG_GOT_TM03_FROM_MISTY, _tm_grant
_rematch_offer:
    npc_msg MSG_REMATCH_OFFER
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _rematch_declined
    npc_msg MSG_REMATCH_ACCEPT
    closemsg
    trainer_battle TRAINER_LEADER_MISTY_REMATCH, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_REMATCH_WON
    closemsg
    clearflag FLAG_GOT_TM03_FROM_MISTY
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
