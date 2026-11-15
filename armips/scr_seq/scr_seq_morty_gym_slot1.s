.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Ecruteak Gym Morty — Leader talk script (scr_seq 922 slot 1).

.equ TRAINER_LEADER_MORTY, 31
.equ TRAINER_LEADER_MORTY_REMATCH, 715
.equ VAR_MIDGAME_BADGES, 0x4134

.equ ITEM_TM056, 383
.equ ITEM_TM066, 393
.equ ITEM_TM065, 392
.equ ITEM_TM030, 357
.equ ITEM_TM079, 406

.equ SCORE_EVENT_BADGE_GET, 22

// data/text/614.txt uses a blank line between each vanilla entry (msgenc index = line/2).
// Appended choice lines are compact: index 20 is the first new line.
.equ MSG_PRE_BATTLE, 0
.equ MSG_POST_BATTLE, 2
.equ MSG_POST_BATTLE_2, 4
.equ MSG_ALREADY_BEATEN, 8
.equ MSG_TM_CHOICE_TM56, 20
.equ MSG_TM_CHOICE_TM66, 21
.equ MSG_TM_CHOICE_TM65, 22
.equ MSG_TM_CHOICE_TM30, 23
.equ MSG_TM_CHOICE_TM79, 24
.equ MSG_REMATCH_OFFER, 25
.equ MSG_REMATCH_ACCEPT, 26
.equ MSG_REMATCH_WON, 27
.equ MSG_FAREWELL, 28

.equ BADGES_TM65, 2
.equ BADGES_TM30, 6

.if GYM_BADGE_COUNT_FIELD_REWARDS == 0
.error "Build via tools/patch_scr_seq_gym_morty.py (sets GYM_BADGE_COUNT_FIELD_REWARDS)"
.endif

.create "build/morty_gym_slot1.bin", 0

scr_seq_morty_gym_001:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    goto_if_set FLAG_GOT_TM30_FROM_MORTY, _rematch_offer
    CheckBadge BADGE_FOG, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _already_beaten
    npc_msg MSG_PRE_BATTLE
    closemsg
    trainer_battle TRAINER_LEADER_MORTY, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_POST_BATTLE
    wait_button
    closemsg
    givebadge BADGE_FOG
    addvar VAR_MIDGAME_BADGES, 1
    add_special_game_stat SCORE_EVENT_BADGE_GET
    setflag FLAG_UNK_998
    buffer_players_name 0
    npc_msg MSG_POST_BATTLE_2
    wait_button
    closemsg
    play_fanfare SEQ_ME_BADGE
    wait_fanfare
.include "armips/include/gym_badge_hm_reward.inc"
_tm_grant:
    // Fling and Payback are both unlocked at 0 badges, so the menu always opens.
    count_badges VAR_SPECIAL_x8000
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_TM_CHOOSE
    touchscreen_menu_hide
    menu_init 1, 1, 0, 0, VAR_SPECIAL_RESULT
    menu_item_add MSG_TM_CHOICE_TM56, 255, 0
    menu_item_add MSG_TM_CHOICE_TM66, 255, 1
    compare VAR_SPECIAL_x8000, BADGES_TM65
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM65, 255, 2
    compare VAR_SPECIAL_x8000, BADGES_TM30
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM30, 255, 3
    menu_item_add MSG_TM_CHOICE_TM79, 255, 4
_menu_show:
    menu_exec
    touchscreen_menu_show
    closemsg
    switch VAR_SPECIAL_RESULT
    case 0, _pick_tm56
    case 1, _pick_tm66
    case 2, _pick_tm65
    case 3, _pick_tm30
    case 4, _pick_tm79
    goto _pick_tm56

_pick_tm56:
    setvar VAR_SPECIAL_x8004, ITEM_TM056
    goto _give_tm
_pick_tm66:
    setvar VAR_SPECIAL_x8004, ITEM_TM066
    goto _give_tm
_pick_tm65:
    setvar VAR_SPECIAL_x8004, ITEM_TM065
    goto _give_tm
_pick_tm30:
    setvar VAR_SPECIAL_x8004, ITEM_TM030
    goto _give_tm
_pick_tm79:
    setvar VAR_SPECIAL_x8004, ITEM_TM079

_give_tm:
    setvar VAR_SPECIAL_x8005, 1
    hasspaceforitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _bag_full
    callstd std_give_item_verbose
    setflag FLAG_GOT_TM30_FROM_MORTY
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
    goto_if_unset FLAG_GOT_TM30_FROM_MORTY, _tm_grant
_rematch_offer:
    npc_msg MSG_REMATCH_OFFER
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _rematch_declined
    npc_msg MSG_REMATCH_ACCEPT
    closemsg
    trainer_battle TRAINER_LEADER_MORTY_REMATCH, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_REMATCH_WON
    closemsg
    clearflag FLAG_GOT_TM30_FROM_MORTY
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
