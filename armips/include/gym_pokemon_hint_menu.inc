_pokemon_hint:
    touchscreen_menu_hide
    npc_msg MSG_HINT_OFFER
    ListLocalText 1, 1, 0, 0, VAR_SPECIAL_x8002
    setvar VAR_SPECIAL_x8003, 0
    setvar VAR_SPECIAL_x8004, MSG_HINT_FIRST_WILD
_add_wild_hint:
    RunNewCommand CMD_GYM_POKEMON_HINT, VAR_SPECIAL_x8003
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _next_wild_hint
    AddListOption VAR_SPECIAL_x8004, NO_LIST_HIGHLIGHT, VAR_SPECIAL_x8003
_next_wild_hint:
    addvar VAR_SPECIAL_x8003, 1
    addvar VAR_SPECIAL_x8004, 1
    compare VAR_SPECIAL_x8003, HINT_WILD_COUNT
    goto_if_lt _add_wild_hint
.if HINT_HAS_GAME_CORNER
    AddListOption MSG_HINT_ROTOM, NO_LIST_HIGHLIGHT, HINT_WILD_COUNT
.endif
    AddListOption MSG_HINT_SKIP, NO_LIST_HIGHLIGHT, HINT_SKIP
    ShowList
    closemsg
    touchscreen_menu_show
    compare VAR_SPECIAL_x8002, HINT_WILD_COUNT
.if HINT_HAS_GAME_CORNER
    goto_if_eq _hint_rotom
    goto_if_gt _hint_done
.else
    goto_if_ge _hint_done
.endif
    RunNewCommand CMD_GYM_POKEMON_HINT, VAR_SPECIAL_x8002
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _hint_done
    buffer_species_name 0, VAR_SPECIAL_x8005, 0, 0
.if HINT_HAS_RESEARCH
    compare VAR_SPECIAL_RESULT, 8
    goto_if_eq _hint_research
.if HINT_HAS_FOSSILS
    compare VAR_SPECIAL_RESULT, 9
    goto_if_eq _hint_fossil
.endif
.endif
.if HINT_HAS_GENERIC_PRIZES
    compare VAR_SPECIAL_RESULT, 10
    goto_if_eq _hint_goldenrod
    compare VAR_SPECIAL_RESULT, 11
    goto_if_eq _hint_celadon
.endif
    buffer_map_sec_name 1, VAR_SPECIAL_x8000
    addvar VAR_SPECIAL_RESULT, MSG_HINT_LAND - 1
    npc_msg_var VAR_SPECIAL_RESULT
    wait_button
    closemsg
    compare VAR_SPECIAL_x8001, 0
    goto_if_eq _hint_done
    compare VAR_SPECIAL_x8001, 17
    goto_if_eq _hint_champion
    buffer_int 0, VAR_SPECIAL_x8001
    npc_msg MSG_HINT_BADGES
    goto _hint_close
_hint_champion:
    npc_msg MSG_HINT_CHAMPION
    goto _hint_close
.if HINT_HAS_GAME_CORNER
_hint_rotom:
    npc_msg MSG_HINT_GAME_CORNER
    goto _hint_close
.endif
.if HINT_HAS_RESEARCH
_hint_research:
    npc_msg MSG_HINT_RESEARCH
    goto _hint_close
.if HINT_HAS_FOSSILS
_hint_fossil:
    buffer_item_name 1, VAR_SPECIAL_x8000
    npc_msg MSG_HINT_FOSSIL_SOURCE
    wait_button
    closemsg
    npc_msg MSG_HINT_FOSSIL_RESTORE
    goto _hint_close
.endif
.endif
.if HINT_HAS_GENERIC_PRIZES
_hint_goldenrod:
    npc_msg MSG_HINT_GOLDENROD
    goto _hint_close
_hint_celadon:
    npc_msg MSG_HINT_CELADON
.endif
_hint_close:
    wait_button
    closemsg
_hint_done:
    return

