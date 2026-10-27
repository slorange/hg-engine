.nds
.thumb

// big thanks to mikelan98 and nomura for this.  really cool stuff

.open "base/arm9.bin", 0x02000000

.org 0x02000CD0 // branch from Main(), run once

    bl load_arm9_expansion


.org 0x02110334

.area 0x02110358-.

load_arm9_expansion: // load the narc subfile with arm9 expansion data
    push {r2, lr}

// load overlay 129 as arm9 expansion (sync NoInit — type 2 async can finish after init runs)
    mov r0, #129
    mov r1, #1
    bl HandleLoadOverlay129 // HandleLoadOverlay(129, 1)

    mov r0, #0
    mov r0, #0
    mov r1, #3
    pop {r2, pc}

.pool

HandleLoadOverlay129:
	push {r3-r7, lr}
	// r0/r1 stay as overlay id / load type (2 = noinit async); skip hooked 0x02006FF8 prologue
	ldr r2, =0x02007000|1 // HandleLoadOverlay+8, need normal loading for the first one
	bx r2

.pool

.endarea

.close
