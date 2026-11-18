#include "apricorn_craft.h"
#include "constants/file.h"
#include "overlay.h"

// Patched after both overlays link. This synchronous NPC service never
// opens an application or yields while executing in the field overlay.
u32 ApricornCraftFieldAddr;

u16 ApricornCraft_Run(void *saveData, BOOL commit, u16 *total, u16 *feeHundreds)
{
    typedef u16 (*CraftFn)(void *, BOOL, u16 *, u16 *);
    *total = *feeHundreds = 0;
    if (!ApricornCraftFieldAddr || !IsOverlayLoaded(OVERLAY_FIELD_EXTENSION))
        return APRICORN_CRAFT_UNAVAILABLE;
    return ((CraftFn)(ApricornCraftFieldAddr | 1u))(saveData, commit, total, feeHundreds);
}
