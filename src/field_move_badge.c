#include "../include/config.h"
#include "../include/types.h"
#include "../include/save.h"

static u8 PopcountBadges(u8 badgeBits)
{
    u8 count = 0;

    while (badgeBits != 0) {
        count += badgeBits & 1;
        badgeBits >>= 1;
    }
    return count;
}

u8 PlayerProfile_CountBadges(const struct PlayerProfile *profile)
{
    return (u8)(PopcountBadges(profile->johtoBadges) + PopcountBadges(profile->kantoBadges));
}

/*
 * Vanilla FieldMove_Check* (arm9 ~0x02067F00) gates HM use on specific Gym badge
 * flags via PlayerProfile_TestBadgeFlag. Open-world grants HMs by total badge count,
 * so those checks must not block field use once the move is in the party.
 *
 * InitMartUI (overlay 12 ~0x02256D34) also calls TestBadgeFlag per item using vanilla
 * badge slot indices; remap those to total badge count for any-order Gyms.
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

#ifdef MART_EXPANSION

/* Mart item visibility checks near InitMartUI; re-scan with scripts/local/_scan_testbadge_bl.py if rebased. */
#define MART_ITEM_BADGE_TEST_LR_MIN 0x02256C00u
#define MART_ITEM_BADGE_TEST_LR_MAX 0x02257000u

static BOOL MartItemBadgeCheckFromCaller(void)
{
    register u32 retAddr asm("lr");

    return retAddr >= MART_ITEM_BADGE_TEST_LR_MIN && retAddr <= MART_ITEM_BADGE_TEST_LR_MAX;
}

#endif // MART_EXPANSION

BOOL PlayerProfile_TestBadgeFlag_hook(struct PlayerProfile *profile, s32 badgeNumber)
{
#ifdef OPENWORLD_FIELD_MOVES_NO_BADGE_GATE
    if (FieldMoveBadgeBypassFromCaller())
        return TRUE;
#endif

#ifdef MART_EXPANSION
    if (MartItemBadgeCheckFromCaller()) {
        if (badgeNumber < 0 || badgeNumber >= 16)
            return FALSE;
        return (BOOL)(PlayerProfile_CountBadges(profile) >= (u8)(badgeNumber + 1));
    }
#endif

    if (badgeNumber >= 16)
        return FALSE;

    if (badgeNumber >= 8)
        return (profile->kantoBadges >> (badgeNumber - 8)) & 1;

    return (profile->johtoBadges >> badgeNumber) & 1;
}
