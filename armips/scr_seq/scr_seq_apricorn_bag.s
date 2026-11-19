.nds
.thumb
.include "armips/include/scriptmacros.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

// Standard Apricorn-tree script, shared by all maps. Text bank 23.
.create "build/a012/2_150", 0
    scrdef _tree
    scrdef_end
_tree:
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    npc_msg 0
    closemsg
    RunNewCommand 9, 0
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _empty
    compare VAR_SPECIAL_RESULT, 2
    goto_if_eq _full
    anim_apricorn_tree VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _empty
    giveitem VAR_SPECIAL_x8004, 1, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _full
    add_special_game_stat 1 // SCORE_EVENT_APRICORN_HARVESTED
    buffer_players_name 0
    buffer_apricorn_name 1, VAR_SPECIAL_x8000
    play_fanfare SEQ_ME_ITEM
    npc_msg 1
    wait_fanfare
    goto _finish
_empty:
    npc_msg 2
    goto _finish
_full:
    npc_msg 3
_finish:
    wait_button
    closemsg
    releaseall
    end
    .align 4
.close

// Route 30 house. Use the existing colour tip in text bank 376.
.create "build/a012/2_228", 0
    scrdef _collector
    scrdef_end
_collector:
    simple_npc_msg 3
    end
    .align 4
.close
