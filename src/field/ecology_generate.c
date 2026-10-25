#include "ecology/ecology_generate.h"

#include "constants/generated/ecology_compat.h"

#ifdef ECOLOGY_STANDALONE
#include <stdlib.h>
#else
#include "global.h"
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
    if (limit <= 1) {
        return 0;
    }
    return (u16)(EcologyRngNext(rng) % limit);
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
    return (sEcologyGroupFlags[groupId] & ECOLOGY_GROUP_FLAG_SHUFFLE) != 0;
}

static u8 EcologyGroupMethodCapacity(u8 groupId, u8 method)
{
    u16 index = EcologyGroupMethodIndex(groupId, method);
    return sEcologyGroupMethodSlots[index];
}

static u16 EcologyLandEntryCount(u8 groupId)
{
    return sEcologyGroupLandOffsets[groupId + 1] - sEcologyGroupLandOffsets[groupId];
}

static EcologyGroupLandEntry EcologyLandEntryAt(u8 groupId, u16 index)
{
    return sEcologyGroupLandEntries[sEcologyGroupLandOffsets[groupId] + index];
}

static u16 EcologyBucketEntryCount(u8 groupId, u8 method)
{
    u16 bucketIndex = EcologyGroupMethodIndex(groupId, method);
    return sEcologyGroupBucketOffsets[bucketIndex + 1] - sEcologyGroupBucketOffsets[bucketIndex];
}

static EcologyGroupBucketEntry EcologyBucketEntryAt(u8 groupId, u8 method, u16 index)
{
    u16 bucketIndex = EcologyGroupMethodIndex(groupId, method);
    return sEcologyGroupBucketEntries[sEcologyGroupBucketOffsets[bucketIndex] + index];
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
                        sEcologyFamilyInfo[entry.familyId].rarity)) {
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
    u8 mask = sEcologyFamilyInfo[familyId].landTimeMask;
    if (mask == 0) {
        return ECOLOGY_TIME_ALL;
    }
    return mask;
}

u8 EcologyEffectiveLandTimeMask(u8 groupId, u16 familyId)
{
    u8 familyMask = EcologyResolveFamilyLandTimeMask(familyId);
    u8 groupMask = sEcologyGroups[groupId].landPeriodMask;
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
    if (!EcologyFamilyAllowedOnMethod(method, sEcologyFamilyInfo[familyId].rarity)) {
        return FALSE;
    }

    slotIndex = (u16)(base + fill);
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
            sEcologyFamilyInfo[entry.familyId].rarity,
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
            sEcologyFamilyInfo[entry.familyId].rarity,
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
    u8 typeCount = sEcologyGroupLocationTypeCount[groupId];
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
    u16 layoutIndex,
    const u16 *slotBases,
    u16 *bucketFill,
    u16 *familyPlacementCount)
{
    u16 slotIndex = (u16)(slotBases[layoutIndex] + bucketFill[layoutIndex]);
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
    u16 layoutIndex,
    const u16 *slotBases,
    u16 *bucketFill,
    u16 *familyPlacementCount)
{
    u16 capacity = EcologyGroupMethodCapacity(groupId, ECOLOGY_METHOD_LAND);
    u8 typeTarget = EcologyTypedLandSlotTarget(groupId);
    bool8 typed = typeTarget > 0;
    u16 picked;

    while (bucketFill[layoutIndex] < capacity) {
        u16 typeMatched = EcologyCountLandTypeMatchSlots(
            groupId, outSlots, layoutIndex, slotBases, bucketFill[layoutIndex]);

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
        u8 rarity = sEcologyFamilyInfo[entry.familyId].rarity;
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
        u8 rarity = sEcologyFamilyInfo[entry.familyId].rarity;
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

u16 EcologyGenSlotLayoutBase(u8 groupId, u8 method, const u16 *slotBases)
{
    return slotBases[EcologyGroupMethodIndex(groupId, method)];
}

u16 EcologyGenBuildSlotLayout(u16 *slotBasesOut)
{
    u16 cursor = 0;
    u8 groupId;
    for (groupId = 0; groupId < ECOLOGY_NUM_GROUPS; groupId++) {
        u8 method;
        for (method = 0; method < ECOLOGY_METHOD_COUNT; method++) {
            u16 index = EcologyGroupMethodIndex(groupId, method);
            slotBasesOut[index] = cursor;
            cursor = (u16)(cursor + EcologyGroupMethodCapacity(groupId, method));
        }
    }
    return cursor;
}

bool8 EcologyGenerateWorld(
    u32 seed,
    u16 *outSlots,
    u8 *outLandSlotTimeMasks,
    u16 outSlotCapacity,
    EcologyGenStats *statsOut)
{
    EcologyRng rng;
    u16 slotBases[ECOLOGY_NUM_GROUPS * ECOLOGY_METHOD_COUNT];
    u16 bucketFill[ECOLOGY_NUM_GROUPS * ECOLOGY_METHOD_COUNT];
    u16 familyPlacementCount[ECOLOGY_NUM_FAMILIES];
    u16 familyOrder[ECOLOGY_NUM_FAMILIES];
#ifdef ECOLOGY_STANDALONE
    EcologyEdgeRef *edgeScratch;
#else
    static EcologyEdgeRef sEdgeScratch[ECOLOGY_NUM_EDGES];
#endif
    u16 totalSlots;
    u16 familyId;
    u8 groupId;

    if (outSlots == NULL) {
        return FALSE;
    }

    EcologyRngInit(&rng, seed);
    totalSlots = EcologyGenBuildSlotLayout(slotBases);
    if (totalSlots > outSlotCapacity) {
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
    edgeScratch = (EcologyEdgeRef *)malloc(sizeof(EcologyEdgeRef) * ECOLOGY_NUM_EDGES);
    if (edgeScratch == NULL) {
        return FALSE;
    }
#else
    edgeScratch = sEdgeScratch;
#endif

    EcologyShuffleU16(&rng, familyOrder, ECOLOGY_NUM_FAMILIES);

    for (familyId = 0; familyId < ECOLOGY_NUM_FAMILIES; familyId++) {
        u16 orderedFamily = familyOrder[familyId];
        const EcologyFamilyInfo *info = &sEcologyFamilyInfo[orderedFamily];
        u16 edgeCount = EcologyCollectFamilyEdges(orderedFamily, edgeScratch, ECOLOGY_NUM_EDGES);
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
                    layoutIndex,
                    slotBases,
                    bucketFill,
                    familyPlacementCount);
            } else {
                while (bucketFill[layoutIndex] < capacity) {
                    u16 picked = EcologyPickWeightedFamily(&rng, groupId, method);
                    u16 slotIndex;
                    if (picked == 0xFFFF) {
                        break;
                    }
                    slotIndex = (u16)(slotBases[layoutIndex] + bucketFill[layoutIndex]);
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
#endif
    return TRUE;
}
