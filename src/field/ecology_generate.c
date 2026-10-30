#include "ecology/ecology_generate.h"

#include "constants/generated/ecology_compat.h"
#include "ecology/ecology_compat_view.h"

#ifdef ECOLOGY_STANDALONE
#include <stdlib.h>
#include "ecology/ecology_compat_access.h"
#define ECO_GEN_DBG(stage) ((void)0)
#else
#include "config.h"
#include "constants/file.h"
#include "types.h"

static const EcologyCompatView *sEcoGenCompatView;

#define ECO_FAMILY_INFO(id) (sEcoGenCompatView->familyInfo[(id)])
#define ECO_GROUPS(gid) (sEcoGenCompatView->groups[(gid)])
#define ECO_GROUP_FLAGS(gid) (sEcoGenCompatView->groupFlags[(gid)])
#define ECO_METHOD_SLOTS(idx) (sEcoGenCompatView->methodSlots[(idx)])
#define ECO_LAND_OFFSETS(gid) (sEcoGenCompatView->landOffsets[(gid)])
#define ECO_LAND_ENTRIES(idx) (sEcoGenCompatView->landEntries[(idx)])
#define ECO_BUCKET_OFFSETS(idx) (sEcoGenCompatView->bucketOffsets[(idx)])
#define ECO_BUCKET_ENTRIES(idx) (sEcoGenCompatView->bucketEntries[(idx)])
#define ECO_LOCATION_TYPE_COUNT(gid) (sEcoGenCompatView->locationTypeCount[(gid)])

#define ECO_GEN_DBG(stage) ((void)0)
#endif

typedef struct EcologyEdgeRef {
    u8 groupId;
    u8 method;
    u8 flags;
} EcologyEdgeRef;

static u16 EcologyGroupMethodIndex(u8 groupId, u8 method)
{
    return (u16)groupId * (u16)ECOLOGY_METHOD_COUNT + (u16)method;
}

void EcologyRngInit(EcologyRng *rng, u32 seed)
{
    rng->state = seed ? seed : 1u;
}

u32 EcologyRngNext(EcologyRng *rng)
{
    rng->state = rng->state * 1664525u + 1013904223u;
    return rng->state;
}

static u16 EcologyRarityWeight(u8 rarity)
{
    /* Pick weight: Common highest, Very Rare lowest (÷3 per step toward rare). */
    static const u16 sTable[] = { 9, 27, 3, 1 };
    if (rarity >= (u8)(sizeof(sTable) / sizeof(sTable[0]))) {
        return 1;
    }
    return sTable[rarity];
}

static u16 EcologyPickWeightEx(u8 rarity, u8 flags, bool8 applyTypeBoost)
{
    u16 weight = EcologyRarityWeight(rarity);
    if (applyTypeBoost && (flags & ECOLOGY_EDGE_TYPE_MATCH)) {
        weight = (u16)(weight * 5u);
    }
    if (weight == 0) {
        weight = 1;
    }
    return weight;
}

static u16 EcologyPickWeight(u8 rarity, u8 flags)
{
    return EcologyPickWeightEx(rarity, flags, TRUE);
}

static bool8 EcologyFamilyAllowedOnMethod(u8 method, u8 rarity)
{
    switch (method) {
    case ECOLOGY_METHOD_OLD_ROD:
        return rarity == ECOLOGY_RARITY_COMMON;
    case ECOLOGY_METHOD_GOOD_ROD:
        return rarity == ECOLOGY_RARITY_COMMON || rarity == ECOLOGY_RARITY_NORMAL;
    case ECOLOGY_METHOD_SUPER_ROD:
        return TRUE;
    default:
        return TRUE;
    }
}

static u16 EcologyRandRange(EcologyRng *rng, u16 limit)
{
    u32 r;
    if (limit <= 1) {
        return 0;
    }
    r = EcologyRngNext(rng);
    return (u16)(r % (u32)limit);
}

static bool8 EcologySlotIndexValid(u16 slotIndex, u16 outSlotCapacity)
{
    return slotIndex < outSlotCapacity;
}

static void EcologyShuffleU16(EcologyRng *rng, u16 *items, u16 count)
{
    u16 i;
    for (i = count; i > 1; i--) {
        u16 j = EcologyRandRange(rng, i);
        u16 tmp = items[i - 1];
        items[i - 1] = items[j];
        items[j] = tmp;
    }
}

static bool8 EcologyGroupShuffleable(u8 groupId)
{
    if (groupId >= ECOLOGY_NUM_GROUPS) {
        return FALSE;
    }
    return (ECO_GROUP_FLAGS(groupId) & ECOLOGY_GROUP_FLAG_SHUFFLE) != 0;
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

static u16 EcologyLandEntryCount(u8 groupId)
{
    return ECO_LAND_OFFSETS(groupId + 1) - ECO_LAND_OFFSETS(groupId);
}

static EcologyGroupLandEntry EcologyLandEntryAt(u8 groupId, u16 index)
{
    return ECO_LAND_ENTRIES(ECO_LAND_OFFSETS(groupId) + index);
}

static u16 EcologyBucketEntryCount(u8 groupId, u8 method)
{
    u16 bucketIndex = EcologyGroupMethodIndex(groupId, method);
    return ECO_BUCKET_OFFSETS(bucketIndex + 1) - ECO_BUCKET_OFFSETS(bucketIndex);
}

static EcologyGroupBucketEntry EcologyBucketEntryAt(u8 groupId, u8 method, u16 index)
{
    u16 bucketIndex = EcologyGroupMethodIndex(groupId, method);
    return ECO_BUCKET_ENTRIES(ECO_BUCKET_OFFSETS(bucketIndex) + index);
}

static u16 EcologyCollectFamilyEdges(u16 familyId, EcologyEdgeRef *out, u16 outMax)
{
    u16 written = 0;
    u8 groupId;

    for (groupId = 0; groupId < ECOLOGY_NUM_GROUPS; groupId++) {
        u8 method;
        if (!EcologyGroupShuffleable(groupId)) {
            continue;
        }

        if (EcologyGroupMethodCapacity(groupId, ECOLOGY_METHOD_LAND) > 0) {
            u16 i;
            u16 count = EcologyLandEntryCount(groupId);
            for (i = 0; i < count; i++) {
                EcologyGroupLandEntry entry = EcologyLandEntryAt(groupId, i);
                if (entry.familyId != familyId) {
                    continue;
                }
                if (written >= outMax) {
                    return written;
                }
                out[written].groupId = groupId;
                out[written].method = ECOLOGY_METHOD_LAND;
                out[written].flags = entry.flags;
                written++;
            }
        }

        for (method = ECOLOGY_METHOD_SURF; method < ECOLOGY_METHOD_COUNT; method++) {
            u16 i;
            u16 count;
            if (EcologyGroupMethodCapacity(groupId, method) == 0) {
                continue;
            }
            count = EcologyBucketEntryCount(groupId, method);
            for (i = 0; i < count; i++) {
                EcologyGroupBucketEntry entry = EcologyBucketEntryAt(groupId, method, i);
                if (entry.familyId != familyId) {
                    continue;
                }
                if (!EcologyFamilyAllowedOnMethod(
                        method,
                        ECO_FAMILY_INFO(entry.familyId).rarity)) {
                    continue;
                }
                if (written >= outMax) {
                    return written;
                }
                out[written].groupId = groupId;
                out[written].method = method;
                out[written].flags = entry.flags;
                written++;
            }
        }
    }

    return written;
}

static u16 EcologyDedupeEdgeRefs(EcologyEdgeRef *edges, u16 count)
{
    u16 out = 0;
    u16 i;
    for (i = 0; i < count; i++) {
        u16 j;
        bool8 duplicate = FALSE;
        for (j = 0; j < out; j++) {
            if (edges[j].groupId == edges[i].groupId && edges[j].method == edges[i].method) {
                duplicate = TRUE;
                break;
            }
        }
        if (!duplicate) {
            edges[out++] = edges[i];
        }
    }
    return out;
}

static u8 EcologyResolveFamilyLandTimeMask(u16 familyId)
{
    u8 mask = ECO_FAMILY_INFO(familyId).landTimeMask;
    if (mask == 0) {
        return ECOLOGY_TIME_ALL;
    }
    return mask;
}

u8 EcologyEffectiveLandTimeMask(u8 groupId, u16 familyId)
{
    u8 familyMask = EcologyResolveFamilyLandTimeMask(familyId);
    u8 groupMask = ECO_GROUPS(groupId).landPeriodMask;
    if (groupMask == 0) {
        groupMask = ECOLOGY_TIME_ALL;
    }
    return familyMask & groupMask;
}

static bool8 EcologyTryAssignSlot(
    u16 familyId,
    u8 groupId,
    u8 method,
    u16 *outSlots,
    u8 *outLandSlotTimeMasks,
    u16 outSlotCapacity,
    const u16 *slotBases,
    u16 *bucketFill,
    u16 *familyPlacementCount)
{
    u16 layoutIndex = EcologyGroupMethodIndex(groupId, method);
    u16 capacity = EcologyGroupMethodCapacity(groupId, method);
    u16 base = slotBases[layoutIndex];
    u16 fill = bucketFill[layoutIndex];
    u16 slotIndex;

    if (capacity == 0 || fill >= capacity) {
        return FALSE;
    }
    if (!EcologyFamilyAllowedOnMethod(method, ECO_FAMILY_INFO(familyId).rarity)) {
        return FALSE;
    }

    slotIndex = (u16)(base + fill);
    if (!EcologySlotIndexValid(slotIndex, outSlotCapacity)) {
        return FALSE;
    }
    outSlots[slotIndex] = familyId;
    if (outLandSlotTimeMasks != NULL && method == ECOLOGY_METHOD_LAND) {
        outLandSlotTimeMasks[slotIndex] = EcologyEffectiveLandTimeMask(groupId, familyId);
    }
    bucketFill[layoutIndex]++;
    familyPlacementCount[familyId]++;
    return TRUE;
}

static bool8 EcologyLandFamilyHasTypeMatch(u8 groupId, u16 familyId)
{
    u16 i;
    u16 count = EcologyLandEntryCount(groupId);
    for (i = 0; i < count; i++) {
        EcologyGroupLandEntry entry = EcologyLandEntryAt(groupId, i);
        if (entry.familyId == familyId && (entry.flags & ECOLOGY_EDGE_TYPE_MATCH)) {
            return TRUE;
        }
    }
    return FALSE;
}

static u16 EcologyPickWeightedLandFamily(
    EcologyRng *rng,
    u8 groupId,
    bool8 requireTypeMatch,
    bool8 excludeTypeMatch,
    bool8 applyTypeBoost)
{
    u16 i;
    u16 count = EcologyLandEntryCount(groupId);
    u16 totalWeight = 0;
    u16 pick;
    u16 cursor;

    for (i = 0; i < count; i++) {
        EcologyGroupLandEntry entry = EcologyLandEntryAt(groupId, i);
        if (requireTypeMatch && !(entry.flags & ECOLOGY_EDGE_TYPE_MATCH)) {
            continue;
        }
        if (excludeTypeMatch && (entry.flags & ECOLOGY_EDGE_TYPE_MATCH)) {
            continue;
        }
        totalWeight += EcologyPickWeightEx(
            ECO_FAMILY_INFO(entry.familyId).rarity,
            entry.flags,
            applyTypeBoost);
    }
    if (totalWeight == 0) {
        return 0xFFFF;
    }
    pick = EcologyRandRange(rng, totalWeight);
    cursor = 0;
    for (i = 0; i < count; i++) {
        EcologyGroupLandEntry entry = EcologyLandEntryAt(groupId, i);
        u16 weight;
        if (requireTypeMatch && !(entry.flags & ECOLOGY_EDGE_TYPE_MATCH)) {
            continue;
        }
        if (excludeTypeMatch && (entry.flags & ECOLOGY_EDGE_TYPE_MATCH)) {
            continue;
        }
        weight = EcologyPickWeightEx(
            ECO_FAMILY_INFO(entry.familyId).rarity,
            entry.flags,
            applyTypeBoost);
        cursor += weight;
        if (pick < cursor) {
            return entry.familyId;
        }
    }
    return 0xFFFF;
}

static u8 EcologyTypedLandSlotTarget(u8 groupId)
{
    u8 typeCount = ECO_LOCATION_TYPE_COUNT(groupId);
    u16 landCapacity;
    u16 target;

    if (typeCount == 0) {
        return 0;
    }
    landCapacity = EcologyGroupMethodCapacity(groupId, ECOLOGY_METHOD_LAND);
    target = (u16)typeCount * (u16)ECOLOGY_TYPED_LAND_SLOTS_PER_TYPE;
    if (target > landCapacity) {
        target = landCapacity;
    }
    return (u8)target;
}

static u16 EcologyCountLandTypeMatchSlots(
    u8 groupId,
    const u16 *outSlots,
    u16 layoutIndex,
    const u16 *slotBases,
    u16 fill)
{
    u16 base = slotBases[layoutIndex];
    u16 i;
    u16 matched = 0;

    for (i = 0; i < fill; i++) {
        u16 familyId = outSlots[base + i];
        if (familyId != 0xFFFF && EcologyLandFamilyHasTypeMatch(groupId, familyId)) {
            matched++;
        }
    }
    return matched;
}

static void EcologyAssignLandSlot(
    u8 groupId,
    u16 familyId,
    u16 *outSlots,
    u8 *outLandSlotTimeMasks,
    u16 outSlotCapacity,
    u16 layoutIndex,
    const u16 *slotBases,
    u16 *bucketFill,
    u16 *familyPlacementCount)
{
    u16 slotIndex = (u16)(slotBases[layoutIndex] + bucketFill[layoutIndex]);

    if (!EcologySlotIndexValid(slotIndex, outSlotCapacity)) {
        return;
    }
    outSlots[slotIndex] = familyId;
    if (outLandSlotTimeMasks != NULL) {
        outLandSlotTimeMasks[slotIndex] = EcologyEffectiveLandTimeMask(groupId, familyId);
    }
    bucketFill[layoutIndex]++;
    familyPlacementCount[familyId]++;
}

static void EcologyFillLandBucket(
    EcologyRng *rng,
    u8 groupId,
    u16 *outSlots,
    u8 *outLandSlotTimeMasks,
    u16 outSlotCapacity,
    u16 layoutIndex,
    const u16 *slotBases,
    u16 *bucketFill,
    u16 *familyPlacementCount)
{
    u16 capacity = EcologyGroupMethodCapacity(groupId, ECOLOGY_METHOD_LAND);
    u8 typeTarget = EcologyTypedLandSlotTarget(groupId);
    bool8 typed = typeTarget > 0;
    u16 picked;
    u16 guard = 0;

    while (bucketFill[layoutIndex] < capacity) {
        u16 typeMatched = EcologyCountLandTypeMatchSlots(
            groupId, outSlots, layoutIndex, slotBases, bucketFill[layoutIndex]);

        if (++guard > (u16)(capacity + 8u)) {
            break;
        }

        if (typed && typeMatched < typeTarget) {
            picked = EcologyPickWeightedLandFamily(rng, groupId, TRUE, FALSE, FALSE);
            if (picked == 0xFFFF) {
                typed = FALSE;
                continue;
            }
        } else {
            bool8 excludeThemed = typed && typeMatched >= typeTarget;
            picked = EcologyPickWeightedLandFamily(
                rng, groupId, FALSE, excludeThemed, typed ? FALSE : TRUE);
            if (picked == 0xFFFF) {
                break;
            }
        }
        EcologyAssignLandSlot(
            groupId,
            picked,
            outSlots,
            outLandSlotTimeMasks,
            outSlotCapacity,
            layoutIndex,
            slotBases,
            bucketFill,
            familyPlacementCount);
    }
}

static u16 EcologyPickWeightedFamily(EcologyRng *rng, u8 groupId, u8 method)
{
    u16 i;
    u16 count;
    u16 totalWeight = 0;
    u16 pick;
    u16 cursor;

    if (method == ECOLOGY_METHOD_LAND) {
        return EcologyPickWeightedLandFamily(rng, groupId, FALSE, FALSE, TRUE);
    }

    count = EcologyBucketEntryCount(groupId, method);
    for (i = 0; i < count; i++) {
        EcologyGroupBucketEntry entry = EcologyBucketEntryAt(groupId, method, i);
        u8 rarity = ECO_FAMILY_INFO(entry.familyId).rarity;
        if (!EcologyFamilyAllowedOnMethod(method, rarity)) {
            continue;
        }
        totalWeight += EcologyPickWeight(rarity, entry.flags);
    }
    if (totalWeight == 0) {
        return 0xFFFF;
    }
    pick = EcologyRandRange(rng, totalWeight);
    cursor = 0;
    for (i = 0; i < count; i++) {
        EcologyGroupBucketEntry entry = EcologyBucketEntryAt(groupId, method, i);
        u8 rarity = ECO_FAMILY_INFO(entry.familyId).rarity;
        u16 weight;
        if (!EcologyFamilyAllowedOnMethod(method, rarity)) {
            continue;
        }
        weight = EcologyPickWeight(rarity, entry.flags);
        cursor += weight;
        if (pick < cursor) {
            return entry.familyId;
        }
    }
    return 0xFFFF;
}

#ifndef ECOLOGY_STANDALONE
static u16 EcologyGenBuildSlotLayoutLocal(u16 *slotBasesOut)
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

bool8 EcologyGenerateWorld(
    const EcologyCompatView *view,
    u32 seed,
    u16 *outSlots,
    u8 *outLandSlotTimeMasks,
    u16 outSlotCapacity,
    EcologyGenStats *statsOut)
{
    EcologyRng rng;
#ifdef ECOLOGY_STANDALONE
    u16 slotBases[ECOLOGY_NUM_GROUPS * ECOLOGY_METHOD_COUNT];
    u16 bucketFill[ECOLOGY_NUM_GROUPS * ECOLOGY_METHOD_COUNT];
    u16 familyPlacementCount[ECOLOGY_NUM_FAMILIES];
    u16 familyOrder[ECOLOGY_NUM_FAMILIES];
#else
    /* Heap scratch — Mom script runs with field overlay 131 loaded. */
    u16 *slotBases;
    u16 *bucketFill;
    u16 *familyPlacementCount;
    u16 *familyOrder;
    u32 layoutSlots = (u32)ECOLOGY_NUM_GROUPS * ECOLOGY_METHOD_COUNT;
#endif
    EcologyEdgeRef *edgeScratch;
    u16 totalSlots;
    u16 familyId;
    u8 groupId;

    if (outSlots == NULL) {
        ECO_GEN_DBG(22);
        return FALSE;
    }

#ifndef ECOLOGY_STANDALONE
    if (view == NULL) {
        ECO_GEN_DBG(23);
        return FALSE;
    }
    sEcoGenCompatView = view;

    slotBases = (u16 *)sys_AllocMemory(HEAPID_DEFAULT, layoutSlots * sizeof(u16));
    bucketFill = (u16 *)sys_AllocMemory(HEAPID_DEFAULT, layoutSlots * sizeof(u16));
    familyPlacementCount =
        (u16 *)sys_AllocMemory(HEAPID_DEFAULT, ECOLOGY_NUM_FAMILIES * sizeof(u16));
    familyOrder = (u16 *)sys_AllocMemory(HEAPID_DEFAULT, ECOLOGY_NUM_FAMILIES * sizeof(u16));
    if (slotBases == NULL || bucketFill == NULL || familyPlacementCount == NULL
        || familyOrder == NULL) {
        if (slotBases != NULL) {
            sys_FreeMemoryEz(slotBases);
        }
        if (bucketFill != NULL) {
            sys_FreeMemoryEz(bucketFill);
        }
        if (familyPlacementCount != NULL) {
            sys_FreeMemoryEz(familyPlacementCount);
        }
        if (familyOrder != NULL) {
            sys_FreeMemoryEz(familyOrder);
        }
        ECO_GEN_DBG(24);
        return FALSE;
    }
#endif

    EcologyRngInit(&rng, seed);
#ifdef ECOLOGY_STANDALONE
    totalSlots = EcologyGenBuildSlotLayout(slotBases);
#else
    totalSlots = EcologyGenBuildSlotLayoutLocal(slotBases);
#endif
    if (totalSlots == 0) {
#ifndef ECOLOGY_STANDALONE
        sys_FreeMemoryEz(slotBases);
        sys_FreeMemoryEz(bucketFill);
        sys_FreeMemoryEz(familyPlacementCount);
        sys_FreeMemoryEz(familyOrder);
#endif
        ECO_GEN_DBG(25);
        return FALSE;
    }
    if (totalSlots > outSlotCapacity) {
#ifndef ECOLOGY_STANDALONE
        sys_FreeMemoryEz(slotBases);
        sys_FreeMemoryEz(bucketFill);
        sys_FreeMemoryEz(familyPlacementCount);
        sys_FreeMemoryEz(familyOrder);
#endif
        ECO_GEN_DBG(27);
        return FALSE;
    }

    for (familyId = 0; familyId < ECOLOGY_NUM_FAMILIES; familyId++) {
        familyPlacementCount[familyId] = 0;
        familyOrder[familyId] = familyId;
    }
    for (groupId = 0; groupId < ECOLOGY_NUM_GROUPS; groupId++) {
        u8 method;
        for (method = 0; method < ECOLOGY_METHOD_COUNT; method++) {
            u16 index = EcologyGroupMethodIndex(groupId, method);
            u16 capacity = EcologyGroupMethodCapacity(groupId, method);
            u16 fill;
            bucketFill[index] = 0;
            for (fill = 0; fill < capacity; fill++) {
                u16 slotIndex = (u16)(slotBases[index] + fill);
                if (!EcologySlotIndexValid(slotIndex, outSlotCapacity)) {
                    break;
                }
                outSlots[slotIndex] = 0xFFFF;
                if (outLandSlotTimeMasks != NULL) {
                    outLandSlotTimeMasks[slotIndex] = 0;
                }
            }
        }
    }

    if (statsOut != NULL) {
        statsOut->familiesUnplaced = 0;
        statsOut->demandShortfall = 0;
        statsOut->bucketsPartiallyFilled = 0;
    }

#ifdef ECOLOGY_STANDALONE
    edgeScratch = (EcologyEdgeRef *)malloc(
        sizeof(EcologyEdgeRef) * ECOLOGY_GEN_MAX_FAMILY_EDGE_SCRATCH);
#else
    edgeScratch = (EcologyEdgeRef *)sys_AllocMemory(
        HEAPID_DEFAULT, sizeof(EcologyEdgeRef) * ECOLOGY_GEN_MAX_FAMILY_EDGE_SCRATCH);
#endif
    if (edgeScratch == NULL) {
#ifndef ECOLOGY_STANDALONE
        sys_FreeMemoryEz(slotBases);
        sys_FreeMemoryEz(bucketFill);
        sys_FreeMemoryEz(familyPlacementCount);
        sys_FreeMemoryEz(familyOrder);
#endif
        ECO_GEN_DBG(26);
        return FALSE;
    }

    EcologyShuffleU16(&rng, familyOrder, ECOLOGY_NUM_FAMILIES);

    for (familyId = 0; familyId < ECOLOGY_NUM_FAMILIES; familyId++) {
        u16 orderedFamily = familyOrder[familyId];
        const EcologyFamilyInfo *info = &ECO_FAMILY_INFO(orderedFamily);
        u16 edgeCount = EcologyCollectFamilyEdges(
            orderedFamily, edgeScratch, ECOLOGY_GEN_MAX_FAMILY_EDGE_SCRATCH);
        u16 demand = info->demand;
        u16 assignedPairs = 0;
        u16 edgeIndex;

        edgeCount = EcologyDedupeEdgeRefs(edgeScratch, edgeCount);

        for (edgeIndex = 0; edgeIndex < edgeCount && assignedPairs < demand; edgeIndex++) {
            u16 swapWith = (u16)(edgeIndex + EcologyRandRange(&rng, (u16)(edgeCount - edgeIndex)));
            EcologyEdgeRef tmp = edgeScratch[edgeIndex];
            edgeScratch[edgeIndex] = edgeScratch[swapWith];
            edgeScratch[swapWith] = tmp;
        }

        for (edgeIndex = 0; edgeIndex < edgeCount && assignedPairs < demand; edgeIndex++) {
            EcologyEdgeRef edge = edgeScratch[edgeIndex];

            if (EcologyTryAssignSlot(
                    orderedFamily,
                    edge.groupId,
                    edge.method,
                    outSlots,
                    outLandSlotTimeMasks,
                    outSlotCapacity,
                    slotBases,
                    bucketFill,
                    familyPlacementCount)) {
                assignedPairs++;
            }
        }

        if (assignedPairs < demand && statsOut != NULL) {
            statsOut->demandShortfall = (u16)(statsOut->demandShortfall + (demand - assignedPairs));
        }
    }

    for (groupId = 0; groupId < ECOLOGY_NUM_GROUPS; groupId++) {
        u8 method;
        if (!EcologyGroupShuffleable(groupId)) {
            continue;
        }
        for (method = 0; method < ECOLOGY_METHOD_COUNT; method++) {
            u16 layoutIndex = EcologyGroupMethodIndex(groupId, method);
            u16 capacity = EcologyGroupMethodCapacity(groupId, method);

            if (method == ECOLOGY_METHOD_LAND && capacity > 0) {
                EcologyFillLandBucket(
                    &rng,
                    groupId,
                    outSlots,
                    outLandSlotTimeMasks,
                    outSlotCapacity,
                    layoutIndex,
                    slotBases,
                    bucketFill,
                    familyPlacementCount);
            } else {
                u16 guard = 0;
                while (bucketFill[layoutIndex] < capacity) {
                    u16 picked = EcologyPickWeightedFamily(&rng, groupId, method);
                    u16 slotIndex;
                    if (++guard > (u16)(capacity + 8u)) {
                        break;
                    }
                    if (picked == 0xFFFF) {
                        break;
                    }
                    slotIndex = (u16)(slotBases[layoutIndex] + bucketFill[layoutIndex]);
                    if (!EcologySlotIndexValid(slotIndex, outSlotCapacity)) {
                        break;
                    }
                    outSlots[slotIndex] = picked;
                    if (outLandSlotTimeMasks != NULL && method == ECOLOGY_METHOD_LAND) {
                        outLandSlotTimeMasks[slotIndex] =
                            EcologyEffectiveLandTimeMask(groupId, picked);
                    }
                    bucketFill[layoutIndex]++;
                    familyPlacementCount[picked]++;
                }
            }
            if (statsOut != NULL && bucketFill[layoutIndex] < capacity) {
                statsOut->bucketsPartiallyFilled++;
            }
        }
    }

    for (familyId = 0; familyId < ECOLOGY_NUM_FAMILIES; familyId++) {
        if (familyPlacementCount[familyId] == 0 && statsOut != NULL) {
            statsOut->familiesUnplaced++;
        }
    }

#ifdef ECOLOGY_STANDALONE
    free(edgeScratch);
#else
    sys_FreeMemoryEz(edgeScratch);
    sys_FreeMemoryEz(slotBases);
    sys_FreeMemoryEz(bucketFill);
    sys_FreeMemoryEz(familyPlacementCount);
    sys_FreeMemoryEz(familyOrder);
#endif
    return TRUE;
}
