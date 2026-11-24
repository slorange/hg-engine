/* Host test of the actual routing code, including save/restart round trips. */
#include "center_hub.h"
#include "config.h"
#include <assert.h>
extern int puts(const char *);

#ifdef OPENWORLD_STORY_SKIP_AND_STARTING_ITEMS
static void TestHomeDoorSwap(void)
{
    // Saffron uses Copycat's house, beside its Pokémon Center.
    Location next = {399, 0, 0, 0, 0};
    Home_ResolveTransition(13, 59, &next);
    assert(next.mapId == 63 && next.warpId == 0);
    Home_ResolveTransition(13, 60, &next);
    assert(next.mapId == 399 && next.warpId == 0);

    next = (Location){59, 14, 0, 0, 0};
    Home_ResolveTransition(13, 399, &next);
    assert(next.mapId == 60 && next.warpId == 1);

    next = (Location){63, 1, 0, 0, 0}; // Bedroom stairs.
    Home_ResolveTransition(13, 64, &next);
    assert(next.mapId == 63 && next.warpId == 1);
    next = (Location){399, -1, 3, 5, 0}; // Explicit-coordinate transition.
    Home_ResolveTransition(13, 59, &next);
    assert(next.mapId == 399 && next.warpId == -1 && next.x == 3 && next.z == 5);
    next = (Location){63, 0, 0, 0, 0};
    Home_ResolveTransition(0, 60, &next);
    Home_ResolveTransition(0xFFFF, 60, &next);
    assert(next.mapId == 63 && next.warpId == 0);
    puts("OK: Home door swap, stairs, explicit coordinates, and default/invalid city");
}
#endif

int main(void)
{
#ifdef OPENWORLD_STORY_SKIP_AND_STARTING_ITEMS
    TestHomeDoorSwap();
#endif
    unsigned i;
    for (i = 0; i < NELEMS(gCenterHubDoors); i++) {
        const CenterHubDoor *door = &gCenterHubDoors[i];
        u8 save[3] = {0};
        u8 reloaded[3];
        Location next = {door->interior, 0, 0, 0, 0};
        CenterHub_ResolveTransition(save, door->exterior, &next);
        assert(next.mapId == CENTER_HUB_MAP && next.warpId == 0);
        assert(CenterHub_GetOrigin(save) == i + 1);
        for (unsigned j = 0; j < 3; j++) {
            reloaded[j] = save[j];
            save[j] = 0;
        }
        // Leave after restarting, using only the bytes in the saved record.
        next = (Location){36, 3, 8, 19, 1};
        CenterHub_ResolveTransition(reloaded, CENTER_HUB_MAP, &next);
        assert(next.mapId == door->exterior && next.warpId == door->exteriorWarp);
        next = (Location){CENTER_HUB_MAP, 1, 0, 0, 0};
        CenterHub_ResolveTransition(reloaded, CENTER_HUB_BASEMENT_MAP, &next);
        assert(CenterHub_GetOrigin(reloaded) == i + 1);
        next = (Location){CENTER_HUB_MAP, -1, 7, 2, 1};
        CenterHub_ResolveTransition(reloaded, 2, &next);
        assert(CenterHub_GetOrigin(reloaded) == i + 1 && next.x == 7);
        // A later Center visit replaces the old origin.
        next = (Location){69, 0, 0, 0, 0};
        CenterHub_ResolveTransition(reloaded, 67, &next);
        assert(CenterHub_GetOrigin(reloaded) == 1);
    }
    {
        u8 invalid[3] = {'C', 'H', 255};
        Location next = {36, 3, 0, 0, 1};
        CenterHub_ResolveTransition(invalid, 169, &next);
        assert(next.mapId == 36 && next.warpId == 3);
        // Indigo is entirely excluded, including the outdoor entrance.
        next = (Location){300, 0, 0, 0, 0};
        CenterHub_ResolveTransition(invalid, 58, &next);
        assert(next.mapId == 300 && next.warpId == 0);
        next = (Location){300, 1, 0, 0, 1};
        CenterHub_ResolveTransition(invalid, 301, &next);
        assert(next.mapId == 300 && next.warpId == 1);
        next = (Location){63, 0, 3, 10, 1};
        CenterHub_ResolveTransition(invalid, 60, &next);
        assert(next.mapId == 63 && next.warpId == 0);
    }
    puts("OK: 24 Center entry/exit and serialized origin round trips; basement/Union returns; origin replacement; invalid-save fallback; Indigo untouched; unrelated warp");
    return 0;
}
