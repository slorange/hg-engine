#include "../include/config.h"

#ifdef OPENWORLD_FLY_MAP

#include "../include/types.h"

/*
 * Fly / Pokégear map gates Kanto on SavePokegear.mapUnlockLevel (0–2), not gameClear.
 * MapApp init calls Pokegear_GetMapUnlockLevel then indexes sMapXScrollLimits[].
 *
 * OPENWORLD_FLY_MAP: arm9 hook at 0x0202EE70 (pret US layout in linked arm9 — not 0x0202EE84).
 */

#define POKEGEAR_BITFIELD_WORD_OFF 4u

static u8 openworld_vanilla_map_unlock_level(void *savePokegear)
{
    u32 word;

    if (savePokegear == NULL)
        return 0;

    word = *(const u32 *)((const u8 *)savePokegear + POKEGEAR_BITFIELD_WORD_OFF);
    /* Match Pokegear_GetMapUnlockLevel @ 0x0202EE70 (lsl #3 / lsr #30). */
    return (u8)(((word << 3) >> 30) & 3u);
}

u8 Pokegear_GetMapUnlockLevel_hook(void *savePokegear)
{
    u8 level;

    level = openworld_vanilla_map_unlock_level(savePokegear);
    if (level < 2u)
        level = 2u;
    return level;
}

#endif // OPENWORLD_FLY_MAP
