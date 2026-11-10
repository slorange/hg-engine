.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Saffron Gym Sabrina — Leader talk (scr_seq 829 slot 0 = script 1, MAP_T11GYM0101).
// Level scripts 602 = 02 05 00 → on-transition script 5 = slot 4. Do not patch it.

.equ TRAINER_LEADER_SABRINA, 258
.equ TRAINER_LEADER_SABRINA_REMATCH, 725
.equ ITEM_TM048, 375
.equ ITEM_TM077, 404
.equ ITEM_TM004, 331
.equ ITEM_TM085, 412
.equ ITEM_TM029, 356

.equ SCORE_EVENT_BADGE_GET, 22

// data/text 531 (msgenc index). Vanilla 0–9; appended 10–18.
.equ MSG_PRE_BATTLE, 0
.equ MSG_POST_BATTLE, 1
.equ MSG_RECEIVED_BADGE, 2
.equ MSG_ALREADY_BEATEN, 5
.equ MSG_TM_CHOICE_TM48, 10
.equ MSG_TM_CHOICE_TM77, 11
.equ MSG_TM_CHOICE_TM04, 12
.equ MSG_TM_CHOICE_TM85, 13
.equ MSG_TM_CHOICE_TM29, 14
.equ MSG_REMATCH_OFFER, 15
.equ MSG_REMATCH_ACCEPT, 16
.equ MSG_REMATCH_WON, 17
.equ MSG_FAREWELL, 18

.equ BADGES_TM04, 4
.equ BADGES_TM85, 6
.equ BADGES_TM29, 10

.if GYM_BADGE_COUNT_FIELD_REWARDS == 0
.error "Build via tools/patch_scr_seq_gym_sabrina.py (sets GYM_BADGE_COUNT_FIELD_REWARDS)"
.endif

.create "build/sabrina_gym_slot0.bin", 0

scr_seq_sabrina_gym_leader:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    goto_if_set FLAG_GOT_TM48_FROM_SABRINA, _rematch_offer
    CheckBadge BADGE_MARSH, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _already_beaten
    npc_msg MSG_PRE_BATTLE
    closemsg
    trainer_battle TRAINER_LEADER_SABRINA, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_POST_BATTLE
    wait_button
    closemsg
    GiveBadge BADGE_MARSH
    addvar VAR_UNK_4135, 1
    setflag 2456
    add_special_game_stat SCORE_EVENT_BADGE_GET
    settrainerflag 230
    settrainerflag 415
    settrainerflag 368
    settrainerflag 369
    buffer_players_name 0
    npc_msg MSG_RECEIVED_BADGE
    wait_button
    closemsg
    play_fanfare SEQ_ME_BADGE
    wait_fanfare
.include "armips/include/gym_badge_hm_reward.inc"
_tm_grant:
    // Skill Swap and Psych Up are both unlocked at 0 badges, so the menu always opens.
    count_badges VAR_SPECIAL_x8000
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_TM_CHOOSE
    touchscreen_menu_hide
    menu_init 1, 1, 0, 0, VAR_SPECIAL_RESULT
    menu_item_add MSG_TM_CHOICE_TM48, 255, 0
    menu_item_add MSG_TM_CHOICE_TM77, 255, 1
    compare VAR_SPECIAL_x8000, BADGES_TM04
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM04, 255, 2
    compare VAR_SPECIAL_x8000, BADGES_TM85
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM85, 255, 3
    compare VAR_SPECIAL_x8000, BADGES_TM29
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM29, 255, 4
_menu_show:
    menu_exec
    touchscreen_menu_show
    closemsg
    switch VAR_SPECIAL_RESULT
    case 0, _pick_tm48
    case 1, _pick_tm77
    case 2, _pick_tm04
    case 3, _pick_tm85
    case 4, _pick_tm29
    goto _pick_tm48

_pick_tm48:
    setvar VAR_SPECIAL_x8004, ITEM_TM048
    goto _give_tm
_pick_tm77:
    setvar VAR_SPECIAL_x8004, ITEM_TM077
    goto _give_tm
_pick_tm04:
    setvar VAR_SPECIAL_x8004, ITEM_TM004
    goto _give_tm
_pick_tm85:
    setvar VAR_SPECIAL_x8004, ITEM_TM085
    goto _give_tm
_pick_tm29:
    setvar VAR_SPECIAL_x8004, ITEM_TM029

_give_tm:
    setvar VAR_SPECIAL_x8005, 1
    hasspaceforitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _bag_full
    callstd std_give_item_verbose
    setflag FLAG_GOT_TM48_FROM_SABRINA
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
    goto_if_unset FLAG_GOT_TM48_FROM_SABRINA, _tm_grant
_rematch_offer:
    npc_msg MSG_REMATCH_OFFER
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _rematch_declined
    npc_msg MSG_REMATCH_ACCEPT
    closemsg
    trainer_battle TRAINER_LEADER_SABRINA_REMATCH, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_REMATCH_WON
    closemsg
    clearflag FLAG_GOT_TM48_FROM_SABRINA
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
