.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

.equ ITEM_SS_TICKET, 456
.equ ITEM_PASS, 480
.equ ITEM_APRICORN_BOX, 468
.equ ITEM_HM02, 421

.equ MSG_MOM_GREET_M, 0
.equ MSG_MOM_GREET_F, 1
.equ MSG_CITY_PROMPT, 2
.equ MSG_MENU_NEW_BARK, 3
.equ MSG_MENU_GOLDENROD, 4
.equ MSG_MENU_SAFFRON, 5
.equ MSG_STARTER_PROMPT, 6
.equ MSG_LIST_HIGHLIGHT, 254
.equ MSG_MENU_CHIKORITA, 7
.equ MSG_MENU_CYNDAQUIL, 8
.equ MSG_MENU_TOTODILE, 9
.equ MSG_MENU_BULBASAUR, 10
.equ MSG_MENU_CHARMANDER, 11
.equ MSG_MENU_SQUIRTLE, 12
.equ MSG_MENU_TREECKO, 13
.equ MSG_MENU_TORCHIC, 14
.equ MSG_MENU_MUDKIP, 15
.equ MSG_MENU_TURTWIG, 16
.equ MSG_MENU_CHIMCHAR, 17
.equ MSG_MENU_PIPLUP, 18

.equ SPECIES_CHIKORITA, 152
.equ SPECIES_CYNDAQUIL, 155
.equ SPECIES_TOTODILE, 158
.equ SPECIES_BULBASAUR, 1
.equ SPECIES_CHARMANDER, 4
.equ SPECIES_SQUIRTLE, 7
.equ SPECIES_TREECKO, 252
.equ SPECIES_TORCHIC, 255
.equ SPECIES_MUDKIP, 258
.equ SPECIES_TURTWIG, 387
.equ SPECIES_CHIMCHAR, 390
.equ SPECIES_PIPLUP, 393

.equ OBJ_MOM, 0

.equ MAP_T20, 60
.equ MAP_T25, 76
.equ MAP_T11, 59

.equ START_CITY_NEW_BARK, 0
.equ START_CITY_GOLDENROD, 1
.equ START_CITY_SAFFRON, 2

.equ NB_HOME_WARP, 1
.equ GD_HOME_WARP, 14
.equ SF_HOME_WARP, 14

.create "build/t20_mom_script0.bin", 0
    scrcmd_609
    lockall
    compare VAR_SCENE_PLAYERS_HOUSE_1F, 0
    goto_if_ne _already_done
    setvar VAR_SCENE_PLAYERS_HOUSE_1F, 1
    apply_movement obj_player, _mv_player_down
    apply_movement OBJ_MOM, _mv_mom_spot
    wait_movement
    call _openworld_pick_city
    goto_if_set FLAG_GOT_STARTER, _mom_begin
    call _openworld_pick_starter
_mom_begin:
    lockall
    callstd std_play_mom_music
    wait 30, VAR_SPECIAL_RESULT
    apply_movement OBJ_MOM, _mv_mom_approach
    wait_movement
    buffer_players_name 0
    gender_msgbox MSG_MOM_GREET_M, MSG_MOM_GREET_F
    closemsg
    // Menu / UI unlocks first (touch screen, Pokédex, Pokégear — no item prompts)
    setflag FLAG_GOT_BAG
    play_fanfare SEQ_SE_PL_KIRAKIRA
    wait_fanfare
    setflag FLAG_GOT_TRAINER_CARD
    play_fanfare SEQ_SE_PL_KIRAKIRA
    wait_fanfare
    setflag FLAG_GOT_SAVE_BUTTON
    play_fanfare SEQ_SE_PL_KIRAKIRA
    wait_fanfare
    setflag FLAG_GOT_OPTIONS_BUTTON
    play_fanfare SEQ_SE_PL_KIRAKIRA
    wait_fanfare
    give_running_shoes
    setflag FLAG_GOT_POKEDEX
    GivePokedex
    setflag FLAG_GOT_POKEGEAR
    play_fanfare SEQ_ME_ITEM
    wait_fanfare
    UpgradePokegear 1
    play_fanfare SEQ_ME_POKEGEAR_REGIST
    wait_fanfare
    register_gear_number PHONE_CONTACT_MOTHER
    register_gear_number PHONE_CONTACT_PROF__ELM
    register_gear_number PHONE_CONTACT_PROF__OAK
    // Key items last (each uses std_give_item_verbose — waits for A)
    giveitem_no_check ITEM_SS_TICKET, 1
    giveitem_no_check ITEM_PASS, 1
    giveitem_no_check ITEM_APRICORN_BOX, 1
    setflag FLAG_GOT_APRICORN_BOX
.if OPENWORLD_TESTING_GRANTS == 1
    giveitem_no_check ITEM_HM02, 1
.endif
    closemsg
    apply_movement OBJ_MOM, _mv_mom_return
    wait_movement
    callstd std_fade_end_mom_music
_already_done:
    releaseall
    end

.align 4

_mv_player_down:
    step 0x003E, 1
    step 0x0021, 1
    step_end

_mv_mom_spot:
    step 0x0020, 1
    step_end

_mv_mom_approach:
    step WalkUpFast, 2
    step WalkLeftFast, 3
    step WalkUpFast, 1
    step_end

_mv_mom_return:
    step 0x0021, 1
    step WalkDownFast, 3
    step WalkRightFast, 3
    step 0x0020, 1
    step_end

_openworld_pick_city:
    touchscreen_menu_hide
    npc_msg MSG_CITY_PROMPT
    ListLocalText 1, 1, 0, 0, VAR_SPECIAL_RESULT
    AddListOption MSG_MENU_NEW_BARK, MSG_LIST_HIGHLIGHT, 0
    AddListOption MSG_MENU_GOLDENROD, MSG_LIST_HIGHLIGHT, 1
    AddListOption MSG_MENU_SAFFRON, MSG_LIST_HIGHLIGHT, 2
    ShowList
    closemsg
    copyvar VAR_PLAYER_START_CITY, VAR_SPECIAL_RESULT
    call _set_home_dynamic_warp
    touchscreen_menu_show
    return

_set_home_dynamic_warp:
    compare VAR_PLAYER_START_CITY, START_CITY_NEW_BARK
    goto_if_eq _dyn_new_bark
    compare VAR_PLAYER_START_CITY, START_CITY_GOLDENROD
    goto_if_eq _dyn_goldenrod
    setvar VAR_TEMP_x4000, MAP_T11
    setvar VAR_TEMP_x4001, SF_HOME_WARP
    setvar VAR_TEMP_x4002, 0
    setvar VAR_TEMP_x4003, 0
    setvar VAR_TEMP_x4004, DIR_NORTH
    set_dynamic_warp VAR_TEMP_x4000, VAR_TEMP_x4001, VAR_TEMP_x4002, VAR_TEMP_x4003, VAR_TEMP_x4004
    return
_dyn_goldenrod:
    setvar VAR_TEMP_x4000, MAP_T25
    setvar VAR_TEMP_x4001, GD_HOME_WARP
    setvar VAR_TEMP_x4002, 0
    setvar VAR_TEMP_x4003, 0
    setvar VAR_TEMP_x4004, DIR_NORTH
    set_dynamic_warp VAR_TEMP_x4000, VAR_TEMP_x4001, VAR_TEMP_x4002, VAR_TEMP_x4003, VAR_TEMP_x4004
    return
_dyn_new_bark:
    setvar VAR_TEMP_x4000, MAP_T20
    setvar VAR_TEMP_x4001, NB_HOME_WARP
    setvar VAR_TEMP_x4002, 0
    setvar VAR_TEMP_x4003, 0
    setvar VAR_TEMP_x4004, DIR_NORTH
    set_dynamic_warp VAR_TEMP_x4000, VAR_TEMP_x4001, VAR_TEMP_x4002, VAR_TEMP_x4003, VAR_TEMP_x4004
    return

_openworld_pick_starter:
    touchscreen_menu_hide
    npc_msg MSG_STARTER_PROMPT
    // Touch menu (menu_init/menu_item_add) supports at most 6 boxes (slots 0–5).
    // ListLocalText supports 12+ entries; cancel=1 adds a blank row and skews selection.
    ListLocalText 1, 1, 0, 0, VAR_SPECIAL_RESULT
    AddListOption MSG_MENU_CHIKORITA, MSG_LIST_HIGHLIGHT, 0
    AddListOption MSG_MENU_CYNDAQUIL, MSG_LIST_HIGHLIGHT, 1
    AddListOption MSG_MENU_TOTODILE, MSG_LIST_HIGHLIGHT, 2
    AddListOption MSG_MENU_BULBASAUR, MSG_LIST_HIGHLIGHT, 3
    AddListOption MSG_MENU_CHARMANDER, MSG_LIST_HIGHLIGHT, 4
    AddListOption MSG_MENU_SQUIRTLE, MSG_LIST_HIGHLIGHT, 5
    AddListOption MSG_MENU_TREECKO, MSG_LIST_HIGHLIGHT, 6
    AddListOption MSG_MENU_TORCHIC, MSG_LIST_HIGHLIGHT, 7
    AddListOption MSG_MENU_MUDKIP, MSG_LIST_HIGHLIGHT, 8
    AddListOption MSG_MENU_TURTWIG, MSG_LIST_HIGHLIGHT, 9
    AddListOption MSG_MENU_CHIMCHAR, MSG_LIST_HIGHLIGHT, 10
    AddListOption MSG_MENU_PIPLUP, MSG_LIST_HIGHLIGHT, 11
    ShowList
    closemsg
    copyvar VAR_PLAYER_STARTER, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 0
    goto_if_eq _give_chikorita
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _give_cyndaquil
    compare VAR_SPECIAL_RESULT, 2
    goto_if_eq _give_totodile
    compare VAR_SPECIAL_RESULT, 3
    goto_if_eq _give_bulbasaur
    compare VAR_SPECIAL_RESULT, 4
    goto_if_eq _give_charmander
    compare VAR_SPECIAL_RESULT, 5
    goto_if_eq _give_squirtle
    compare VAR_SPECIAL_RESULT, 6
    goto_if_eq _give_treecko
    compare VAR_SPECIAL_RESULT, 7
    goto_if_eq _give_torchic
    compare VAR_SPECIAL_RESULT, 8
    goto_if_eq _give_mudkip
    compare VAR_SPECIAL_RESULT, 9
    goto_if_eq _give_turtwig
    compare VAR_SPECIAL_RESULT, 10
    goto_if_eq _give_chimchar
    give_mon SPECIES_PIPLUP, 5, 0, 0, 0, VAR_SPECIAL_RESULT
    goto _starter_done
_give_chikorita:
    give_mon SPECIES_CHIKORITA, 5, 0, 0, 0, VAR_SPECIAL_RESULT
    goto _starter_done
_give_cyndaquil:
    give_mon SPECIES_CYNDAQUIL, 5, 0, 0, 0, VAR_SPECIAL_RESULT
    goto _starter_done
_give_totodile:
    give_mon SPECIES_TOTODILE, 5, 0, 0, 0, VAR_SPECIAL_RESULT
    goto _starter_done
_give_bulbasaur:
    give_mon SPECIES_BULBASAUR, 5, 0, 0, 0, VAR_SPECIAL_RESULT
    goto _starter_done
_give_charmander:
    give_mon SPECIES_CHARMANDER, 5, 0, 0, 0, VAR_SPECIAL_RESULT
    goto _starter_done
_give_squirtle:
    give_mon SPECIES_SQUIRTLE, 5, 0, 0, 0, VAR_SPECIAL_RESULT
    goto _starter_done
_give_treecko:
    give_mon SPECIES_TREECKO, 5, 0, 0, 0, VAR_SPECIAL_RESULT
    goto _starter_done
_give_torchic:
    give_mon SPECIES_TORCHIC, 5, 0, 0, 0, VAR_SPECIAL_RESULT
    goto _starter_done
_give_mudkip:
    give_mon SPECIES_MUDKIP, 5, 0, 0, 0, VAR_SPECIAL_RESULT
    goto _starter_done
_give_turtwig:
    give_mon SPECIES_TURTWIG, 5, 0, 0, 0, VAR_SPECIAL_RESULT
    goto _starter_done
_give_chimchar:
    give_mon SPECIES_CHIMCHAR, 5, 0, 0, 0, VAR_SPECIAL_RESULT
    goto _starter_done
_starter_done:
    setflag FLAG_GOT_STARTER
    get_partymon_species 0, VAR_TEMP_x4001
    set_starter_choice VAR_TEMP_x4001
    play_fanfare SEQ_ME_POKEGET
    wait_fanfare
    touchscreen_menu_show
    return

.close
