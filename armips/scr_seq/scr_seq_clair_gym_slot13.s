.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Blackthorn Gym Clair — Leader talk script (scr_seq 943 slot 1, MAP_T30GYM0101).

.equ TRAINER_LEADER_CLAIR, 35
.equ VAR_MIDGAME_BADGES, 0x4134
.equ ITEM_TM059, 386

.equ SCORE_EVENT_BADGE_GET, 22

// data/text/631.txt — msgenc index (decode build/text/7_631; not 1-based line numbers).
.equ MSG_PRE_BATTLE, 3
.equ MSG_POST_BATTLE, 4
.equ MSG_LOSS, 5
.equ MSG_TM_FLAVOR, 7
.equ MSG_BAG_FULL, 8
.equ MSG_ALREADY_BEATEN, 9

.if GYM_BADGE_COUNT_FIELD_REWARDS == 0
.error "Build via tools/patch_scr_seq_gym_clair.py (sets GYM_BADGE_COUNT_FIELD_REWARDS)"
.endif

.create "build/clair_gym_slot13.bin", 0

scr_seq_clair_gym_leader:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
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
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_TM_INTRO
    wait_button
    closemsg
    goto_if_no_item_space ITEM_TM059, 1, _bag_full
    play_fanfare SEQ_ME_WAZA
    wait_fanfare
    item_vars ITEM_TM059, 1
    giveitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    setflag FLAG_GOT_TM59_FROM_CLAIR
    npc_msg MSG_TM_FLAVOR
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
