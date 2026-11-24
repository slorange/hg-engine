.nds
.thumb

// Keep only the application identity in ARM9 scratch.
.open "base/arm9.bin", 0x02000000
.org 0x021FF948
AbraTravelMapArgs:
    .word 0
.close

// The selector runs inside the picker overlay's own load range.
.open "base/overlay/overlay_0101.bin", 0x021E7740
.org 0x021FB300
.area 0x20, 0
AbraMapLoadMessages:
    push {r4, lr}
    ldr r0, [r4, 0x10] // Picker state -> map context -> application args.
    ldr r0, [r0, 0x20]
    ldr r4, =AbraTravelMapArgs
    ldr r4, [r4]
    cmp r0, r4
    bne @@load
    ldr r2, =855 // Abra copy of bank 273 with Teleport wording.
@@load:
    mov r0, 0 // Native MSGDATA_LOAD_LAZY argument.
    bl 0x0200BAF8
    pop {r4, pc}
    .pool
.endarea
.org 0x021EE23E
    bl AbraMapLoadMessages
.close
