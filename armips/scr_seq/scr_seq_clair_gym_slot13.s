.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
// Blackthorn Gym Clair — dedicated Leader talk script (scr_seq 938 slot 13).

.equ TRAINER_LEADER_CLAIR, 35
.equ VAR_MIDGAME_BADGES, 0x4134
.equ SCORE_EVENT_BADGE_GET, 22

// data/text/631.txt — one msgenc index per line.
.equ MSG_PRE_BATTLE, 3
.equ MSG_POST_BATTLE, 5
.equ MSG_LEAGUE_OBEDIENCE, 14
.equ MSG_ALREADY_BEATEN, 10

.create "build/clair_gym_slot13.bin", 0

scr_seq_clair_gym_leader:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    CheckBadge BADGE_RISING, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _already_beaten
    npc_msg MSG_PRE_BATTLE
    wait_button
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
    play_fanfare SEQ_ME_BADGE
    wait_fanfare
    GiveJohtoBadgeOpenWorld BADGE_RISING
    addvar VAR_MIDGAME_BADGES, 1
    add_special_game_stat SCORE_EVENT_BADGE_GET
    npc_msg MSG_LEAGUE_OBEDIENCE
    wait_button
    closemsg
    releaseall
    end

_already_beaten:
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
