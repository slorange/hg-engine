#ifndef ECOLOGY_ECOLOGY_GENERATE_H
#define ECOLOGY_ECOLOGY_GENERATE_H

#include "constants/generated/ecology_compat.h"
#include "ecology/ecology_compat_view.h"

typedef struct EcologyRng {
    u32 state;
} EcologyRng;

typedef struct EcologyGenStats {
    u16 familiesUnplaced;
    u16 requiredRouteMiss;
    u16 pairingShortfall;
    u16 bucketsPartiallyFilled;
} EcologyGenStats;

void EcologyRngInit(EcologyRng *rng, u32 seed);
u32 EcologyRngNext(EcologyRng *rng);

u16 EcologyGenSlotLayoutBase(u8 groupId, u8 method, const u16 *slotBases);
u16 EcologyGenBuildSlotLayout(u16 *slotBasesOut);

// outSlots length must be >= EcologyGenBuildSlotLayout(...) return value.
// Each entry is a family id assigned to one encounter slot (stable order: group, method, slot).
// outLandSlotTimeMasks is optional; when non-NULL, same length as outSlots — land entries get
// effective spawn period mask (family ∩ group); non-land entries are 0.
bool8 EcologyGenerateWorld(
    const EcologyCompatView *view,
    u32 seed,
    u16 *outSlots,
    u8 *outLandSlotTimeMasks,
    u16 outSlotCapacity,
    EcologyGenStats *statsOut);

// Effective land spawn mask for a family at a group (0 in family table means all periods).
u8 EcologyEffectiveLandTimeMask(u8 groupId, u16 familyId);

#endif
