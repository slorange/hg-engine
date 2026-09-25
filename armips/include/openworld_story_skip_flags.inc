// Vanilla story skip on new saves — Mom intro (OPENWORLD_STORY_SKIP_AND_STARTING_ITEMS).
// DESIGN-STORY.md Story-2. Mahogany rocket *flags* live here; Mahogany map OnLoad only
// runs hide_person when open-world starting items are on (see scr_seq_t28_005_onload.s).

// Cherrygrove guide / Route 30 (Apricorn Box + shoes from Mom)
    setflag FLAG_HIDE_CHERRYGROVE_GUIDE_GENT
    setflag FLAG_HIDE_ROUTE_30_YOUNGSTER_JOEY
    setflag FLAG_HIDE_ROUTE_30_APRICORN_MAN
    setflag FLAG_HIDE_ROUTE_30_BATTLERS

// SS Aqua: skip first-voyage story; ticket item already granted in Mom script
    setflag FLAG_BOAT_ARRIVED
    setflag FLAG_UNK_0F2

// Azalea — D26R0102 post–Proton (+ 425/426 gym); scr_seq 866 patches well coord + rival scripts
    setflag FLAG_UNK_1A9
    clearflag FLAG_UNK_19E
    clearflag FLAG_UNK_19F
    clearflag FLAG_HIDE_AZALEA_SLOWPOKES
    setflag FLAG_BEAT_AZALEA_ROCKETS
    setvar VAR_UNK_4075, 1
    setvar VAR_UNK_4080, 2
    setflag FLAG_UNK_1AA

// Mahogany post-rocket (do not set Gyarados flags 201 / 362 / 483)
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

// Rival removed — hide overworld appearances; skip naming flow flags
    setflag FLAG_UNK_079
    setflag FLAG_TALKED_TO_MOM_AFTER_NAMING_RIVAL
    setflag FLAG_HIDE_NEW_BARK_RIVAL
    setflag FLAG_HIDE_CHERRYGROVE_RIVAL
    setflag FLAG_HIDE_RADIO_TOWER_RIVAL
    setflag FLAG_HIDE_BURNED_TOWER_1F_RIVAL
    setflag FLAG_HIDE_OLIVINE_RIVAL
    setflag FLAG_HIDE_ROCKET_HIDEOUT_B3F_RIVAL
    setflag FLAG_HIDE_VICTORY_ROAD_RIVAL
    setflag FLAG_HIDE_ECRUTEAK_RIVAL
    setflag FLAG_HIDE_INDIGO_PLATEAU_RIVAL
    setflag FLAG_HIDE_DRAGONS_DEN_RIVAL
    setflag FLAG_HIDE_ROUTE_22_GIOVANNI_RIVAL

// Professor Elm lab errand (Falkner patch uses VAR_SCENE_ELMS_LAB = 6)
    clearflag FLAG_ELMS_LAB_PREVENT_PLAYER_ESCAPE
    setvar VAR_SCENE_ELMS_LAB, 6
    setflag FLAG_HIDE_ELMS_LAB_OFFICER
    setflag FLAG_HIDE_ELMS_LAB_FRIEND
