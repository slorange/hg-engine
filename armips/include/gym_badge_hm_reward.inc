// Shared post-badge level cap + badge-count HM grant (World-3 table, no Flash/Headbutt).
// Include after badge fanfare; leader script must define label _tm_grant immediately after.
//
// Text: data/text/854.txt

.equ MSG_BANK_GYM_REWARDS, 854

.equ MSG_GYM_LEVEL_CAP, 0
.equ MSG_GYM_HM01_CUT, 1
.equ MSG_GYM_HM06_ROCK_SMASH, 2
.equ MSG_GYM_HM02_FLY, 3
.equ MSG_GYM_HM03_SURF, 4
.equ MSG_GYM_HM04_STRENGTH, 5
.equ MSG_GYM_HM05_WHIRLPOOL, 6
.equ MSG_GYM_HM07_WATERFALL, 7
.equ MSG_GYM_HM08_ROCK_CLIMB, 8
.equ MSG_GYM_TM_INTRO, 9

.equ ITEM_HM01, 420
.equ ITEM_HM02, 421
.equ ITEM_HM03, 422
.equ ITEM_HM04, 423
.equ ITEM_HM05, 424
.equ ITEM_HM06, 425
.equ ITEM_HM07, 426
.equ ITEM_HM08, 427

// --- level cap (10 + 4 * badges; 80 at 16) ---
    count_badges VAR_SPECIAL_x8000
    compare VAR_SPECIAL_x8000, 16
    goto_if_eq _gym_cap80
    setvar VAR_SPECIAL_x8001, 10
    setvar VAR_SPECIAL_x8002, 0
_gym_cap_loop:
    compare VAR_SPECIAL_x8002, VAR_SPECIAL_x8000
    goto_if_eq _gym_cap_show
    addvar VAR_SPECIAL_x8001, 4
    addvar VAR_SPECIAL_x8002, 1
    goto _gym_cap_loop
_gym_cap80:
    setvar VAR_SPECIAL_x8001, 80
_gym_cap_show:
    TextNumber 0, VAR_SPECIAL_x8001
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_LEVEL_CAP
    wait_button
    closemsg

// --- HM by total badge count (after this badge) ---
    count_badges VAR_SPECIAL_x8000
    compare VAR_SPECIAL_x8000, 2
    goto_if_eq _gym_hm_b2
    compare VAR_SPECIAL_x8000, 3
    goto_if_eq _gym_hm_b3
    compare VAR_SPECIAL_x8000, 5
    goto_if_eq _gym_hm_b5
    compare VAR_SPECIAL_x8000, 6
    goto_if_eq _gym_hm_b6
    compare VAR_SPECIAL_x8000, 7
    goto_if_eq _gym_hm_b7
    compare VAR_SPECIAL_x8000, 10
    goto_if_eq _gym_hm_b10
    compare VAR_SPECIAL_x8000, 13
    goto_if_eq _gym_hm_b13
    compare VAR_SPECIAL_x8000, 16
    goto_if_eq _gym_hm_b16
    goto _tm_grant

_gym_hm_b2:
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_HM01_CUT
    wait_button
    closemsg
    goto_if_no_item_space ITEM_HM01, 1, _tm_grant
    play_fanfare SEQ_ME_WAZA
    wait_fanfare
    item_vars ITEM_HM01, 1
    giveitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    setflag FLAG_GOT_HM01
    goto _tm_grant

_gym_hm_b3:
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_HM06_ROCK_SMASH
    wait_button
    closemsg
    goto_if_no_item_space ITEM_HM06, 1, _tm_grant
    play_fanfare SEQ_ME_WAZA
    wait_fanfare
    item_vars ITEM_HM06, 1
    giveitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    goto _tm_grant

_gym_hm_b5:
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_HM02_FLY
    wait_button
    closemsg
    goto_if_no_item_space ITEM_HM02, 1, _tm_grant
    play_fanfare SEQ_ME_WAZA
    wait_fanfare
    item_vars ITEM_HM02, 1
    giveitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    setflag FLAG_GOT_HM02
    goto _tm_grant

_gym_hm_b6:
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_HM03_SURF
    wait_button
    closemsg
    goto_if_no_item_space ITEM_HM03, 1, _tm_grant
    play_fanfare SEQ_ME_WAZA
    wait_fanfare
    item_vars ITEM_HM03, 1
    giveitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    setflag FLAG_GOT_HM03
    goto _tm_grant

_gym_hm_b7:
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_HM04_STRENGTH
    wait_button
    closemsg
    goto_if_no_item_space ITEM_HM04, 1, _tm_grant
    play_fanfare SEQ_ME_WAZA
    wait_fanfare
    item_vars ITEM_HM04, 1
    giveitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    goto _tm_grant

_gym_hm_b10:
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_HM05_WHIRLPOOL
    wait_button
    closemsg
    goto_if_no_item_space ITEM_HM05, 1, _tm_grant
    play_fanfare SEQ_ME_WAZA
    wait_fanfare
    item_vars ITEM_HM05, 1
    giveitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    goto _tm_grant

_gym_hm_b13:
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_HM07_WATERFALL
    wait_button
    closemsg
    goto_if_no_item_space ITEM_HM07, 1, _tm_grant
    play_fanfare SEQ_ME_WAZA
    wait_fanfare
    item_vars ITEM_HM07, 1
    giveitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    goto _tm_grant

_gym_hm_b16:
    non_npc_msg_extern MSG_BANK_GYM_REWARDS, MSG_GYM_HM08_ROCK_CLIMB
    wait_button
    closemsg
    goto_if_no_item_space ITEM_HM08, 1, _tm_grant
    play_fanfare SEQ_ME_WAZA
    wait_fanfare
    item_vars ITEM_HM08, 1
    giveitem VAR_SPECIAL_x8004, VAR_SPECIAL_x8005, VAR_SPECIAL_RESULT
    setflag FLAG_GOT_HM08
    goto _tm_grant
