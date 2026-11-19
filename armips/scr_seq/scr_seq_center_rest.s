.nds
.thumb
.include "armips/include/scriptmacros.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

.create "build/center_rest.bin", 0
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    npc_msg 38
    touchscreen_menu_hide
    menu_init 1, 1, 0, 1, VAR_SPECIAL_RESULT
    menu_item_add 39, 255, 0
    menu_item_add 40, 255, 1
    menu_item_add 41, 255, 2
    menu_item_add 42, 255, 3
    menu_exec
    touchscreen_menu_show
    closemsg
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _morning
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _day
    compare VAR_SPECIAL_RESULT, 2
    goto_if_eq _night
    npc_msg 44
    goto _finish
_morning:
    setvar VAR_SPECIAL_x8000, 4
    goto _rest
_day:
    setvar VAR_SPECIAL_x8000, 10
    goto _rest
_night:
    setvar VAR_SPECIAL_x8000, 20
_rest:
    fade_screen 6, 1, 0, RGB_BLACK
    wait_fade
    RunNewCommand 7, VAR_SPECIAL_x8000
    wait 30, VAR_SPECIAL_x8002
    fade_screen 6, 1, 1, RGB_BLACK
    wait_fade
    compare VAR_SPECIAL_RESULT, 1
    goto_if_ne _unavailable
    npc_msg 43
    goto _finish
_unavailable:
    npc_msg 45
_finish:
    wait_button_or_walk_away
    closemsg
    releaseall
    end
.close
