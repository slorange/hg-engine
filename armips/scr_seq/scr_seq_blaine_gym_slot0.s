.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Cinnabar cave gym Blaine — Leader talk (scr_seq 15 slot 0 = script 1, MAP_D11R0106).
// Level scripts 276 reference scripts 9 and 10 (slots 8 and 9). Do not patch them.

.equ TRAINER_LEADER_BLAINE, 259
.equ TRAINER_LEADER_BLAINE_REMATCH, 726
.equ ITEM_TM011, 338
.equ ITEM_TM061, 388
.equ ITEM_TM038, 365
.equ ITEM_TM050, 377
.equ ITEM_TM035, 362

.equ SCORE_EVENT_BADGE_GET, 22

// data/text 53 (msgenc index). Vanilla 0–25; appended 26–34.
.equ MSG_PRE_BATTLE, 0
.equ MSG_POST_BATTLE, 1
.equ MSG_RECEIVED_BADGE, 2
.equ MSG_ALREADY_BEATEN, 5
.equ MSG_TM_CHOICE_TM11, 26
.equ MSG_TM_CHOICE_TM61, 27
.equ MSG_TM_CHOICE_TM38, 28
.equ MSG_TM_CHOICE_TM50, 29
.equ MSG_TM_CHOICE_TM35, 30
.equ MSG_REMATCH_OFFER, 31
.equ MSG_REMATCH_ACCEPT, 32
.equ MSG_REMATCH_WON, 33
.equ MSG_FAREWELL, 34

.equ BADGES_TM61, 2
.equ BADGES_TM38, 8
.equ BADGES_TM35, 10

.if GYM_BADGE_COUNT_FIELD_REWARDS == 0
.error "Build via tools/patch_scr_seq_gym_blaine.py (sets GYM_BADGE_COUNT_FIELD_REWARDS)"
.endif

.create "build/blaine_gym_slot0.bin", 0

scr_seq_blaine_gym_leader:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    goto_if_set FLAG_GOT_TM50_FROM_BLAINE, _rematch_offer
    CheckBadge BADGE_VOLCANO, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _already_beaten
    npc_msg MSG_PRE_BATTLE
    closemsg
    trainer_battle TRAINER_LEADER_BLAINE, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_POST_BATTLE
    wait_button
    closemsg
    GiveBadge BADGE_VOLCANO
    addvar VAR_UNK_4135, 1
    setflag 613
    setflag 665
    clearflag 666
    add_special_game_stat SCORE_EVENT_BADGE_GET
    setflag 319
    setflag 320
    setflag 316
    buffer_players_name 0
    npc_msg MSG_RECEIVED_BADGE
    wait_button
    closemsg
    play_fanfare SEQ_ME_BADGE
    wait_fanfare
.include "armips/include/gym_badge_hm_reward.inc"
_tm_grant:
    count_badges VAR_SPECIAL_x8000
    compare VAR_SPECIAL_x8000, BADGES_TM61
    goto_if_lt _only_tm11
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_TM_CHOOSE
    touchscreen_menu_hide
    menu_init 1, 1, 0, 0, VAR_SPECIAL_RESULT
    menu_item_add MSG_TM_CHOICE_TM11, 255, 0
    menu_item_add MSG_TM_CHOICE_TM61, 255, 1
    compare VAR_SPECIAL_x8000, BADGES_TM38
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM38, 255, 2
    menu_item_add MSG_TM_CHOICE_TM50, 255, 3
    compare VAR_SPECIAL_x8000, BADGES_TM35
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM35, 255, 4
_menu_show:
    menu_exec
    touchscreen_menu_show
    closemsg
    switch VAR_SPECIAL_RESULT
    case 0, _pick_tm11
    case 1, _pick_tm61
    case 2, _pick_tm38
    case 3, _pick_tm50
    case 4, _pick_tm35
    goto _only_tm11

_only_tm11:
_pick_tm11:
    setvar VAR_SPECIAL_x8004, ITEM_TM011
    goto _give_tm
_pick_tm61:
    setvar VAR_SPECIAL_x8004, ITEM_TM061
    goto _give_tm
_pick_tm38:
    setvar VAR_SPECIAL_x8004, ITEM_TM038
    goto _give_tm
_pick_tm50:
    setvar VAR_SPECIAL_x8004, ITEM_TM050
    goto _give_tm
_pick_tm35:
    setvar VAR_SPECIAL_x8004, ITEM_TM035

_give_tm:
    setvar VAR_SPECIAL_x8005, 1
    hasspaceforitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _bag_full
    callstd std_give_item_verbose
    setflag FLAG_GOT_TM50_FROM_BLAINE
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
    goto_if_unset FLAG_GOT_TM50_FROM_BLAINE, _tm_grant
_rematch_offer:
    npc_msg MSG_REMATCH_OFFER
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _rematch_declined
    npc_msg MSG_REMATCH_ACCEPT
    closemsg
    trainer_battle TRAINER_LEADER_BLAINE_REMATCH, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_REMATCH_WON
    closemsg
    clearflag FLAG_GOT_TM50_FROM_BLAINE
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
