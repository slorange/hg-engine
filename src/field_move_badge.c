#include "../include/config.h"
#include "../include/types.h"
#include "../include/save.h"

/*
 * Vanilla FieldMove_Check* (arm9 ~0x02067F00) gates HM use on specific Gym badge
 * flags via PlayerProfile_TestBadgeFlag. Open-world grants HMs by total badge count,
 * so those checks must not block field use once the move is in the party.
 *
 * Mart badge shelves (ScrCmd_MartBuy in field overlay 131) also call TestBadgeFlag;
 * LR distinguishes field-move callers from everything else.
 */
#ifdef OPENWORLD_FIELD_MOVES_NO_BADGE_GATE

#define FIELD_MOVE_TEST_BADGE_LR_MIN 0x02067F87u
#define FIELD_MOVE_TEST_BADGE_LR_MAX 0x0206888Bu

static BOOL FieldMoveBadgeBypassFromCaller(void)
{
    register u32 retAddr asm("lr");

    return retAddr >= FIELD_MOVE_TEST_BADGE_LR_MIN && retAddr <= FIELD_MOVE_TEST_BADGE_LR_MAX;
}

#endif // OPENWORLD_FIELD_MOVES_NO_BADGE_GATE

BOOL PlayerProfile_TestBadgeFlag_hook(struct PlayerProfile *profile, s32 badgeNumber)
{
#ifdef OPENWORLD_FIELD_MOVES_NO_BADGE_GATE
    if (FieldMoveBadgeBypassFromCaller())
        return TRUE;
#endif

    if (badgeNumber >= 16)
        return FALSE;

    if (badgeNumber >= 8)
        return (profile->kantoBadges >> (badgeNumber - 8)) & 1;

    return (profile->johtoBadges >> badgeNumber) & 1;
}
