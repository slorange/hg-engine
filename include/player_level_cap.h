#ifndef PLAYER_LEVEL_CAP_H
#define PLAYER_LEVEL_CAP_H

#include "types.h"

/** Battle-4: cap = 10 + 4×badges (80 at 16+). */
static inline u8 GetPlayerLevelCapForBadges(u8 badgeCount)
{
    if (badgeCount >= 16) {
        return 80;
    }
    return (u8)(10 + 4 * badgeCount);
}

#endif
