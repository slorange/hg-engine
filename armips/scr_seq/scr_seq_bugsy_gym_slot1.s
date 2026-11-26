.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Azalea Gym Bugsy — Leader talk (scr_seq 869 slot 1 = script 2, MAP_T23GYM0102).
// Slot 16 is the on-transition script (level scripts 642). Do not patch it.
// Entrance map T23GYM0101 is scr_seq 868 and has no battle.

.equ TRAINER_LEADER_BUGSY, 21
.equ TRAINER_LEADER_BUGSY_REMATCH, 713
.equ ITEM_TM062, 389
.equ ITEM_TM089, 416
.equ ITEM_TM081, 408

.equ SCORE_EVENT_BADGE_GET, 22

// data/text/567.txt. Vanilla 0–6; appended 7–13.
.equ MSG_PRE_BATTLE, 0
.equ MSG_POST_BATTLE, 1
.equ MSG_RECEIVED_BADGE, 2
.equ MSG_ALREADY_BEATEN, 6
.equ MSG_TM_CHOICE_TM62, 7
.equ MSG_TM_CHOICE_TM89, 8
.equ MSG_TM_CHOICE_TM81, 9
.equ MSG_REMATCH_OFFER, 10
.equ MSG_REMATCH_ACCEPT, 11
.equ MSG_REMATCH_WON, 12
.equ MSG_FAREWELL, 13

.equ BADGES_TM89, 4
.equ BADGES_TM81, 6

.if GYM_BADGE_COUNT_FIELD_REWARDS == 0
.error "Build via tools/patch_scr_seq_gym_bugsy.py (sets GYM_BADGE_COUNT_FIELD_REWARDS)"
.endif

.equ MSG_HINT_OFFER, 14
.equ MSG_HINT_FIRST_WILD, 15
.equ MSG_HINT_SKIP, 37
.equ MSG_HINT_LAND, 38
.equ MSG_HINT_BADGES, 45
.equ MSG_HINT_CHAMPION, 46
.equ MSG_HINT_RESEARCH, 47
.equ MSG_HINT_FOSSIL_SOURCE, 48
.equ MSG_HINT_FOSSIL_RESTORE, 49
.equ MSG_HINT_GOLDENROD, 50
.equ MSG_HINT_CELADON, 51
.equ HINT_WILD_COUNT, MSG_HINT_SKIP - MSG_HINT_FIRST_WILD
.equ HINT_SKIP, HINT_WILD_COUNT
.equ HINT_HAS_GAME_CORNER, 0
.equ HINT_HAS_RESEARCH, 1
.equ HINT_HAS_FOSSILS, 1
.equ HINT_HAS_GENERIC_PRIZES, 1
.equ NO_LIST_HIGHLIGHT, 255
.equ CMD_GYM_POKEMON_HINT, 15

.create "build/bugsy_gym_slot1.bin", 0

scr_seq_bugsy_gym_leader:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    goto_if_set FLAG_GOT_TM89_FROM_BUGSY, _rematch_offer
    CheckBadge BADGE_HIVE, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _already_beaten
    npc_msg MSG_PRE_BATTLE
    closemsg
    trainer_battle TRAINER_LEADER_BUGSY, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_POST_BATTLE
    wait_button
    closemsg
    buffer_players_name 0
    npc_msg MSG_RECEIVED_BADGE
    wait_button
    closemsg
    GiveBadge BADGE_HIVE
    settrainerflag 68
    settrainerflag 67
    settrainerflag 69
    settrainerflag 10
    add_special_game_stat SCORE_EVENT_BADGE_GET
    play_fanfare SEQ_ME_BADGE
    wait_fanfare
.include "armips/include/gym_badge_hm_reward.inc"
_tm_grant:
    call _pokemon_hint
_tm_menu:
    count_badges VAR_SPECIAL_x8000
    compare VAR_SPECIAL_x8000, BADGES_TM89
    goto_if_lt _only_tm62
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_TM_CHOOSE
    touchscreen_menu_hide
    menu_init 1, 1, 0, 0, VAR_SPECIAL_RESULT
    menu_item_add MSG_TM_CHOICE_TM62, 255, 0
    menu_item_add MSG_TM_CHOICE_TM89, 255, 1
    compare VAR_SPECIAL_x8000, BADGES_TM81
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM81, 255, 2
_menu_show:
    menu_exec
    touchscreen_menu_show
    closemsg
    switch VAR_SPECIAL_RESULT
    case 0, _pick_tm62
    case 1, _pick_tm89
    case 2, _pick_tm81
    goto _only_tm62

_only_tm62:
_pick_tm62:
    setvar VAR_SPECIAL_x8004, ITEM_TM062
    goto _give_tm
_pick_tm89:
    setvar VAR_SPECIAL_x8004, ITEM_TM089
    goto _give_tm
_pick_tm81:
    setvar VAR_SPECIAL_x8004, ITEM_TM081

_give_tm:
    setvar VAR_SPECIAL_x8005, 1
    hasspaceforitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _bag_full
    callstd std_give_item_verbose
    setflag FLAG_GOT_TM89_FROM_BUGSY
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
    goto_if_unset FLAG_GOT_TM89_FROM_BUGSY, _tm_menu
_rematch_offer:
    npc_msg MSG_REMATCH_OFFER
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _rematch_declined
    npc_msg MSG_REMATCH_ACCEPT
    closemsg
    trainer_battle TRAINER_LEADER_BUGSY_REMATCH, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_REMATCH_WON
    closemsg
    clearflag FLAG_GOT_TM89_FROM_BUGSY
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

.include "armips/include/gym_pokemon_hint_menu.inc"

.close
