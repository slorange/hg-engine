#include "config.h"

#ifdef IMPLEMENT_ECOLOGY_GENERATION

#include "constants/generated/ecology_compat.h"
#include "ecology/ecology_compat_access.h"
#include "ecology/ecology_generate.h"

static u16 EcologyGroupMethodIndex(u8 groupId, u8 method)
{
    return (u16)groupId * (u16)ECOLOGY_METHOD_COUNT + (u16)method;
}

static u8 EcologyGroupMethodCapacity(u8 groupId, u8 method)
{
    u16 index = EcologyGroupMethodIndex(groupId, method);
    u8 capacity = ECO_METHOD_SLOTS(index);

    if (capacity > ECOLOGY_GEN_MAX_SLOTS_PER_BUCKET) {
        return 0;
    }
    return capacity;
}

u16 EcologyGenSlotLayoutBase(u8 groupId, u8 method, const u16 *slotBases)
{
    return slotBases[EcologyGroupMethodIndex(groupId, method)];
}

u16 EcologyGenBuildSlotLayout(u16 *slotBasesOut)
{
    u32 cursor = 0;
    u8 groupId;

    for (groupId = 0; groupId < ECOLOGY_NUM_GROUPS; groupId++) {
        u8 method;
        for (method = 0; method < ECOLOGY_METHOD_COUNT; method++) {
            u16 index = EcologyGroupMethodIndex(groupId, method);
            u8 capacity = EcologyGroupMethodCapacity(groupId, method);

            slotBasesOut[index] = (u16)cursor;
            cursor += capacity;
            if (cursor > (u32)ECOLOGY_GEN_TOTAL_SLOTS) {
                return 0;
            }
        }
    }
    return (u16)cursor;
}

#endif
