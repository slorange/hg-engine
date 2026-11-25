.nds
.thumb
.include "armips/include/scriptmacros.s"
.include "armips/include/flags.s"
.include "armips/include/soundeffects.s"
.include "armips/include/vars.s"

.equ KIMONO_GIRL, 12
.equ FOLLOWER, 253

.create "build/ilex_kimono.bin", 0
    play_se SEQ_SE_DP_SELECT
    lockall
    faceplayer
    npc_msg 68
    wait_ab_press
    npc_msg 73
    wait_ab_press
    closemsg
    scrcmd_729 VAR_TEMP_x4000 // FollowMon_IsActive
    compare VAR_TEMP_x4000, 1
    goto_if_ne thank_player
    apply_movement FOLLOWER, follower_points_west
    wait_movement
    npc_msg 71
    goto farewell_done

thank_player:
    npc_msg 70
farewell_done:
    wait_ab_press
    closemsg

    // Step south to go around a player standing directly to her west.
    get_player_coords VAR_TEMP_x4000, VAR_TEMP_x4001
    compare VAR_TEMP_x4000, 37
    goto_if_eq step_around_player
    apply_movement KIMONO_GIRL, walk_west
    goto finish
step_around_player:
    apply_movement KIMONO_GIRL, walk_south_then_west
finish:
    wait_movement
    hide_person KIMONO_GIRL
    setflag FLAG_UNK_23D
    setvar VAR_UNK_40E9, 1
    releaseall
    end

.align 2
follower_points_west:
    .halfword LookLeft, 1, JumpLeftSite, 1, MovementEnd, 0
walk_west:
    .halfword WalkLeftFast, 8, WalkDownFast, 1, WalkLeftFast, 4, MovementEnd, 0
walk_south_then_west:
    .halfword WalkDownFast, 1, WalkLeftFast, 12, MovementEnd, 0
.close
