.nds
.thumb

.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

.create "build/t28_005_patch.bin", 0

// Mahogany Town OnLoad (slot 5 / scriptId 6): force post-rocket-hideout town state.
// Do NOT set Gyarados hide/catch flags (483, 362, 201). Flag 202 = hideout cleared (Route 43).
    setvar VAR_SCENE_ROCKET_TAKEOVER, 5
    setvar VAR_UNK_407A, 1
    clearflag FLAG_UNK_0C5
    clearflag FLAG_ROCKET_TAKEOVER_ACTIVE
    setflag FLAG_BEAT_RADIO_TOWER_ROCKETS
    setflag FLAG_ROCKET_HIDEOUT_CLEARED
    setflag FLAG_SPECIAL_MART_MAHOGANY_GOOD
    clearflag FLAG_HIDE_MAHOGANY_SHOP_SALESWOMAN
    setflag FLAG_HIDE_MAHOGANY_SHOP_SHADY_SALESMAN
    setflag FLAG_HIDE_MAHOGANY_SHOP_LANCE
    setflag FLAG_HIDE_ROCKET_TAKEOVER_1
    setflag FLAG_HIDE_ROCKET_TAKEOVER_2
    setflag FLAG_HIDE_ROCKET_TAKEOVER_3
    setflag FLAG_HIDE_ROCKET_TAKEOVER_4
    setflag FLAG_HIDE_ROCKET_TAKEOVER_5
    setflag FLAG_HIDE_ROCKET_TAKEOVER_6
    setflag FLAG_HIDE_ROUTE_43_GATE_ROCKETS
    clearflag FLAG_HIDE_ROUTE_43_GATE_GUARD
    setflag FLAG_UNK_1F9
    setflag FLAG_UNK_205
    hide_person 0
    hide_person 2
    setflag FLAG_HIDE_ROCKET_HIDEOUT_B2F_ARIANA
    setflag FLAG_HIDE_ROCKET_HIDEOUT_B3F_PETREL
    setflag FLAG_HIDE_ROCKET_HIDEOUT_B3F_ELECTRODE_1_AND_4
    setflag FLAG_HIDE_ROCKET_HIDEOUT_B3F_ELECTRODE_2_AND_5
    setflag FLAG_HIDE_ROCKET_HIDEOUT_B3F_ELECTRODE_3_AND_6
    setflag FLAG_HIDE_ROCKET_HIDEOUT_B3F_LANCE
    setflag FLAG_HIDE_ROCKET_HIDEOUT_B3F_RIVAL
    setflag FLAG_HIDE_ROCKET_HIDEOUT_B3F_GIOVANNI
    setflag FLAG_HIDE_ROCKET_HIDEOUT_B3F_MURKROW_1
    setflag FLAG_HIDE_ROCKET_HIDEOUT_B2F_MURKROW_1
    setflag FLAG_HIDE_ROCKET_HIDEOUT_B3F_MURKROW_2
    setflag FLAG_HIDE_ROCKET_HIDEOUT_B2F_MURKROW_2
    setflag FLAG_HIDE_ROCKET_HIDEOUT_B2F_MURKROW_3
    end

.close
