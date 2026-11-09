.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Pewter Gym Brock — Leader talk script (scr_seq 752 slot 0 = script 1, MAP_T03GYM0101).

.equ TRAINER_LEADER_BROCK, 253
.equ ITEM_TM080, 407

.equ SCORE_EVENT_BADGE_GET, 22
.equ TRAINER_PEWTER_GYM_1, 308
.equ TRAINER_PEWTER_GYM_2, 685

// data/text 462 (msgenc index).
.equ MSG_PRE_BATTLE, 0
.equ MSG_POST_BATTLE, 1
.equ MSG_RECEIVED_BADGE, 2
.equ MSG_TM_FLAVOR_M, 3
.equ MSG_TM_FLAVOR_F, 4
.equ MSG_ALREADY_BEATEN, 5

.if GYM_BADGE_COUNT_FIELD_REWARDS == 0
.error "Build via tools/patch_scr_seq_gym_brock.py (sets GYM_BADGE_COUNT_FIELD_REWARDS)"
.endif

.create "build/brock_gym_slot0.bin", 0

scr_seq_brock_gym_leader:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
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
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_TM_INTRO
    wait_button
    closemsg
    goto_if_no_item_space ITEM_TM080, 1, _bag_full
    play_fanfare SEQ_ME_WAZA
    wait_fanfare
    item_vars ITEM_TM080, 1
    giveitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    setflag FLAG_GOT_TM80_FROM_BROCK
    buffer_players_name 0
    gender_msgbox MSG_TM_FLAVOR_M, MSG_TM_FLAVOR_F
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
