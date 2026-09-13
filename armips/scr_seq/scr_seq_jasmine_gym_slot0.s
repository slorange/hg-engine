.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Olivine Gym Jasmine — Leader talk script (scr_seq 913 slot 0).

.equ TRAINER_LEADER_JASMINE, 33

.equ VAR_MIDGAME_BADGES, 0x4134
.equ ITEM_TM023, 350

.equ SCORE_EVENT_BADGE_GET, 22

// data/text/606.txt: indices 3–4 are blank placeholders (Steelix trade text at 7+).
.equ MSG_PRE_BATTLE, 0
.equ MSG_POST_BATTLE, 1
.equ MSG_POST_BATTLE_2, 2
.equ MSG_TM_GRANT, 5
.equ MSG_ALREADY_BEATEN, 6

.if GYM_BADGE_COUNT_FIELD_REWARDS == 0
.error "Build via tools/patch_scr_seq_gym_jasmine.py (sets GYM_BADGE_COUNT_FIELD_REWARDS)"
.endif

.create "build/jasmine_gym_slot0.bin", 0

scr_seq_jasmine_gym_001:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
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
    count_badges VAR_SPECIAL_x8000
    compare VAR_SPECIAL_x8000, 3
    goto_if_ne _skip_rocket_scene
    setvar VAR_SCENE_ROCKET_TAKEOVER, 1
_skip_rocket_scene:
    buffer_players_name 0
    npc_msg MSG_POST_BATTLE_2
    wait_button
    closemsg
    play_fanfare SEQ_ME_BADGE
    wait_fanfare
.include "armips/include/gym_badge_hm_reward.inc"
_tm_grant:
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_TM_INTRO
    wait_button
    closemsg
    goto_if_no_item_space ITEM_TM023, 1, _bag_full
    play_fanfare SEQ_ME_WAZA
    wait_fanfare
    item_vars ITEM_TM023, 1
    giveitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    setflag FLAG_GOT_TM23_FROM_JASMINE
    npc_msg MSG_TM_GRANT
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
