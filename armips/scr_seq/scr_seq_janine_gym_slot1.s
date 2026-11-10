.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Fuchsia Gym Janine — Leader talk (scr_seq 809 slot 1 = script 2, MAP_T08GYM0101).
// Slot 0 is the on-transition script (level scripts 582). Do not patch it.

.equ TRAINER_LEADER_JANINE, 257
.equ TRAINER_LEADER_JANINE_REMATCH, 724
.equ ITEM_TM006, 333
.equ ITEM_TM036, 363
.equ ITEM_TM084, 411

.equ SCORE_EVENT_BADGE_GET, 22
.equ VANILLA_PRE_BATTLE_TEMP, 111

// data/text 514 (msgenc index). Vanilla 0–18; appended 19–25.
.equ MSG_PRE_BATTLE, 0
.equ MSG_POST_BATTLE, 1
.equ MSG_RECEIVED_BADGE, 2
.equ MSG_ALREADY_BEATEN, 4
.equ MSG_TM_CHOICE_TM06, 19
.equ MSG_TM_CHOICE_TM84, 20
.equ MSG_TM_CHOICE_TM36, 21
.equ MSG_REMATCH_OFFER, 22
.equ MSG_REMATCH_ACCEPT, 23
.equ MSG_REMATCH_WON, 24
.equ MSG_FAREWELL, 25

.equ BADGES_TM84, 6
.equ BADGES_TM36, 8

.if GYM_BADGE_COUNT_FIELD_REWARDS == 0
.error "Build via tools/patch_scr_seq_gym_janine.py (sets GYM_BADGE_COUNT_FIELD_REWARDS)"
.endif

.create "build/janine_gym_slot1.bin", 0

scr_seq_janine_gym_leader:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    goto_if_set FLAG_GOT_TM84_FROM_JANINE, _rematch_offer
    CheckBadge BADGE_SOUL, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _already_beaten
    npc_msg MSG_PRE_BATTLE
    closemsg
    setvar VAR_TEMP_x400B, VANILLA_PRE_BATTLE_TEMP
    trainer_battle TRAINER_LEADER_JANINE, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    setvar VAR_TEMP_x400B, 0
    npc_msg MSG_POST_BATTLE
    wait_button
    closemsg
    GiveBadge BADGE_SOUL
    addvar VAR_UNK_4135, 1
    add_special_game_stat SCORE_EVENT_BADGE_GET
    settrainerflag 83
    settrainerflag 84
    settrainerflag 136
    settrainerflag 183
    buffer_players_name 0
    npc_msg MSG_RECEIVED_BADGE
    wait_button
    closemsg
    play_fanfare SEQ_ME_BADGE
    wait_fanfare
.include "armips/include/gym_badge_hm_reward.inc"
_tm_grant:
    count_badges VAR_SPECIAL_x8000
    compare VAR_SPECIAL_x8000, BADGES_TM84
    goto_if_lt _only_tm06
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_TM_CHOOSE
    touchscreen_menu_hide
    menu_init 1, 1, 0, 0, VAR_SPECIAL_RESULT
    menu_item_add MSG_TM_CHOICE_TM06, 255, 0
    menu_item_add MSG_TM_CHOICE_TM84, 255, 1
    compare VAR_SPECIAL_x8000, BADGES_TM36
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM36, 255, 2
_menu_show:
    menu_exec
    touchscreen_menu_show
    closemsg
    switch VAR_SPECIAL_RESULT
    case 0, _pick_tm06
    case 1, _pick_tm84
    case 2, _pick_tm36
    goto _only_tm06

_only_tm06:
_pick_tm06:
    setvar VAR_SPECIAL_x8004, ITEM_TM006
    goto _give_tm
_pick_tm84:
    setvar VAR_SPECIAL_x8004, ITEM_TM084
    goto _give_tm
_pick_tm36:
    setvar VAR_SPECIAL_x8004, ITEM_TM036

_give_tm:
    setvar VAR_SPECIAL_x8005, 1
    hasspaceforitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _bag_full
    callstd std_give_item_verbose
    setflag FLAG_GOT_TM84_FROM_JANINE
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
    goto_if_unset FLAG_GOT_TM84_FROM_JANINE, _tm_grant
_rematch_offer:
    npc_msg MSG_REMATCH_OFFER
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _rematch_declined
    npc_msg MSG_REMATCH_ACCEPT
    closemsg
    setvar VAR_TEMP_x400B, VANILLA_PRE_BATTLE_TEMP
    trainer_battle TRAINER_LEADER_JANINE_REMATCH, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    setvar VAR_TEMP_x400B, 0
    npc_msg MSG_REMATCH_WON
    closemsg
    clearflag FLAG_GOT_TM84_FROM_JANINE
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
