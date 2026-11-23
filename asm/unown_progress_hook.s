.syntax unified
.thumb

.global UnownBattleCaughtIconHook
.thumb_func
UnownBattleCaughtIconHook:
    push {r4, lr}
    movs r2, r4
    bl UnownBattleCaughtIcon
    pop {r4, pc}

.global Summary_ShowTypeIcon_R4
.thumb_func
Summary_ShowTypeIcon_R4:
    push {r4, lr}
    movs r2, r4
    bl Summary_ShowPokemonTypeIcon
    pop {r4, pc}

.global Summary_ShowTypeIcon_R5
.thumb_func
Summary_ShowTypeIcon_R5:
    push {r5, lr}
    movs r2, r5
    bl Summary_ShowPokemonTypeIcon
    pop {r5, pc}
