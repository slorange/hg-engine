.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Blackthorn Gym Clair — Leader talk script (scr_seq 943 slot 0 = script 1, MAP_T30GYM0101).

.equ TRAINER_LEADER_CLAIR, 35
.equ TRAINER_LEADER_CLAIR_REMATCH, 719
.equ VAR_MIDGAME_BADGES, 0x4134
.equ ITEM_TM002, 329
.equ ITEM_TM059, 386

.equ SCORE_EVENT_BADGE_GET, 22

// data/text/631.txt — msgenc index (decode build/text/7_631; not 1-based line numbers).
// Appended choice lines start at 14.
.equ MSG_PRE_BATTLE, 3
.equ MSG_POST_BATTLE, 4
.equ MSG_LOSS, 5
.equ MSG_ALREADY_BEATEN, 9
.equ MSG_TM_CHOICE_TM02, 14
.equ MSG_TM_CHOICE_TM59, 15
.equ MSG_REMATCH_OFFER, 16
.equ MSG_REMATCH_ACCEPT, 17
.equ MSG_REMATCH_WON, 18
.equ MSG_FAREWELL, 19

.equ BADGES_TM59, 8

.if GYM_BADGE_COUNT_FIELD_REWARDS == 0
.error "Build via tools/patch_scr_seq_gym_clair.py (sets GYM_BADGE_COUNT_FIELD_REWARDS)"
.endif

.create "build/clair_gym_slot13.bin", 0

scr_seq_clair_gym_leader:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    goto_if_set FLAG_GOT_TM59_FROM_CLAIR, _rematch_offer
    CheckBadge BADGE_RISING, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _already_beaten
    npc_msg MSG_PRE_BATTLE
    closemsg
    trainer_battle TRAINER_LEADER_CLAIR, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_POST_BATTLE
    wait_button
    closemsg
    GiveJohtoBadgeOpenWorld BADGE_RISING
    addvar VAR_MIDGAME_BADGES, 1
    add_special_game_stat SCORE_EVENT_BADGE_GET
    play_fanfare SEQ_ME_BADGE
    wait_fanfare
.include "armips/include/gym_badge_hm_reward.inc"
_tm_grant:
    count_badges VAR_SPECIAL_x8000
    compare VAR_SPECIAL_x8000, BADGES_TM59
    goto_if_lt _only_tm02
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_TM_CHOOSE
    touchscreen_menu_hide
    menu_init 1, 1, 0, 0, VAR_SPECIAL_RESULT
    menu_item_add MSG_TM_CHOICE_TM02, 255, 0
    menu_item_add MSG_TM_CHOICE_TM59, 255, 1
_menu_show:
    menu_exec
    touchscreen_menu_show
    closemsg
    switch VAR_SPECIAL_RESULT
    case 0, _pick_tm02
    case 1, _pick_tm59
    goto _only_tm02

_only_tm02:
_pick_tm02:
    setvar VAR_SPECIAL_x8004, ITEM_TM002
    goto _give_tm
_pick_tm59:
    setvar VAR_SPECIAL_x8004, ITEM_TM059

_give_tm:
    setvar VAR_SPECIAL_x8005, 1
    hasspaceforitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _bag_full
    callstd std_give_item_verbose
    setflag FLAG_GOT_TM59_FROM_CLAIR
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
    goto_if_unset FLAG_GOT_TM59_FROM_CLAIR, _tm_grant
_rematch_offer:
    npc_msg MSG_REMATCH_OFFER
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _rematch_declined
    npc_msg MSG_REMATCH_ACCEPT
    closemsg
    trainer_battle TRAINER_LEADER_CLAIR_REMATCH, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_REMATCH_WON
    closemsg
    clearflag FLAG_GOT_TM59_FROM_CLAIR
    goto _tm_grant

_rematch_declined:
    npc_msg MSG_ALREADY_BEATEN
    wait_button
    closemsg
    releaseall
    end

_white_out:
    lockall
    faceplayer
    npc_msg MSG_LOSS
    wait_button
    closemsg
    white_out
    releaseall
    end

.close
