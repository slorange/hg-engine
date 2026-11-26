.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Cianwood Gym Chuck — Leader talk (scr_seq 877 slot 0 = script 1, MAP_T24GYM0101).
// Slot 1 is the on-transition script (level scripts 650). Do not patch it.
// VAR_TEMP_x4000 == 0 means the waterfall is still on him. VAR_UNK_4134 is the
// vanilla midgame counter (Morty, Chuck, Jasmine, Pryce). Rocket takeover is
// that counter reaching 3, not count_badges.

.equ TRAINER_LEADER_CHUCK, 34
.equ TRAINER_LEADER_CHUCK_REMATCH, 718
.equ ITEM_TM031, 358
.equ ITEM_TM008, 335
.equ ITEM_TM060, 387
.equ ITEM_TM001, 328
.equ ITEM_TM052, 379

.equ SCORE_EVENT_BADGE_GET, 22
.equ VAR_MIDGAME_BADGES, 0x4134

// data/text/574.txt. Vanilla 0–14; appended 15–23.
.equ MSG_PRE_BATTLE, 0
.equ MSG_POST_BATTLE, 3
.equ MSG_RECEIVED_BADGE, 4
.equ MSG_ALREADY_BEATEN, 8
.equ MSG_TRAINING, 9
.equ MSG_TM_CHOICE_TM31, 15
.equ MSG_TM_CHOICE_TM08, 16
.equ MSG_TM_CHOICE_TM60, 17
.equ MSG_TM_CHOICE_TM01, 18
.equ MSG_TM_CHOICE_TM52, 19
.equ MSG_REMATCH_OFFER, 20
.equ MSG_REMATCH_ACCEPT, 21
.equ MSG_REMATCH_WON, 22
.equ MSG_FAREWELL, 23

.equ BADGES_TM08, 4
.equ BADGES_TM01, 6
.equ BADGES_TM52, 8

.if GYM_BADGE_COUNT_FIELD_REWARDS == 0
.error "Build via tools/patch_scr_seq_gym_chuck.py (sets GYM_BADGE_COUNT_FIELD_REWARDS)"
.endif

.equ MSG_HINT_OFFER, 24
.equ MSG_HINT_FIRST_WILD, 25
.equ MSG_HINT_SKIP, 33
.equ MSG_HINT_LAND, 34
.equ MSG_HINT_BADGES, 41
.equ MSG_HINT_CHAMPION, 42
.equ MSG_HINT_RESEARCH, 43
.equ MSG_HINT_FOSSIL_SOURCE, 44
.equ MSG_HINT_FOSSIL_RESTORE, 45
.equ MSG_HINT_GOLDENROD, 46
.equ MSG_HINT_CELADON, 47
.equ HINT_WILD_COUNT, MSG_HINT_SKIP - MSG_HINT_FIRST_WILD
.equ HINT_SKIP, HINT_WILD_COUNT
.equ HINT_HAS_GAME_CORNER, 0
.equ HINT_HAS_RESEARCH, 1
.equ HINT_HAS_FOSSILS, 1
.equ HINT_HAS_GENERIC_PRIZES, 1
.equ NO_LIST_HIGHLIGHT, 255
.equ CMD_GYM_POKEMON_HINT, 20

.create "build/chuck_gym_slot0.bin", 0

scr_seq_chuck_gym_leader:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    compare VAR_TEMP_x4000, 0
    goto_if_eq _training
    goto_if_set FLAG_GOT_TM01_FROM_CHUCK, _rematch_offer
    CheckBadge BADGE_STORM, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _already_beaten
    npc_msg MSG_PRE_BATTLE
    closemsg
    trainer_battle TRAINER_LEADER_CHUCK, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_POST_BATTLE
    wait_button
    closemsg
    settrainerflag 156
    settrainerflag 157
    settrainerflag 251
    settrainerflag 159
    buffer_players_name 0
    npc_msg MSG_RECEIVED_BADGE
    wait_button
    closemsg
    GiveBadge BADGE_STORM
    play_fanfare SEQ_ME_BADGE
    wait_fanfare
    addvar VAR_MIDGAME_BADGES, 1
    add_special_game_stat SCORE_EVENT_BADGE_GET
    setvar VAR_UNK_4116, 1
.include "armips/include/gym_badge_hm_reward.inc"
_tm_grant:
    call _pokemon_hint
_tm_menu:
    count_badges VAR_SPECIAL_x8000
    compare VAR_SPECIAL_x8000, BADGES_TM08
    goto_if_lt _only_tm31
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_TM_CHOOSE
    touchscreen_menu_hide
    menu_init 1, 1, 0, 0, VAR_SPECIAL_RESULT
    menu_item_add MSG_TM_CHOICE_TM31, 255, 0
    menu_item_add MSG_TM_CHOICE_TM08, 255, 1
    menu_item_add MSG_TM_CHOICE_TM60, 255, 2
    compare VAR_SPECIAL_x8000, BADGES_TM01
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM01, 255, 3
    compare VAR_SPECIAL_x8000, BADGES_TM52
    goto_if_lt _menu_show
    menu_item_add MSG_TM_CHOICE_TM52, 255, 4
_menu_show:
    menu_exec
    touchscreen_menu_show
    closemsg
    switch VAR_SPECIAL_RESULT
    case 0, _pick_tm31
    case 1, _pick_tm08
    case 2, _pick_tm60
    case 3, _pick_tm01
    case 4, _pick_tm52
    goto _only_tm31

_only_tm31:
_pick_tm31:
    setvar VAR_SPECIAL_x8004, ITEM_TM031
    goto _give_tm
_pick_tm08:
    setvar VAR_SPECIAL_x8004, ITEM_TM008
    goto _give_tm
_pick_tm60:
    setvar VAR_SPECIAL_x8004, ITEM_TM060
    goto _give_tm
_pick_tm01:
    setvar VAR_SPECIAL_x8004, ITEM_TM001
    goto _give_tm
_pick_tm52:
    setvar VAR_SPECIAL_x8004, ITEM_TM052

_give_tm:
    setvar VAR_SPECIAL_x8005, 1
    hasspaceforitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _bag_full
    callstd std_give_item_verbose
    setflag FLAG_GOT_TM01_FROM_CHUCK
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
    goto_if_unset FLAG_GOT_TM01_FROM_CHUCK, _tm_menu
_rematch_offer:
    npc_msg MSG_REMATCH_OFFER
    yesno VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _rematch_declined
    npc_msg MSG_REMATCH_ACCEPT
    closemsg
    trainer_battle TRAINER_LEADER_CHUCK_REMATCH, 0, 0, 0
    check_battle_won VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _white_out
    lockall
    faceplayer
    npc_msg MSG_REMATCH_WON
    closemsg
    clearflag FLAG_GOT_TM01_FROM_CHUCK
    goto _tm_grant

_rematch_declined:
    npc_msg MSG_ALREADY_BEATEN
    wait_button
    closemsg
    releaseall
    end

_training:
    npc_msg MSG_TRAINING
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
