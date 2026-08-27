.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

.equ ITEM_SS_TICKET, 456
.equ ITEM_PASS, 480
.equ ITEM_APRICORN_BOX, 468

.equ MSG_MOM_GREET_M, 0
.equ MSG_MOM_GREET_F, 1

.equ OBJ_MOM, 0

.create "build/t20_mom_script0.bin", 0
    scrcmd_609
    lockall
    compare VAR_SCENE_PLAYERS_HOUSE_1F, 0
    goto_if_ne _already_done
    setvar VAR_SCENE_PLAYERS_HOUSE_1F, 1
    apply_movement obj_player, _mv_player_down
    apply_movement OBJ_MOM, _mv_mom_spot
    wait_movement
    callstd std_play_mom_music
    wait 30, VAR_SPECIAL_RESULT
    apply_movement OBJ_MOM, _mv_mom_approach
    wait_movement
    buffer_players_name 0
    gender_msgbox MSG_MOM_GREET_M, MSG_MOM_GREET_F
    closemsg
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
    giveitem_no_check ITEM_SS_TICKET, 1
    giveitem_no_check ITEM_PASS, 1
    giveitem_no_check ITEM_APRICORN_BOX, 1
    closemsg
    setflag FLAG_GOT_APRICORN_BOX
    give_running_shoes
    setflag FLAG_GOT_POKEDEX
    GivePokedex
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

.close
