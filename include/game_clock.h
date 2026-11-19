#ifndef GAME_CLOCK_H
#define GAME_CLOCK_H
#include "types.h"

// Session-only time-of-day adjustment. Calendar and normal save layout stay intact.
BOOL GameClock_RestUntilHour(u32 hour);
#endif
