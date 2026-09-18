.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

.equ ITEM_SS_TICKET, 456
.equ ITEM_PASS, 480
.equ ITEM_APRICORN_BOX, 468
.equ ITEM_POKE_BALL, 4
.equ ITEM_HM02, 421

.equ MSG_MOM_GREET_M, 0
.equ MSG_MOM_GREET_F, 1
.equ MSG_CITY_PROMPT, 2
.equ MSG_MENU_NEW_BARK, 3
.equ MSG_MENU_VIOLET, 4
.equ MSG_MENU_AZALEA, 5
.equ MSG_MENU_GOLDENROD, 6
.equ MSG_MENU_ECRUTEAK, 7
.equ MSG_MENU_OLIVINE, 8
.equ MSG_MENU_CIANWOOD, 9
.equ MSG_MENU_MAHOGANY, 10
.equ MSG_MENU_BLACKTHORN, 11
.equ MSG_MENU_PALLET, 12
.equ MSG_MENU_VIRIDIAN, 13
.equ MSG_MENU_PEWTER, 14
.equ MSG_MENU_CERULEAN, 15
.equ MSG_MENU_SAFFRON, 16
.equ MSG_MENU_LAVENDER, 17
.equ MSG_MENU_CELADON, 18
.equ MSG_MENU_VERMILION, 19
.equ MSG_MENU_FUCHSIA, 20
.equ MSG_STARTER_PROMPT, 21
.equ MSG_LIST_HIGHLIGHT, 254
.equ MSG_MENU_CHIKORITA, 22
.equ MSG_MENU_CYNDAQUIL, 23
.equ MSG_MENU_TOTODILE, 24
.equ MSG_MENU_BULBASAUR, 25
.equ MSG_MENU_CHARMANDER, 26
.equ MSG_MENU_SQUIRTLE, 27
.equ MSG_MENU_TREECKO, 28
.equ MSG_MENU_TORCHIC, 29
.equ MSG_MENU_MUDKIP, 30
.equ MSG_MENU_TURTWIG, 31
.equ MSG_MENU_CHIMCHAR, 32
.equ MSG_MENU_PIPLUP, 33

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
.equ MAP_T08, 56
.equ MAP_T22, 73
.equ MAP_T23, 74
.equ MAP_T26, 77
.equ MAP_T27, 78
.equ MAP_T24, 75
.equ MAP_T28, 87
.equ MAP_T30, 89
.equ MAP_T01, 49
.equ MAP_T02, 50
.equ MAP_T03, 51
.equ MAP_T04, 52
.equ MAP_T05, 53
.equ MAP_T06, 54
.equ MAP_T07, 55

.equ START_CITY_NEW_BARK, 0
.equ START_CITY_VIOLET, 1
.equ START_CITY_AZALEA, 2
.equ START_CITY_GOLDENROD, 3
.equ START_CITY_ECRUTEAK, 4
.equ START_CITY_OLIVINE, 5
.equ START_CITY_CIANWOOD, 6
.equ START_CITY_MAHOGANY, 7
.equ START_CITY_BLACKTHORN, 8
.equ START_CITY_PALLET, 9
.equ START_CITY_VIRIDIAN, 10
.equ START_CITY_PEWTER, 11
.equ START_CITY_CERULEAN, 12
.equ START_CITY_SAFFRON, 13
.equ START_CITY_LAVENDER, 14
.equ START_CITY_CELADON, 15
.equ START_CITY_VERMILION, 16
.equ START_CITY_FUCHSIA, 17

.equ NB_HOME_WARP, 1
.equ GD_HOME_WARP, 14
.equ SF_HOME_WARP, 14
.equ FC_HOME_WARP, 8
.equ VI_HOME_WARP, 8
.equ AZ_HOME_WARP, 4
.equ EC_HOME_WARP, 1
.equ OL_HOME_WARP, 6
.equ CI_HOME_WARP, 7
.equ MH_HOME_WARP, 4
.equ BT_HOME_WARP, 4
.equ PA_HOME_WARP, 0
.equ VR_HOME_WARP, 1
.equ PW_HOME_WARP, 5
.equ CE_HOME_WARP, 2
.equ LA_HOME_WARP, 2
.equ CD_HOME_WARP, 6
.equ VM_HOME_WARP, 3

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
    setflag FLAG_UNK_09A
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
    setflag FLAG_UNLOCKED_WEST_KANTO
    setflag FLAG_UNK_265
    setflag FLAG_HIDE_ROUTE_19_WORKMEN_CLOSED
    setflag FLAG_HIDE_ROUTE_19_WORKMEN_OPEN
    setflag FLAG_MAPTEMP_010
    setflag FLAG_MAPTEMP_011
    setflag FLAG_MAPTEMP_012
    setflag FLAG_MAPTEMP_013
    setflag FLAG_MAPTEMP_014
.if OPENWORLD_STORY_FLAG_SWEEP == 1
    setvar VAR_TEMP_x4000, OPENWORLD_STORY_FLAG_SWEEP_START
_story_flag_sweep:
    setflagvar VAR_TEMP_x4000
    addvar VAR_TEMP_x4000, 1
    compare VAR_TEMP_x4000, OPENWORLD_STORY_FLAG_SWEEP_END + 1
    goto_if_lt _story_flag_sweep
.endif
    giveitem_no_check ITEM_POKE_BALL, 5
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
    AddListOption MSG_MENU_VIOLET, MSG_LIST_HIGHLIGHT, 1
    AddListOption MSG_MENU_AZALEA, MSG_LIST_HIGHLIGHT, 2
    AddListOption MSG_MENU_GOLDENROD, MSG_LIST_HIGHLIGHT, 3
    AddListOption MSG_MENU_ECRUTEAK, MSG_LIST_HIGHLIGHT, 4
    AddListOption MSG_MENU_OLIVINE, MSG_LIST_HIGHLIGHT, 5
    AddListOption MSG_MENU_CIANWOOD, MSG_LIST_HIGHLIGHT, 6
    AddListOption MSG_MENU_MAHOGANY, MSG_LIST_HIGHLIGHT, 7
    AddListOption MSG_MENU_BLACKTHORN, MSG_LIST_HIGHLIGHT, 8
    AddListOption MSG_MENU_PALLET, MSG_LIST_HIGHLIGHT, 9
    AddListOption MSG_MENU_VIRIDIAN, MSG_LIST_HIGHLIGHT, 10
    AddListOption MSG_MENU_PEWTER, MSG_LIST_HIGHLIGHT, 11
    AddListOption MSG_MENU_CERULEAN, MSG_LIST_HIGHLIGHT, 12
    AddListOption MSG_MENU_SAFFRON, MSG_LIST_HIGHLIGHT, 13
    AddListOption MSG_MENU_LAVENDER, MSG_LIST_HIGHLIGHT, 14
    AddListOption MSG_MENU_CELADON, MSG_LIST_HIGHLIGHT, 15
    AddListOption MSG_MENU_VERMILION, MSG_LIST_HIGHLIGHT, 16
    AddListOption MSG_MENU_FUCHSIA, MSG_LIST_HIGHLIGHT, 17
    ShowList
    closemsg
    copyvar VAR_PLAYER_START_CITY, VAR_SPECIAL_RESULT
    call _set_home_dynamic_warp
    touchscreen_menu_show
    return

_set_home_dynamic_warp:
    // All cities wired except New Bark (0).
    compare VAR_PLAYER_START_CITY, START_CITY_VIOLET
    goto_if_eq _dyn_violet
    compare VAR_PLAYER_START_CITY, START_CITY_AZALEA
    goto_if_eq _dyn_azalea
    compare VAR_PLAYER_START_CITY, START_CITY_GOLDENROD
    goto_if_eq _dyn_goldenrod
    compare VAR_PLAYER_START_CITY, START_CITY_ECRUTEAK
    goto_if_eq _dyn_ecruteak
    compare VAR_PLAYER_START_CITY, START_CITY_OLIVINE
    goto_if_eq _dyn_olivine
    compare VAR_PLAYER_START_CITY, START_CITY_CIANWOOD
    goto_if_eq _dyn_cianwood
    compare VAR_PLAYER_START_CITY, START_CITY_MAHOGANY
    goto_if_eq _dyn_mahogany
    compare VAR_PLAYER_START_CITY, START_CITY_BLACKTHORN
    goto_if_eq _dyn_blackthorn
    compare VAR_PLAYER_START_CITY, START_CITY_PALLET
    goto_if_eq _dyn_pallet
    compare VAR_PLAYER_START_CITY, START_CITY_VIRIDIAN
    goto_if_eq _dyn_viridian
    compare VAR_PLAYER_START_CITY, START_CITY_PEWTER
    goto_if_eq _dyn_pewter
    compare VAR_PLAYER_START_CITY, START_CITY_CERULEAN
    goto_if_eq _dyn_cerulean
    compare VAR_PLAYER_START_CITY, START_CITY_SAFFRON
    goto_if_eq _dyn_saffron
    compare VAR_PLAYER_START_CITY, START_CITY_LAVENDER
    goto_if_eq _dyn_lavender
    compare VAR_PLAYER_START_CITY, START_CITY_CELADON
    goto_if_eq _dyn_celadon
    compare VAR_PLAYER_START_CITY, START_CITY_VERMILION
    goto_if_eq _dyn_vermilion
    compare VAR_PLAYER_START_CITY, START_CITY_FUCHSIA
    goto_if_eq _dyn_fuchsia
    goto _dyn_new_bark
_dyn_cianwood:
    setvar VAR_TEMP_x4000, MAP_T24
    setvar VAR_TEMP_x4001, CI_HOME_WARP
    setvar VAR_TEMP_x4002, 0
    setvar VAR_TEMP_x4003, 0
    setvar VAR_TEMP_x4004, DIR_NORTH
    set_dynamic_warp VAR_TEMP_x4000, VAR_TEMP_x4001, VAR_TEMP_x4002, VAR_TEMP_x4003, VAR_TEMP_x4004
    return
_dyn_mahogany:
    setvar VAR_TEMP_x4000, MAP_T28
    setvar VAR_TEMP_x4001, MH_HOME_WARP
    setvar VAR_TEMP_x4002, 0
    setvar VAR_TEMP_x4003, 0
    setvar VAR_TEMP_x4004, DIR_NORTH
    set_dynamic_warp VAR_TEMP_x4000, VAR_TEMP_x4001, VAR_TEMP_x4002, VAR_TEMP_x4003, VAR_TEMP_x4004
    return
_dyn_blackthorn:
    setvar VAR_TEMP_x4000, MAP_T30
    setvar VAR_TEMP_x4001, BT_HOME_WARP
    setvar VAR_TEMP_x4002, 0
    setvar VAR_TEMP_x4003, 0
    setvar VAR_TEMP_x4004, DIR_NORTH
    set_dynamic_warp VAR_TEMP_x4000, VAR_TEMP_x4001, VAR_TEMP_x4002, VAR_TEMP_x4003, VAR_TEMP_x4004
    return
_dyn_pallet:
    setvar VAR_TEMP_x4000, MAP_T01
    setvar VAR_TEMP_x4001, PA_HOME_WARP
    setvar VAR_TEMP_x4002, 0
    setvar VAR_TEMP_x4003, 0
    setvar VAR_TEMP_x4004, DIR_NORTH
    set_dynamic_warp VAR_TEMP_x4000, VAR_TEMP_x4001, VAR_TEMP_x4002, VAR_TEMP_x4003, VAR_TEMP_x4004
    return
_dyn_viridian:
    setvar VAR_TEMP_x4000, MAP_T02
    setvar VAR_TEMP_x4001, VR_HOME_WARP
    setvar VAR_TEMP_x4002, 0
    setvar VAR_TEMP_x4003, 0
    setvar VAR_TEMP_x4004, DIR_NORTH
    set_dynamic_warp VAR_TEMP_x4000, VAR_TEMP_x4001, VAR_TEMP_x4002, VAR_TEMP_x4003, VAR_TEMP_x4004
    return
_dyn_pewter:
    setvar VAR_TEMP_x4000, MAP_T03
    setvar VAR_TEMP_x4001, PW_HOME_WARP
    setvar VAR_TEMP_x4002, 0
    setvar VAR_TEMP_x4003, 0
    setvar VAR_TEMP_x4004, DIR_NORTH
    set_dynamic_warp VAR_TEMP_x4000, VAR_TEMP_x4001, VAR_TEMP_x4002, VAR_TEMP_x4003, VAR_TEMP_x4004
    return
_dyn_cerulean:
    setvar VAR_TEMP_x4000, MAP_T04
    setvar VAR_TEMP_x4001, CE_HOME_WARP
    setvar VAR_TEMP_x4002, 0
    setvar VAR_TEMP_x4003, 0
    setvar VAR_TEMP_x4004, DIR_NORTH
    set_dynamic_warp VAR_TEMP_x4000, VAR_TEMP_x4001, VAR_TEMP_x4002, VAR_TEMP_x4003, VAR_TEMP_x4004
    return
_dyn_lavender:
    setvar VAR_TEMP_x4000, MAP_T05
    setvar VAR_TEMP_x4001, LA_HOME_WARP
    setvar VAR_TEMP_x4002, 0
    setvar VAR_TEMP_x4003, 0
    setvar VAR_TEMP_x4004, DIR_NORTH
    set_dynamic_warp VAR_TEMP_x4000, VAR_TEMP_x4001, VAR_TEMP_x4002, VAR_TEMP_x4003, VAR_TEMP_x4004
    return
_dyn_celadon:
    setvar VAR_TEMP_x4000, MAP_T07
    setvar VAR_TEMP_x4001, CD_HOME_WARP
    setvar VAR_TEMP_x4002, 0
    setvar VAR_TEMP_x4003, 0
    setvar VAR_TEMP_x4004, DIR_NORTH
    set_dynamic_warp VAR_TEMP_x4000, VAR_TEMP_x4001, VAR_TEMP_x4002, VAR_TEMP_x4003, VAR_TEMP_x4004
    return
_dyn_vermilion:
    setvar VAR_TEMP_x4000, MAP_T06
    setvar VAR_TEMP_x4001, VM_HOME_WARP
    setvar VAR_TEMP_x4002, 0
    setvar VAR_TEMP_x4003, 0
    setvar VAR_TEMP_x4004, DIR_NORTH
    set_dynamic_warp VAR_TEMP_x4000, VAR_TEMP_x4001, VAR_TEMP_x4002, VAR_TEMP_x4003, VAR_TEMP_x4004
    return
_dyn_azalea:
    setvar VAR_TEMP_x4000, MAP_T23
    setvar VAR_TEMP_x4001, AZ_HOME_WARP
    setvar VAR_TEMP_x4002, 0
    setvar VAR_TEMP_x4003, 0
    setvar VAR_TEMP_x4004, DIR_NORTH
    set_dynamic_warp VAR_TEMP_x4000, VAR_TEMP_x4001, VAR_TEMP_x4002, VAR_TEMP_x4003, VAR_TEMP_x4004
    return
_dyn_ecruteak:
    setvar VAR_TEMP_x4000, MAP_T27
    setvar VAR_TEMP_x4001, EC_HOME_WARP
    setvar VAR_TEMP_x4002, 0
    setvar VAR_TEMP_x4003, 0
    setvar VAR_TEMP_x4004, DIR_NORTH
    set_dynamic_warp VAR_TEMP_x4000, VAR_TEMP_x4001, VAR_TEMP_x4002, VAR_TEMP_x4003, VAR_TEMP_x4004
    return
_dyn_olivine:
    setvar VAR_TEMP_x4000, MAP_T26
    setvar VAR_TEMP_x4001, OL_HOME_WARP
    setvar VAR_TEMP_x4002, 0
    setvar VAR_TEMP_x4003, 0
    setvar VAR_TEMP_x4004, DIR_NORTH
    set_dynamic_warp VAR_TEMP_x4000, VAR_TEMP_x4001, VAR_TEMP_x4002, VAR_TEMP_x4003, VAR_TEMP_x4004
    return
_dyn_violet:
    setvar VAR_TEMP_x4000, MAP_T22
    setvar VAR_TEMP_x4001, VI_HOME_WARP
    setvar VAR_TEMP_x4002, 0
    setvar VAR_TEMP_x4003, 0
    setvar VAR_TEMP_x4004, DIR_NORTH
    set_dynamic_warp VAR_TEMP_x4000, VAR_TEMP_x4001, VAR_TEMP_x4002, VAR_TEMP_x4003, VAR_TEMP_x4004
    return
_dyn_fuchsia:
    setvar VAR_TEMP_x4000, MAP_T08
    setvar VAR_TEMP_x4001, FC_HOME_WARP
    setvar VAR_TEMP_x4002, 0
    setvar VAR_TEMP_x4003, 0
    setvar VAR_TEMP_x4004, DIR_NORTH
    set_dynamic_warp VAR_TEMP_x4000, VAR_TEMP_x4001, VAR_TEMP_x4002, VAR_TEMP_x4003, VAR_TEMP_x4004
    return
_dyn_saffron:
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
