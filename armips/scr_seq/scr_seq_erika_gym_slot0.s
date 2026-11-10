.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Celadon Gym Erika — Leader talk (scr_seq 786 slot 0 = script 1, MAP_T07GYM0101).
// Level scripts 559 = 02 03 00 → on-transition script 3 = slot 2. Do not patch it.
// Zone 352 is also the Celadon cut-tree member. Do not rewrite it.

.equ TRAINER_LEADER_ERIKA, 256
.equ TRAINER_LEADER_ERIKA_REMATCH, 723
.equ ITEM_TM009, 336
.equ ITEM_TM086, 413
.equ ITEM_TM019, 346
.equ ITEM_TM022, 349
.equ ITEM_TM053, 380

.equ SCORE_EVENT_BADGE_GET, 22

// data/text 492 (msgenc index). Vanilla 0–6; appended 7–15.
.equ MSG_PRE_BATTLE, 0
.equ MSG_POST_BATTLE, 1
.equ MSG_RECEIVED_BADGE, 2
.equ MSG_ALREADY_BEATEN, 4
.equ MSG_TM_CHOICE_TM09, 7
.equ MSG_TM_CHOICE_TM86, 8
.equ MSG_TM_CHOICE_TM19, 9
.equ MSG_TM_CHOICE_TM22, 10
.equ MSG_TM_CHOICE_TM53, 11
.equ MSG_REMATCH_OFFER, 12
.equ MSG_REMATCH_ACCEPT, 13
.equ MSG_REMATCH_WON, 14
.equ MSG_FAREWELL, 15

.equ BADGES_TM86, 2
.equ BADGES_TM19, 4
.equ BADGES_TM22, 8

.if GYM_BADGE_COUNT_FIELD_REWARDS == 0
.error "Build via tools/patch_scr_seq_gym_erika.py (sets GYM_BADGE_COUNT_FIELD_REWARDS)"
.endif

.create "build/erika_gym_slot0.bin", 0

scr_seq_erika_gym_leader:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    goto_if_set FLAG_GOT_TM19_FROM_ERIKA, _rematch_offer
    CheckBadge BADGE_RAINBOW, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _already_beaten
    npc_msg MSG_PRE_BATTLE
    closemsg
    trainer_battle TRAINER_LEADER_ERIKA, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_POST_BATTLE
    wait_button
    closemsg
    GiveBadge BADGE_RAINBOW
    addvar VAR_UNK_4135, 1
    add_special_game_stat SCORE_EVENT_BADGE_GET
    settrainerflag 326
    settrainerflag 356
    settrainerflag 336
    settrainerflag 346
    buffer_players_name 0
    npc_msg MSG_RECEIVED_BADGE
    wait_button
    closemsg
    play_fanfare SEQ_ME_BADGE
    wait_fanfare
.include "armips/include/gym_badge_hm_reward.inc"
_tm_grant:
    count_badges VAR_SPECIAL_x8000
    compare VAR_SPECIAL_x8000, BADGES_TM86
    goto_if_lt _only_tm09
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_TM_CHOOSE
    touchscreen_menu_hide
    menu_init 1, 1, 0, 0, VAR_SPECIAL_RESULT
    menu_item_add MSG_TM_CHOICE_TM09, 255, 0
    menu_item_add MSG_TM_CHOICE_TM86, 255, 1
    compare VAR_SPECIAL_x8000, BADGES_TM19
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM19, 255, 2
    compare VAR_SPECIAL_x8000, BADGES_TM22
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM22, 255, 3
    menu_item_add MSG_TM_CHOICE_TM53, 255, 4
_menu_show:
    menu_exec
    touchscreen_menu_show
    closemsg
    switch VAR_SPECIAL_RESULT
    case 0, _pick_tm09
    case 1, _pick_tm86
    case 2, _pick_tm19
    case 3, _pick_tm22
    case 4, _pick_tm53
    goto _only_tm09

_only_tm09:
_pick_tm09:
    setvar VAR_SPECIAL_x8004, ITEM_TM009
    goto _give_tm
_pick_tm86:
    setvar VAR_SPECIAL_x8004, ITEM_TM086
    goto _give_tm
_pick_tm19:
    setvar VAR_SPECIAL_x8004, ITEM_TM019
    goto _give_tm
_pick_tm22:
    setvar VAR_SPECIAL_x8004, ITEM_TM022
    goto _give_tm
_pick_tm53:
    setvar VAR_SPECIAL_x8004, ITEM_TM053

_give_tm:
    setvar VAR_SPECIAL_x8005, 1
    hasspaceforitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _bag_full
    callstd std_give_item_verbose
    setflag FLAG_GOT_TM19_FROM_ERIKA
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
    goto_if_unset FLAG_GOT_TM19_FROM_ERIKA, _tm_grant
_rematch_offer:
    npc_msg MSG_REMATCH_OFFER
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _rematch_declined
    npc_msg MSG_REMATCH_ACCEPT
    closemsg
    trainer_battle TRAINER_LEADER_ERIKA_REMATCH, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_REMATCH_WON
    closemsg
    clearflag FLAG_GOT_TM19_FROM_ERIKA
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
