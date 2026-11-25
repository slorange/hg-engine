.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Olivine Gym Jasmine — Leader talk script (scr_seq 913 slot 0).

.equ TRAINER_LEADER_JASMINE, 33
.equ TRAINER_LEADER_JASMINE_REMATCH, 717

.equ VAR_MIDGAME_BADGES, 0x4134
.equ ITEM_TM047, 374
.equ ITEM_TM074, 401
.equ ITEM_TM023, 350
.equ ITEM_TM091, 418

.equ SCORE_EVENT_BADGE_GET, 22

// data/text/606.txt: indices 3–4 are blank placeholders (Steelix trade text at 7+).
// Appended choice lines start at 25.
.equ MSG_PRE_BATTLE, 0
.equ MSG_POST_BATTLE, 1
.equ MSG_POST_BATTLE_2, 2
.equ MSG_ALREADY_BEATEN, 6
.equ MSG_TM_CHOICE_TM47, 25
.equ MSG_TM_CHOICE_TM74, 26
.equ MSG_TM_CHOICE_TM23, 27
.equ MSG_TM_CHOICE_TM91, 28
.equ MSG_REMATCH_OFFER, 29
.equ MSG_REMATCH_ACCEPT, 30
.equ MSG_REMATCH_WON, 31
.equ MSG_FAREWELL, 32

.equ BADGES_TM74, 2
.equ BADGES_TM23, 6

.if GYM_BADGE_COUNT_FIELD_REWARDS == 0
.error "Build via tools/patch_scr_seq_gym_jasmine.py (sets GYM_BADGE_COUNT_FIELD_REWARDS)"
.endif

.create "build/jasmine_gym_slot0.bin", 0

scr_seq_jasmine_gym_001:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    goto_if_set FLAG_GOT_TM23_FROM_JASMINE, _rematch_offer
    CheckBadge BADGE_MINERAL, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _already_beaten
    npc_msg MSG_PRE_BATTLE
    closemsg
    trainer_battle TRAINER_LEADER_JASMINE, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_POST_BATTLE
    wait_button
    closemsg
    givebadge BADGE_MINERAL
    addvar VAR_MIDGAME_BADGES, 1
    add_special_game_stat SCORE_EVENT_BADGE_GET
    buffer_players_name 0
    npc_msg MSG_POST_BATTLE_2
    wait_button
    closemsg
    play_fanfare SEQ_ME_BADGE
    wait_fanfare
.include "armips/include/gym_badge_hm_reward.inc"
_tm_grant:
    count_badges VAR_SPECIAL_x8000
    compare VAR_SPECIAL_x8000, BADGES_TM74
    goto_if_lt _only_tm47
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_TM_CHOOSE
    touchscreen_menu_hide
    menu_init 1, 1, 0, 0, VAR_SPECIAL_RESULT
    menu_item_add MSG_TM_CHOICE_TM47, 255, 0
    menu_item_add MSG_TM_CHOICE_TM74, 255, 1
    compare VAR_SPECIAL_x8000, BADGES_TM23
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM23, 255, 2
    menu_item_add MSG_TM_CHOICE_TM91, 255, 3
_menu_show:
    menu_exec
    touchscreen_menu_show
    closemsg
    switch VAR_SPECIAL_RESULT
    case 0, _pick_tm47
    case 1, _pick_tm74
    case 2, _pick_tm23
    case 3, _pick_tm91
    goto _only_tm47

_only_tm47:
_pick_tm47:
    setvar VAR_SPECIAL_x8004, ITEM_TM047
    goto _give_tm
_pick_tm74:
    setvar VAR_SPECIAL_x8004, ITEM_TM074
    goto _give_tm
_pick_tm23:
    setvar VAR_SPECIAL_x8004, ITEM_TM023
    goto _give_tm
_pick_tm91:
    setvar VAR_SPECIAL_x8004, ITEM_TM091

_give_tm:
    setvar VAR_SPECIAL_x8005, 1
    hasspaceforitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _bag_full
    callstd std_give_item_verbose
    setflag FLAG_GOT_TM23_FROM_JASMINE
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
    goto_if_unset FLAG_GOT_TM23_FROM_JASMINE, _tm_grant
_rematch_offer:
    npc_msg MSG_REMATCH_OFFER
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _rematch_declined
    npc_msg MSG_REMATCH_ACCEPT
    closemsg
    trainer_battle TRAINER_LEADER_JASMINE_REMATCH, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_REMATCH_WON
    closemsg
    clearflag FLAG_GOT_TM23_FROM_JASMINE
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
