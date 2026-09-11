.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"
.include "armips/include/config.s"

.equ ITEM_OLD_ROD, 445
.equ ITEM_GOOD_ROD, 446
.equ ITEM_SUPER_ROD, 447

.equ MSG_GIVE_OLD, 9
.equ MSG_GIVE_GOOD, 10
.equ MSG_GIVE_SUPER, 11
.equ MSG_PROGRESS, 12
.equ MSG_ALL_DONE, 13

.create "build/olivine_rod_guru.bin", 0
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer

    hasitem ITEM_OLD_ROD, 1, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _sync_old_flag
    goto _sync_good_item

_sync_old_flag:
    setflag FLAG_GOT_OLD_ROD

_sync_good_item:
    hasitem ITEM_GOOD_ROD, 1, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _sync_good_flags
    goto _main

_sync_good_flags:
    setflag FLAG_GOT_OLD_ROD
    setflag FLAG_GOT_GOOD_ROD

_main:
    hasitem ITEM_SUPER_ROD, 1, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _all_done

    hasitem ITEM_GOOD_ROD, 1, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _check_super_tier
    goto_if_set FLAG_GOT_GOOD_ROD, _check_super_tier

    hasitem ITEM_OLD_ROD, 1, VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq _check_good_tier
    goto_if_set FLAG_GOT_OLD_ROD, _check_good_tier

    goto _give_old

_check_good_tier:
    FishingRodCount VAR_SPECIAL_x8001
    compare VAR_SPECIAL_x8001, FISHING_ROD_GOOD_FAMILIES
    goto_if_ge _give_good
    setvar VAR_SPECIAL_x8000, FISHING_ROD_GOOD_FAMILIES
    subvar VAR_SPECIAL_x8000, VAR_SPECIAL_x8001
    TextNumber 0, VAR_SPECIAL_x8000
    npc_msg MSG_PROGRESS
    goto _finish

_give_good:
    npc_msg MSG_GIVE_GOOD
    wait_button_or_walk_away
    closemsg
    giveitem_no_check ITEM_GOOD_ROD, 1
    setflag FLAG_GOT_GOOD_ROD
    goto _finish_give

_check_super_tier:
    FishingRodCount VAR_SPECIAL_x8001
    compare VAR_SPECIAL_x8001, FISHING_ROD_SUPER_FAMILIES
    goto_if_ge _give_super
    setvar VAR_SPECIAL_x8000, FISHING_ROD_SUPER_FAMILIES
    subvar VAR_SPECIAL_x8000, VAR_SPECIAL_x8001
    TextNumber 0, VAR_SPECIAL_x8000
    npc_msg MSG_PROGRESS
    goto _finish

_give_super:
    npc_msg MSG_GIVE_SUPER
    wait_button_or_walk_away
    closemsg
    giveitem_no_check ITEM_SUPER_ROD, 1
    goto _finish_give

_give_old:
    npc_msg MSG_GIVE_OLD
    wait_button_or_walk_away
    closemsg
    giveitem_no_check ITEM_OLD_ROD, 1
    setflag FLAG_GOT_OLD_ROD
    goto _finish_give

_all_done:
    npc_msg MSG_ALL_DONE
    goto _finish

_finish_give:
    closemsg
    releaseall
    end

_finish:
    wait_button_or_walk_away
    closemsg
    releaseall
    end
.close
