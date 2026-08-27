.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/vars.s"

.equ ITEM_SS_TICKET, 456
.equ ITEM_PASS, 480
.equ ITEM_APRICORN_BOX, 468

// Entered via goto replacing wait(15) after Mom's vanilla UI gifts.
// setvar first (stops OnFrame re-trigger), then grants, then goto back to walk-away.
.create "build/t20_mom_openworld.bin", 0
    setvar VAR_SCENE_PLAYERS_HOUSE_1F, 1
    giveitem_no_check ITEM_SS_TICKET, 1
    giveitem_no_check ITEM_PASS, 1
    giveitem_no_check ITEM_APRICORN_BOX, 1
    setflag FLAG_GOT_APRICORN_BOX
    give_running_shoes
    setflag FLAG_GOT_POKEDEX
    GivePokedex
.close
