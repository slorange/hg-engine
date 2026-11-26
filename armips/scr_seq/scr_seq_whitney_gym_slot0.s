.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Goldenrod Gym Whitney — Leader talk (scr_seq 886 slot 0 = script 1, MAP_T25GYM0101).
// First win cries and does not give the badge. Slot 1 is the chase (sets FLAG_UNK_0B7).
// Slot 4 is the on-transition script (level scripts 659). Leave both vanilla.
// Badge, level cap, HM, and the TM menu run only on the talk after the chase.

.equ TRAINER_LEADER_WHITNEY, 30
.equ TRAINER_LEADER_WHITNEY_REMATCH, 714
.equ ITEM_TM045, 372
.equ ITEM_TM042, 369
.equ ITEM_TM027, 354
.equ ITEM_TM015, 342
.equ ITEM_TM068, 395

.equ SCORE_EVENT_BADGE_GET, 22

// data/text/582.txt. Vanilla 0–13; appended 14–22.
.equ MSG_PRE_BATTLE, 0
.equ MSG_CRYING, 2
.equ MSG_BADGE_ASK, 3
.equ MSG_RECEIVED_BADGE, 4
.equ MSG_ALREADY_BEATEN, 8
.equ MSG_TM_CHOICE_TM45, 14
.equ MSG_TM_CHOICE_TM42, 15
.equ MSG_TM_CHOICE_TM27, 16
.equ MSG_TM_CHOICE_TM15, 17
.equ MSG_TM_CHOICE_TM68, 18
.equ MSG_REMATCH_OFFER, 19
.equ MSG_REMATCH_ACCEPT, 20
.equ MSG_REMATCH_WON, 21
.equ MSG_FAREWELL, 22

.equ BADGES_TM42, 2
.equ BADGES_TM27, 4
.equ BADGES_TM15, 8

.if GYM_BADGE_COUNT_FIELD_REWARDS == 0
.error "Build via tools/patch_scr_seq_gym_whitney.py (sets GYM_BADGE_COUNT_FIELD_REWARDS)"
.endif

.equ MSG_HINT_OFFER, 23
.equ MSG_HINT_FIRST_WILD, 24
.equ MSG_HINT_SKIP, 49
.equ MSG_HINT_LAND, 50
.equ MSG_HINT_BADGES, 57
.equ MSG_HINT_CHAMPION, 58
.equ MSG_HINT_RESEARCH, 59
.equ MSG_HINT_FOSSIL_SOURCE, 60
.equ MSG_HINT_FOSSIL_RESTORE, 61
.equ MSG_HINT_GOLDENROD, 62
.equ MSG_HINT_CELADON, 63
.equ HINT_WILD_COUNT, MSG_HINT_SKIP - MSG_HINT_FIRST_WILD
.equ HINT_SKIP, HINT_WILD_COUNT
.equ HINT_HAS_GAME_CORNER, 0
.equ HINT_HAS_RESEARCH, 1
.equ HINT_HAS_FOSSILS, 1
.equ HINT_HAS_GENERIC_PRIZES, 1
.equ NO_LIST_HIGHLIGHT, 255
.equ CMD_GYM_POKEMON_HINT, 16

.create "build/whitney_gym_slot0.bin", 0

scr_seq_whitney_gym_leader:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    goto_if_set FLAG_GOT_TM45_FROM_WHITNEY, _rematch_offer
    CheckBadge BADGE_PLAIN, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _already_beaten
    checkflag FLAG_UNK_0B7
    goto_if_eq _badge_grant
    compare VAR_UNK_410A, 1
    goto_if_eq _still_crying
    npc_msg MSG_PRE_BATTLE
    closemsg
    trainer_battle TRAINER_LEADER_WHITNEY, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    settrainerflag 22
    settrainerflag 71
    settrainerflag 5
    settrainerflag 70
    add_special_game_stat SCORE_EVENT_BADGE_GET
    move_person_facing 1, 13, 0, 15, 0
    npc_msg MSG_CRYING
    wait_button
    closemsg
    releaseall
    setvar VAR_UNK_410A, 1
    setflag FLAG_UNK_084
    setvar VAR_UNK_40DA, 1
    clearflag FLAG_HIDE_PARK_SOUTH_GATE_POKEATHLON_ENTHUSIASTS_UNLOCKED
    setflag FLAG_HIDE_PARK_SOUTH_GATE_POKEATHLON_ENTHUSIASTS_LOCKED
    end

_still_crying:
    npc_msg MSG_CRYING
    wait_button
    closemsg
    releaseall
    end

_badge_grant:
    npc_msg MSG_BADGE_ASK
    buffer_players_name 0
    npc_msg MSG_RECEIVED_BADGE
    wait_button
    closemsg
    GiveBadge BADGE_PLAIN
    setvar VAR_UNK_410A, 2
    clearflag FLAG_UNK_084
    setflag FLAG_UNK_998
    play_fanfare SEQ_ME_BADGE
    wait_fanfare
.include "armips/include/gym_badge_hm_reward.inc"
_tm_grant:
    call _pokemon_hint
_tm_menu:
    count_badges VAR_SPECIAL_x8000
    compare VAR_SPECIAL_x8000, BADGES_TM42
    goto_if_lt _only_tm45
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_TM_CHOOSE
    touchscreen_menu_hide
    menu_init 1, 1, 0, 0, VAR_SPECIAL_RESULT
    menu_item_add MSG_TM_CHOICE_TM45, 255, 0
    menu_item_add MSG_TM_CHOICE_TM42, 255, 1
    compare VAR_SPECIAL_x8000, BADGES_TM27
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM27, 255, 2
    compare VAR_SPECIAL_x8000, BADGES_TM15
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM15, 255, 3
    menu_item_add MSG_TM_CHOICE_TM68, 255, 4
_menu_show:
    menu_exec
    touchscreen_menu_show
    closemsg
    switch VAR_SPECIAL_RESULT
    case 0, _pick_tm45
    case 1, _pick_tm42
    case 2, _pick_tm27
    case 3, _pick_tm15
    case 4, _pick_tm68
    goto _only_tm45

_only_tm45:
_pick_tm45:
    setvar VAR_SPECIAL_x8004, ITEM_TM045
    goto _give_tm
_pick_tm42:
    setvar VAR_SPECIAL_x8004, ITEM_TM042
    goto _give_tm
_pick_tm27:
    setvar VAR_SPECIAL_x8004, ITEM_TM027
    goto _give_tm
_pick_tm15:
    setvar VAR_SPECIAL_x8004, ITEM_TM015
    goto _give_tm
_pick_tm68:
    setvar VAR_SPECIAL_x8004, ITEM_TM068

_give_tm:
    setvar VAR_SPECIAL_x8005, 1
    hasspaceforitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _bag_full
    callstd std_give_item_verbose
    setflag FLAG_GOT_TM45_FROM_WHITNEY
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
    goto_if_unset FLAG_GOT_TM45_FROM_WHITNEY, _tm_menu
_rematch_offer:
    npc_msg MSG_REMATCH_OFFER
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _rematch_declined
    npc_msg MSG_REMATCH_ACCEPT
    closemsg
    trainer_battle TRAINER_LEADER_WHITNEY_REMATCH, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_REMATCH_WON
    closemsg
    clearflag FLAG_GOT_TM45_FROM_WHITNEY
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
