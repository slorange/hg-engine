.nds
.thumb

.open "base/overlay/overlay_0001.bin", 0x021E5900

// The animation gets the 1-based colour in r0. Use the fruit sprite table
// instead of base tag + colour, since tags 277 and 278 belong to other objects.
.org 0x022049D0
.area 0x12, 0
    lsl r6, r0, 1
    ldr r1, [pc, 0xCC] // 0x02204AA0, repointed to gApricornFruitTags
    ldrh r1, [r1, r6]
    ldr r0, [r5, 0x3C]
    ldr r2, [sp, 4]
    ldr r3, [sp, 0]
    nop
    nop
    nop
.endarea

.close
