.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Vermilion Gym Lt. Surge — Leader script (scr_seq 778 slot 23 = script 24, MAP_T06GYM0101).

.equ TRAINER_LEADER_LT_SURGE, 255
.equ TRAINER_LEADER_LT_SURGE_REMATCH, 722
.equ ITEM_TM024, 351
.equ ITEM_TM025, 352
.equ ITEM_TM034, 361
.equ ITEM_TM057, 384
.equ ITEM_TM073, 400

.equ SCORE_EVENT_BADGE_GET, 22

// data/text 485 (msgenc index).
.equ MSG_PRE_BATTLE, 0
.equ MSG_POST_BATTLE, 1
.equ MSG_RECEIVED_BADGE, 2
.equ MSG_ALREADY_BEATEN, 5
// TM labels 15–19 (unlock order); rematch 20–23 — decode bank 485 before editing.
.equ MSG_TM_CHOICE_TM34, 15
.equ MSG_TM_CHOICE_TM57, 16
.equ MSG_TM_CHOICE_TM73, 17
.equ MSG_TM_CHOICE_TM25, 18
.equ MSG_TM_CHOICE_TM24, 19
.equ MSG_REMATCH_OFFER, 20
.equ MSG_REMATCH_ACCEPT, 21
.equ MSG_REMATCH_WON, 22
.equ MSG_FAREWELL, 23
.equ MSG_HINT_OFFER, 24
.equ MSG_HINT_FIRST_WILD, 25
.equ MSG_HINT_ROTOM, 36
.equ MSG_HINT_SKIP, 37
.equ MSG_HINT_LAND, 38
.equ MSG_HINT_BADGES, 45
.equ MSG_HINT_CHAMPION, 46
.equ MSG_HINT_GAME_CORNER, 47
.equ HINT_WILD_COUNT, MSG_HINT_ROTOM - MSG_HINT_FIRST_WILD
.equ HINT_SKIP, HINT_WILD_COUNT + 1
.equ HINT_HAS_GAME_CORNER, 1
.equ HINT_HAS_RESEARCH, 0
// 255 leaves the dialogue window alone when the list cursor changes.
.equ HINT_HAS_GENERIC_PRIZES, 0
.equ NO_LIST_HIGHLIGHT, 255

.equ CMD_GYM_POKEMON_HINT, 11

.equ BADGES_TM73, 2
.equ BADGES_TM25, 8
.equ BADGES_TM24, 10

.if GYM_BADGE_COUNT_FIELD_REWARDS == 0
.error "Build via tools/patch_scr_seq_gym_surge.py (sets GYM_BADGE_COUNT_FIELD_REWARDS)"
.endif

.macro remove_surge_fence_objects
    setflag FLAG_UNK_31A // Hide all six collision objects on future visits.
    hide_person 0
    hide_person 1
    hide_person 2
    hide_person 3
    hide_person 4
    hide_person 5
.endmacro

.create "build/surge_gym_slot22.bin", 0
    goto_if_set FLAG_UNK_31A, _transition_end
    // Transition scripts run without the task environment used by 0x8000 vars.
    CheckBadge BADGE_THUNDER, VAR_TEMP_x4000
    compare VAR_TEMP_x4000, 1
    goto_if_eq _repair_defeated_gym

    // Vanilla transition hides the collision objects' sprites while the puzzle is active.
    VanishOverworld 0
    VanishOverworld 1
    VanishOverworld 2
    VanishOverworld 3
    VanishOverworld 4
    VanishOverworld 5
_transition_end:
    end

_repair_defeated_gym:
    remove_surge_fence_objects
    end
.close

.create "build/surge_gym_slot23.bin", 0

scr_seq_surge_gym_leader:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    goto_if_set FLAG_GOT_TM34_FROM_LT_SURGE, _rematch_offer
    CheckBadge BADGE_THUNDER, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _already_beaten
    npc_msg MSG_PRE_BATTLE
    closemsg
    trainer_battle TRAINER_LEADER_LT_SURGE, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_POST_BATTLE
    wait_button
    closemsg
    GiveBadge BADGE_THUNDER
    vermilion_gym_lock_action 0, 3
    remove_surge_fence_objects
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
    call _pokemon_hint
_tm_menu:
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_TM_CHOOSE
    touchscreen_menu_hide
    count_badges VAR_SPECIAL_x8000
    menu_init 1, 1, 0, 0, VAR_SPECIAL_RESULT
    menu_item_add MSG_TM_CHOICE_TM34, 255, 0
    menu_item_add MSG_TM_CHOICE_TM57, 255, 1
    compare VAR_SPECIAL_x8000, BADGES_TM73
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM73, 255, 2
    compare VAR_SPECIAL_x8000, BADGES_TM25
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM25, 255, 3
    compare VAR_SPECIAL_x8000, BADGES_TM24
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM24, 255, 4
_menu_show:
    menu_exec
    touchscreen_menu_show
    closemsg
    switch VAR_SPECIAL_RESULT
    case 0, _pick_tm34
    case 1, _pick_tm57
    case 2, _pick_tm73
    case 3, _pick_tm25
    goto _pick_tm24

_pick_tm34:
    setvar VAR_SPECIAL_x8004, ITEM_TM034
    goto _give_tm
_pick_tm57:
    setvar VAR_SPECIAL_x8004, ITEM_TM057
    goto _give_tm
_pick_tm73:
    setvar VAR_SPECIAL_x8004, ITEM_TM073
    goto _give_tm
_pick_tm25:
    setvar VAR_SPECIAL_x8004, ITEM_TM025
    goto _give_tm
_pick_tm24:
    setvar VAR_SPECIAL_x8004, ITEM_TM024

_give_tm:
    setvar VAR_SPECIAL_x8005, 1
    hasspaceforitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _bag_full
    callstd std_give_item_verbose
    setflag FLAG_GOT_TM34_FROM_LT_SURGE
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
    goto_if_unset FLAG_GOT_TM34_FROM_LT_SURGE, _tm_menu
_rematch_offer:
    npc_msg MSG_REMATCH_OFFER
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _rematch_declined
    npc_msg MSG_REMATCH_ACCEPT
    closemsg
    trainer_battle TRAINER_LEADER_LT_SURGE_REMATCH, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_REMATCH_WON
    wait_button
    closemsg
    clearflag FLAG_GOT_TM34_FROM_LT_SURGE
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
