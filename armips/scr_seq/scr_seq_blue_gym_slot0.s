.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Viridian Gym Blue — Leader talk (scr_seq 743 slot 0 = script 1, MAP_T02GYM0101).
// Slot 2 is the on-transition script (level scripts 516). Do not replace it.

.equ TRAINER_LEADER_BLUE, 261
.equ TRAINER_LEADER_BLUE_REMATCH, 727
.equ ITEM_TM020, 347
.equ ITEM_TM032, 359
.equ ITEM_TM075, 402
.equ ITEM_TM087, 414
.equ ITEM_TM092, 419

.equ SCORE_EVENT_BADGE_GET, 22
.equ VAR_BLUE_POST_WIN, 0x4096

// data/text 454 (msgenc index). Vanilla 0–10; appended 11–19.
.equ MSG_PRE_BATTLE, 0
.equ MSG_POST_BATTLE, 1
.equ MSG_RECEIVED_BADGE, 2
.equ MSG_ALREADY_BEATEN, 5
.equ MSG_TM_CHOICE_TM87, 11
.equ MSG_TM_CHOICE_TM20, 12
.equ MSG_TM_CHOICE_TM32, 13
.equ MSG_TM_CHOICE_TM75, 14
.equ MSG_TM_CHOICE_TM92, 15
.equ MSG_REMATCH_OFFER, 16
.equ MSG_REMATCH_ACCEPT, 17
.equ MSG_REMATCH_WON, 18
.equ MSG_FAREWELL, 19

.equ BADGES_TM20, 2
.equ BADGES_TM32, 4
.equ BADGES_TM75, 6
.equ BADGES_TM92, 8

.if GYM_BADGE_COUNT_FIELD_REWARDS == 0
.error "Build via tools/patch_scr_seq_gym_blue.py (sets GYM_BADGE_COUNT_FIELD_REWARDS)"
.endif

.create "build/blue_gym_slot0.bin", 0

scr_seq_blue_gym_leader:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    goto_if_set FLAG_GOT_TM92_FROM_BLUE, _rematch_offer
    CheckBadge BADGE_EARTH, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _already_beaten
    npc_msg MSG_PRE_BATTLE
    closemsg
    trainer_battle TRAINER_LEADER_BLUE, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_POST_BATTLE
    wait_button
    closemsg
    GiveBadge BADGE_EARTH
    addvar VAR_UNK_4135, 1
    setflag 2456
    add_special_game_stat SCORE_EVENT_BADGE_GET
    settrainerflag 681
    settrainerflag 683
    settrainerflag 682
    settrainerflag 684
    setflag 2431
    clearflag 663
    setflag 783
    setvar VAR_BLUE_POST_WIN, 1
    buffer_players_name 0
    npc_msg MSG_RECEIVED_BADGE
    wait_button
    closemsg
    play_fanfare SEQ_ME_BADGE
    wait_fanfare
.include "armips/include/gym_badge_hm_reward.inc"
_tm_grant:
    count_badges VAR_SPECIAL_x8000
    compare VAR_SPECIAL_x8000, BADGES_TM20
    goto_if_lt _only_tm87
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_TM_CHOOSE
    touchscreen_menu_hide
    menu_init 1, 1, 0, 0, VAR_SPECIAL_RESULT
    menu_item_add MSG_TM_CHOICE_TM87, 255, 0
    menu_item_add MSG_TM_CHOICE_TM20, 255, 1
    compare VAR_SPECIAL_x8000, BADGES_TM32
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM32, 255, 2
    compare VAR_SPECIAL_x8000, BADGES_TM75
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM75, 255, 3
    compare VAR_SPECIAL_x8000, BADGES_TM92
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM92, 255, 4
_menu_show:
    menu_exec
    touchscreen_menu_show
    closemsg
    switch VAR_SPECIAL_RESULT
    case 0, _pick_tm87
    case 1, _pick_tm20
    case 2, _pick_tm32
    case 3, _pick_tm75
    case 4, _pick_tm92
    goto _only_tm87

_only_tm87:
_pick_tm87:
    setvar VAR_SPECIAL_x8004, ITEM_TM087
    goto _give_tm
_pick_tm20:
    setvar VAR_SPECIAL_x8004, ITEM_TM020
    goto _give_tm
_pick_tm32:
    setvar VAR_SPECIAL_x8004, ITEM_TM032
    goto _give_tm
_pick_tm75:
    setvar VAR_SPECIAL_x8004, ITEM_TM075
    goto _give_tm
_pick_tm92:
    setvar VAR_SPECIAL_x8004, ITEM_TM092

_give_tm:
    setvar VAR_SPECIAL_x8005, 1
    hasspaceforitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _bag_full
    callstd std_give_item_verbose
    setflag FLAG_GOT_TM92_FROM_BLUE
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
    goto_if_unset FLAG_GOT_TM92_FROM_BLUE, _tm_grant
_rematch_offer:
    npc_msg MSG_REMATCH_OFFER
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _rematch_declined
    npc_msg MSG_REMATCH_ACCEPT
    closemsg
    trainer_battle TRAINER_LEADER_BLUE_REMATCH, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_REMATCH_WON
    closemsg
    clearflag FLAG_GOT_TM92_FROM_BLUE
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
