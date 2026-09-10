#ifndef FISHING_ROD_H
#define FISHING_ROD_H

#include "types.h"

typedef struct SaveData SaveData;

u16 LONG_CALL CountCaughtWaterTypeFamilies(SaveData *saveData);
u16 LONG_CALL FishingRod_RemainingForNextTier(SaveData *saveData);

#endif
