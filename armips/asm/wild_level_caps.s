.nds
.thumb

// arm9 scratch for wild level cap runtime state (survives overlay 129 reloads).
// sPersistFieldSysPtr: written by StoreFieldSysPtr

.open "base/arm9.bin", 0x02000000

.org 0x021FF900
    .word 0

.org 0x021FF910
    .skip 0x20

.org 0x021FF930
    .skip 0x8

.close
