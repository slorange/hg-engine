.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Pewter Gym Brock — Leader talk script (scr_seq 752 slot 0 = script 1, MAP_T03GYM0101).

.equ TRAINER_LEADER_BROCK, 253
.equ TRAINER_LEADER_BROCK_REMATCH, 720
.equ ITEM_TM026, 353
.equ ITEM_TM037, 364
.equ ITEM_TM039, 366
.equ ITEM_TM069, 396
.equ ITEM_TM071, 398
.equ ITEM_TM080, 407

.equ SCORE_EVENT_BADGE_GET, 22
.equ TRAINER_PEWTER_GYM_1, 308
.equ TRAINER_PEWTER_GYM_2, 685

// data/text 462 (msgenc index).
.equ MSG_PRE_BATTLE, 0
.equ MSG_POST_BATTLE, 1
.equ MSG_RECEIVED_BADGE, 2
.equ MSG_ALREADY_BEATEN, 5
.equ MSG_TM_CHOICE_TM37, 10
.equ MSG_TM_CHOICE_TM39, 11
.equ MSG_TM_CHOICE_TM69, 12
.equ MSG_TM_CHOICE_TM80, 13
.equ MSG_TM_CHOICE_TM71, 14
.equ MSG_TM_CHOICE_TM26, 15
.equ MSG_REMATCH_OFFER, 16
.equ MSG_REMATCH_ACCEPT, 17
.equ MSG_REMATCH_WON, 18
.equ MSG_FAREWELL, 19

// Minimum badges (incl. Boulder) to offer each TM; Sandstorm / Rock Tomb / Rock Polish always.
// Gated entries are added in ascending order so one early exit skips the rest.
.equ BADGES_TM80, 4
.equ BADGES_TM71, 8
.equ BADGES_TM26, 12

.if GYM_BADGE_COUNT_FIELD_REWARDS == 0
.error "Build via tools/patch_scr_seq_gym_brock.py (sets GYM_BADGE_COUNT_FIELD_REWARDS)"
.endif

.create "build/brock_gym_slot0.bin", 0

scr_seq_brock_gym_leader:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    goto_if_set FLAG_GOT_TM80_FROM_BROCK, _rematch_offer
    CheckBadge BADGE_BOULDER, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _already_beaten
    npc_msg MSG_PRE_BATTLE
    closemsg
    trainer_battle TRAINER_LEADER_BROCK, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_POST_BATTLE
    wait_button
    closemsg
    GiveBadge BADGE_BOULDER
    addvar VAR_UNK_4135, 1
    add_special_game_stat SCORE_EVENT_BADGE_GET
    settrainerflag TRAINER_PEWTER_GYM_1
    settrainerflag TRAINER_PEWTER_GYM_2
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
    menu_item_add MSG_TM_CHOICE_TM37, 255, 0
    menu_item_add MSG_TM_CHOICE_TM39, 255, 1
    menu_item_add MSG_TM_CHOICE_TM69, 255, 2
    compare VAR_SPECIAL_x8000, BADGES_TM80
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM80, 255, 3
    compare VAR_SPECIAL_x8000, BADGES_TM71
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM71, 255, 4
    compare VAR_SPECIAL_x8000, BADGES_TM26
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM26, 255, 5
_menu_show:
    menu_exec
    touchscreen_menu_show
    closemsg
    switch VAR_SPECIAL_RESULT
    case 0, _pick_tm37
    case 1, _pick_tm39
    case 2, _pick_tm69
    case 3, _pick_tm80
    case 4, _pick_tm71
    goto _pick_tm26

_pick_tm26:
    setvar VAR_SPECIAL_x8004, ITEM_TM026
    goto _give_tm
_pick_tm37:
    setvar VAR_SPECIAL_x8004, ITEM_TM037
    goto _give_tm
_pick_tm39:
    setvar VAR_SPECIAL_x8004, ITEM_TM039
    goto _give_tm
_pick_tm69:
    setvar VAR_SPECIAL_x8004, ITEM_TM069
    goto _give_tm
_pick_tm71:
    setvar VAR_SPECIAL_x8004, ITEM_TM071
    goto _give_tm
_pick_tm80:
    setvar VAR_SPECIAL_x8004, ITEM_TM080

_give_tm:
    setvar VAR_SPECIAL_x8005, 1
    hasspaceforitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _bag_full
    callstd std_give_item_verbose
    setflag FLAG_GOT_TM80_FROM_BROCK
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
    goto_if_unset FLAG_GOT_TM80_FROM_BROCK, _tm_grant
_rematch_offer:
    npc_msg MSG_REMATCH_OFFER
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _rematch_declined
    npc_msg MSG_REMATCH_ACCEPT
    closemsg
    trainer_battle TRAINER_LEADER_BROCK_REMATCH, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_REMATCH_WON
    closemsg
    // Cleared so a bag-full rematch reward is retried on the next talk instead of offering another battle.
    clearflag FLAG_GOT_TM80_FROM_BROCK
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
