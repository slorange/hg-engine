#include "ecology/ecology_generate.h"

#include "constants/generated/ecology_compat.h"
#include "ecology/ecology_compat_access.h"

#ifdef ECOLOGY_STANDALONE
#include <stdlib.h>
#define ECO_GEN_DBG(stage) ((void)0)
#else
#include "config.h"
#include "constants/file.h"
#include "types.h"
#if defined(IMPLEMENT_ECOLOGY_GENERATION) && defined(DEBUG_ECOLOGY_GEN_LEVELS)
#include "ecology/ecology_script.h"
#define ECO_GEN_DBG(stage) EcologySetGenDebugStage(stage)
#else
#define ECO_GEN_DBG(stage) ((void)0)
#endif
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
    /* Phase 4 fill only (Very Rare excluded at pick sites): Normal / Common / Rare. */
    static const u16 sTable[] = { 3, 9, 1, 0 };
    if (rarity >= (u8)(sizeof(sTable) / sizeof(sTable[0]))) {
        return 1;
    }
    return sTable[rarity];
}

static u16 EcologyPickWeight(u8 rarity)
{
    u16 weight = EcologyRarityWeight(rarity);
    if (weight == 0) {
        weight = 1;
    }
    return weight;
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

static bool8 EcologyFamilyListedOnLand(u8 groupId, u16 familyId)
{
    u16 i;
    u16 count = EcologyLandEntryCount(groupId);
    for (i = 0; i < count; i++) {
        if (EcologyLandEntryAt(groupId, i).familyId == familyId) {
            return TRUE;
        }
    }
    return FALSE;
}

static bool8 EcologyFamilyListedInBucket(u8 groupId, u8 method, u16 familyId)
{
    u16 i;
    u16 count = EcologyBucketEntryCount(groupId, method);
    for (i = 0; i < count; i++) {
        if (EcologyBucketEntryAt(groupId, method, i).familyId == familyId) {
            return TRUE;
        }
    }
    return FALSE;
}

static bool8 EcologyFamilyHasCompatAtGroupMethod(u8 groupId, u16 familyId, u8 method, bool8 forRequired)
{
    if (method == ECOLOGY_METHOD_LAND) {
        return EcologyFamilyListedOnLand(groupId, familyId);
    }
    if (!forRequired
        && !EcologyFamilyAllowedOnMethod(method, ECO_FAMILY_INFO(familyId).rarity)) {
        return FALSE;
    }
    return EcologyFamilyListedInBucket(groupId, method, familyId);
}

static bool8 EcologyTryAssignSlotEx(
    u16 familyId,
    u8 groupId,
    u8 method,
    u16 *outSlots,
    u8 *outLandSlotTimeMasks,
    u16 outSlotCapacity,
    const u16 *slotBases,
    u16 *bucketFill,
    u16 *familyPlacementCount,
    bool8 ignoreRodRarity)
{
    u16 layoutIndex = EcologyGroupMethodIndex(groupId, method);
    u16 capacity = EcologyGroupMethodCapacity(groupId, method);
    u16 base = slotBases[layoutIndex];
    u16 fill = bucketFill[layoutIndex];
    u16 slotIndex;

    if (capacity == 0 || fill >= capacity) {
        return FALSE;
    }
    if (!EcologyFamilyHasCompatAtGroupMethod(groupId, familyId, method, ignoreRodRarity)) {
        return FALSE;
    }
    if (!ignoreRodRarity
        && !EcologyFamilyAllowedOnMethod(method, ECO_FAMILY_INFO(familyId).rarity)) {
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
    return EcologyTryAssignSlotEx(
        familyId,
        groupId,
        method,
        outSlots,
        outLandSlotTimeMasks,
        outSlotCapacity,
        slotBases,
        bucketFill,
        familyPlacementCount,
        FALSE);
}

static u8 EcologyPartnerFamilyId(u16 familyId)
{
    return ECO_FAMILY_INFO(familyId).partnerFamilyId;
}

static bool8 EcologyFamilyHasPairing(u16 familyId)
{
    return EcologyPartnerFamilyId(familyId) != ECOLOGY_FAMILY_NO_PARTNER;
}

static bool8 EcologyFamilyOnGroup(
    u8 groupId,
    u16 familyId,
    const u16 *outSlots,
    const u16 *slotBases,
    const u16 *bucketFill)
{
    u8 method;
    for (method = 0; method < ECOLOGY_METHOD_COUNT; method++) {
        u16 layoutIndex = EcologyGroupMethodIndex(groupId, method);
        u16 fill = bucketFill[layoutIndex];
        u16 base = slotBases[layoutIndex];
        u16 i;
        for (i = 0; i < fill; i++) {
            if (outSlots[base + i] == familyId) {
                return TRUE;
            }
        }
    }
    return FALSE;
}

static u8 EcologyCountDistinctGroups(
    u16 familyId,
    const u16 *outSlots,
    const u16 *slotBases,
    const u16 *bucketFill)
{
    u8 groupId;
    u8 count = 0;

    for (groupId = 0; groupId < ECOLOGY_NUM_GROUPS; groupId++) {
        if (EcologyFamilyOnGroup(groupId, familyId, outSlots, slotBases, bucketFill)) {
            count++;
        }
    }
    return count;
}

static u8 EcologyFamilyRouteBaseline(u8 rarity)
{
    /* Index = ECOLOGY_RARITY_* (Normal, Common, Rare, Very Rare). */
    static const u8 sBaseline[] = { 3, 5, 2, 1 };
    if (rarity >= (u8)(sizeof(sBaseline) / sizeof(sBaseline[0]))) {
        return 5;
    }
    return sBaseline[rarity];
}

static bool8 EcologyFamilyMayUseNewGroup(
    u16 familyId,
    u8 groupId,
    const u16 *outSlots,
    const u16 *slotBases,
    const u16 *bucketFill)
{
    u8 rarity;

    if (EcologyFamilyOnGroup(groupId, familyId, outSlots, slotBases, bucketFill)) {
        return TRUE;
    }
    rarity = ECO_FAMILY_INFO(familyId).rarity;
    if (rarity == ECOLOGY_RARITY_VERY_RARE
        && EcologyCountDistinctGroups(familyId, outSlots, slotBases, bucketFill) >= 1) {
        return FALSE;
    }
    return TRUE;
}

static bool8 EcologyBucketHasSpace(u8 groupId, u8 method, const u16 *bucketFill)
{
    u16 layoutIndex = EcologyGroupMethodIndex(groupId, method);
    return bucketFill[layoutIndex] < EcologyGroupMethodCapacity(groupId, method);
}

static bool8 EcologyCanPlacePartnerOnGroup(
    u8 groupId,
    u16 partnerId,
    const u16 *bucketFill)
{
    u8 method;
    if (partnerId == 0xFFFF) {
        return FALSE;
    }
    for (method = 0; method < ECOLOGY_METHOD_COUNT; method++) {
        if (!EcologyBucketHasSpace(groupId, method, bucketFill)) {
            continue;
        }
        if (EcologyFamilyHasCompatAtGroupMethod(groupId, partnerId, method, FALSE)) {
            return TRUE;
        }
    }
    return FALSE;
}

static bool8 EcologyTryPlacePartnerOnGroup(
    u16 partnerId,
    u8 groupId,
    u8 preferredMethod,
    u16 *outSlots,
    u8 *outLandSlotTimeMasks,
    u16 outSlotCapacity,
    const u16 *slotBases,
    u16 *bucketFill,
    u16 *familyPlacementCount)
{
    u8 method;
    if (partnerId == 0xFFFF || EcologyFamilyOnGroup(groupId, partnerId, outSlots, slotBases, bucketFill)) {
        return TRUE;
    }
    if (!EcologyFamilyMayUseNewGroup(
            partnerId, groupId, outSlots, slotBases, bucketFill)) {
        return FALSE;
    }
    if (preferredMethod < ECOLOGY_METHOD_COUNT
        && EcologyTryAssignSlot(
            partnerId,
            groupId,
            preferredMethod,
            outSlots,
            outLandSlotTimeMasks,
            outSlotCapacity,
            slotBases,
            bucketFill,
            familyPlacementCount)) {
        return TRUE;
    }
    for (method = 0; method < ECOLOGY_METHOD_COUNT; method++) {
        if (method == preferredMethod) {
            continue;
        }
        if (EcologyTryAssignSlot(
                partnerId,
                groupId,
                method,
                outSlots,
                outLandSlotTimeMasks,
                outSlotCapacity,
                slotBases,
                bucketFill,
                familyPlacementCount)) {
            return TRUE;
        }
    }
    return FALSE;
}

static bool8 EcologyTryAssignWithPairingEx(
    u16 familyId,
    u8 groupId,
    u8 method,
    u16 *outSlots,
    u8 *outLandSlotTimeMasks,
    u16 outSlotCapacity,
    const u16 *slotBases,
    u16 *bucketFill,
    u16 *familyPlacementCount,
    bool8 ignoreRodRarity)
{
    u16 layoutIndex = EcologyGroupMethodIndex(groupId, method);
    u16 fillBefore = bucketFill[layoutIndex];
    u16 slotIndex;
    u8 partner;

    if (!EcologyFamilyMayUseNewGroup(
            familyId, groupId, outSlots, slotBases, bucketFill)) {
        return FALSE;
    }

    if (!EcologyTryAssignSlotEx(
            familyId,
            groupId,
            method,
            outSlots,
            outLandSlotTimeMasks,
            outSlotCapacity,
            slotBases,
            bucketFill,
            familyPlacementCount,
            ignoreRodRarity)) {
        return FALSE;
    }

    partner = EcologyPartnerFamilyId(familyId);
    if (partner != ECOLOGY_FAMILY_NO_PARTNER
        && !EcologyFamilyMayUseNewGroup(
            partner, groupId, outSlots, slotBases, bucketFill)
        && !EcologyFamilyOnGroup(groupId, partner, outSlots, slotBases, bucketFill)) {
        slotIndex = (u16)(slotBases[layoutIndex] + fillBefore);
        outSlots[slotIndex] = 0xFFFF;
        if (outLandSlotTimeMasks != NULL && method == ECOLOGY_METHOD_LAND) {
            outLandSlotTimeMasks[slotIndex] = 0;
        }
        bucketFill[layoutIndex] = fillBefore;
        if (familyPlacementCount[familyId] > 0) {
            familyPlacementCount[familyId]--;
        }
        return FALSE;
    }
    if (partner != ECOLOGY_FAMILY_NO_PARTNER
        && !EcologyTryPlacePartnerOnGroup(
            partner,
            groupId,
            method,
            outSlots,
            outLandSlotTimeMasks,
            outSlotCapacity,
            slotBases,
            bucketFill,
            familyPlacementCount)) {
        slotIndex = (u16)(slotBases[layoutIndex] + fillBefore);
        outSlots[slotIndex] = 0xFFFF;
        if (outLandSlotTimeMasks != NULL && method == ECOLOGY_METHOD_LAND) {
            outLandSlotTimeMasks[slotIndex] = 0;
        }
        bucketFill[layoutIndex] = fillBefore;
        if (familyPlacementCount[familyId] > 0) {
            familyPlacementCount[familyId]--;
        }
        return FALSE;
    }
    return TRUE;
}

static bool8 EcologyTryAssignWithPairing(
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
    return EcologyTryAssignWithPairingEx(
        familyId,
        groupId,
        method,
        outSlots,
        outLandSlotTimeMasks,
        outSlotCapacity,
        slotBases,
        bucketFill,
        familyPlacementCount,
        FALSE);
}

static bool8 EcologyFamilyEligibleForFill(
    u8 groupId,
    u16 familyId,
    u16 remainSlots,
    const u16 *outSlots,
    const u16 *slotBases,
    const u16 *bucketFill)
{
    u8 partner;

    if (!EcologyFamilyHasPairing(familyId)) {
        return TRUE;
    }
    if (remainSlots <= 1) {
        return FALSE;
    }
    partner = EcologyPartnerFamilyId(familyId);
    if (EcologyFamilyOnGroup(groupId, partner, outSlots, slotBases, bucketFill)) {
        return TRUE;
    }
    return EcologyCanPlacePartnerOnGroup(groupId, partner, bucketFill);
}

static void EcologyAssignRequiredRoutes(
    u16 *outSlots,
    u8 *outLandSlotTimeMasks,
    u16 outSlotCapacity,
    const u16 *slotBases,
    u16 *bucketFill,
    u16 *familyPlacementCount,
    EcologyGenStats *statsOut)
{
    u16 routeIndex;
    static const u8 sRequiredMethodOrder[] = {
        ECOLOGY_METHOD_LAND,
        ECOLOGY_METHOD_SURF,
        ECOLOGY_METHOD_OLD_ROD,
        ECOLOGY_METHOD_ROCK_SMASH,
        ECOLOGY_METHOD_HEADBUTT,
    };
    u8 orderIndex;

    for (routeIndex = 0; routeIndex < ECO_REQUIRED_ROUTE_COUNT; routeIndex++) {
        EcologyRequiredRoute route = ECO_REQUIRED_ROUTE(routeIndex);
        u16 familyId = route.familyId;
        u8 groupId = route.groupId;

        for (orderIndex = 0; orderIndex < (u8)(sizeof(sRequiredMethodOrder) / sizeof(sRequiredMethodOrder[0]));
             orderIndex++) {
            u8 method = sRequiredMethodOrder[orderIndex];
            if (!EcologyFamilyHasCompatAtGroupMethod(groupId, familyId, method, TRUE)) {
                continue;
            }
            if (!EcologyTryAssignWithPairingEx(
                    familyId,
                    groupId,
                    method,
                    outSlots,
                    outLandSlotTimeMasks,
                    outSlotCapacity,
                    slotBases,
                    bucketFill,
                    familyPlacementCount,
                    TRUE)) {
                if (statsOut != NULL) {
                    statsOut->requiredRouteMiss++;
                }
            }
        }
    }
}

static bool8 EcologyFamilyMatchesRouteFilter(u8 rarity, u8 filter)
{
    if (filter == 0) {
        return TRUE;
    }
    if (filter == 1) {
        return rarity != ECOLOGY_RARITY_VERY_RARE;
    }
    if (filter == 2) {
        return rarity <= ECOLOGY_RARITY_COMMON;
    }
    return rarity == ECOLOGY_RARITY_COMMON;
}

static void EcologyShuffleEdgeRefs(EcologyRng *rng, EcologyEdgeRef *edges, u16 count)
{
    u16 i;
    for (i = count; i > 1; i--) {
        u16 j = EcologyRandRange(rng, i);
        EcologyEdgeRef tmp = edges[i - 1];
        edges[i - 1] = edges[j];
        edges[j] = tmp;
    }
}

static u16 EcologyPartitionTypeMatchEdges(EcologyEdgeRef *edges, u16 count)
{
    u16 typed = 0;
    u16 i;
    for (i = 0; i < count; i++) {
        if (edges[i].flags & ECOLOGY_EDGE_TYPE_MATCH) {
            if (typed != i) {
                EcologyEdgeRef tmp = edges[typed];
                edges[typed] = edges[i];
                edges[i] = tmp;
            }
            typed++;
        }
    }
    return typed;
}

static bool8 EcologyTryShuffledEdges(
    EcologyRng *rng,
    u16 familyId,
    EcologyEdgeRef *edges,
    u16 count,
    u16 *outSlots,
    u8 *outLandSlotTimeMasks,
    u16 outSlotCapacity,
    const u16 *slotBases,
    u16 *bucketFill,
    u16 *familyPlacementCount)
{
    u16 edgeIndex;
    if (count == 0) {
        return FALSE;
    }
    EcologyShuffleEdgeRefs(rng, edges, count);
    for (edgeIndex = 0; edgeIndex < count; edgeIndex++) {
        EcologyEdgeRef edge = edges[edgeIndex];
        if (EcologyTryAssignWithPairing(
                familyId,
                edge.groupId,
                edge.method,
                outSlots,
                outLandSlotTimeMasks,
                outSlotCapacity,
                slotBases,
                bucketFill,
                familyPlacementCount)) {
            return TRUE;
        }
    }
    return FALSE;
}

static bool8 EcologyAssignFamilyViaEdges(
    EcologyRng *rng,
    u16 familyId,
    bool8 onlyNewGroups,
    u16 *outSlots,
    u8 *outLandSlotTimeMasks,
    u16 outSlotCapacity,
    const u16 *slotBases,
    u16 *bucketFill,
    u16 *familyPlacementCount,
    EcologyEdgeRef *edgeScratch,
    u16 edgeScratchMax)
{
    u16 edgeCount;
    u16 edgeIndex;
    u16 kept;

    edgeCount = EcologyCollectFamilyEdges(familyId, edgeScratch, edgeScratchMax);
    edgeCount = EcologyDedupeEdgeRefs(edgeScratch, edgeCount);
    if (onlyNewGroups) {
        kept = 0;
        for (edgeIndex = 0; edgeIndex < edgeCount; edgeIndex++) {
            EcologyEdgeRef edge = edgeScratch[edgeIndex];
            if (!EcologyFamilyOnGroup(
                    edge.groupId, familyId, outSlots, slotBases, bucketFill)) {
                edgeScratch[kept++] = edge;
            }
        }
        edgeCount = kept;
    }
    if (edgeCount == 0) {
        return FALSE;
    }

    {
        u16 typedCount = EcologyPartitionTypeMatchEdges(edgeScratch, edgeCount);
        u16 otherCount = (u16)(edgeCount - typedCount);
        bool8 typeFirst = (EcologyRandRange(rng, 2) == 0);

        if (typeFirst) {
            if (EcologyTryShuffledEdges(
                    rng,
                    familyId,
                    edgeScratch,
                    typedCount,
                    outSlots,
                    outLandSlotTimeMasks,
                    outSlotCapacity,
                    slotBases,
                    bucketFill,
                    familyPlacementCount)) {
                return TRUE;
            }
            return EcologyTryShuffledEdges(
                rng,
                familyId,
                edgeScratch + typedCount,
                otherCount,
                outSlots,
                outLandSlotTimeMasks,
                outSlotCapacity,
                slotBases,
                bucketFill,
                familyPlacementCount);
        }
        if (EcologyTryShuffledEdges(
                rng,
                familyId,
                edgeScratch + typedCount,
                otherCount,
                outSlots,
                outLandSlotTimeMasks,
                outSlotCapacity,
                slotBases,
                bucketFill,
                familyPlacementCount)) {
            return TRUE;
        }
        return EcologyTryShuffledEdges(
            rng,
            familyId,
            edgeScratch,
            typedCount,
            outSlots,
            outLandSlotTimeMasks,
            outSlotCapacity,
            slotBases,
            bucketFill,
            familyPlacementCount);
    }
    return FALSE;
}

static void EcologyPlaceUnplacedFamilies(
    EcologyRng *rng,
    u16 *outSlots,
    u8 *outLandSlotTimeMasks,
    u16 outSlotCapacity,
    const u16 *slotBases,
    u16 *bucketFill,
    u16 *familyPlacementCount,
    u16 *familyOrder,
    EcologyEdgeRef *edgeScratch,
    u16 edgeScratchMax)
{
    u16 pass;
    for (pass = 0; pass < ECOLOGY_NUM_FAMILIES; pass++) {
        u16 familyId = familyOrder[pass];

        if (EcologyCountDistinctGroups(
                familyId, outSlots, slotBases, bucketFill)
            > 0) {
            continue;
        }

        (void)EcologyAssignFamilyViaEdges(
            rng,
            familyId,
            FALSE,
            outSlots,
            outLandSlotTimeMasks,
            outSlotCapacity,
            slotBases,
            bucketFill,
            familyPlacementCount,
            edgeScratch,
            edgeScratchMax);
    }
}

static void EcologyRunRouteTargetPasses(
    EcologyRng *rng,
    u16 *outSlots,
    u8 *outLandSlotTimeMasks,
    u16 outSlotCapacity,
    const u16 *slotBases,
    u16 *bucketFill,
    u16 *familyPlacementCount,
    u16 *familyOrder,
    EcologyEdgeRef *edgeScratch,
    u16 edgeScratchMax)
{
    static const u8 sPassTarget[] = { 1, 2, 3, 5 };
    static const u8 sPassFilter[] = { 0, 1, 1, 2 };
    u16 passIndex;

    for (passIndex = 0; passIndex < (u16)(sizeof(sPassTarget) / sizeof(sPassTarget[0])); passIndex++) {
        u8 target = sPassTarget[passIndex];
        u8 filter = sPassFilter[passIndex];
        bool8 progress;
        u16 guard = 0;

        do {
            u16 orderIndex;
            progress = FALSE;
            EcologyShuffleU16(rng, familyOrder, ECOLOGY_NUM_FAMILIES);

            for (orderIndex = 0; orderIndex < ECOLOGY_NUM_FAMILIES; orderIndex++) {
                u16 familyId = familyOrder[orderIndex];
                u8 rarity = ECO_FAMILY_INFO(familyId).rarity;
                u8 routeBaseline = EcologyFamilyRouteBaseline(rarity);
                u8 routeCount = EcologyCountDistinctGroups(
                    familyId, outSlots, slotBases, bucketFill);

                if (target > routeBaseline || routeCount >= target) {
                    continue;
                }
                if (!EcologyFamilyMatchesRouteFilter(rarity, filter)) {
                    continue;
                }
                if (EcologyAssignFamilyViaEdges(
                        rng,
                        familyId,
                        TRUE,
                        outSlots,
                        outLandSlotTimeMasks,
                        outSlotCapacity,
                        slotBases,
                        bucketFill,
                        familyPlacementCount,
                        edgeScratch,
                        edgeScratchMax)) {
                    progress = TRUE;
                }
            }
        } while (progress && ++guard < (u16)(ECOLOGY_NUM_FAMILIES * 4u));
    }
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
    bool8 excludeVeryRare,
    u16 remainSlots,
    const u16 *outSlots,
    const u16 *slotBases,
    const u16 *bucketFill)
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
        if (excludeVeryRare
            && ECO_FAMILY_INFO(entry.familyId).rarity == ECOLOGY_RARITY_VERY_RARE) {
            continue;
        }
        if (!EcologyFamilyEligibleForFill(
                groupId, entry.familyId, remainSlots, outSlots, slotBases, bucketFill)) {
            continue;
        }
        totalWeight += EcologyPickWeight(ECO_FAMILY_INFO(entry.familyId).rarity);
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
        if (excludeVeryRare
            && ECO_FAMILY_INFO(entry.familyId).rarity == ECOLOGY_RARITY_VERY_RARE) {
            continue;
        }
        if (!EcologyFamilyEligibleForFill(
                groupId, entry.familyId, remainSlots, outSlots, slotBases, bucketFill)) {
            continue;
        }
        weight = EcologyPickWeight(ECO_FAMILY_INFO(entry.familyId).rarity);
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
        u16 remainSlots = (u16)(capacity - bucketFill[layoutIndex]);
        u16 typeMatched = EcologyCountLandTypeMatchSlots(
            groupId, outSlots, layoutIndex, slotBases, bucketFill[layoutIndex]);

        if (++guard > (u16)(capacity + 8u)) {
            break;
        }

        if (typed && typeMatched < typeTarget) {
            picked = EcologyPickWeightedLandFamily(
                rng,
                groupId,
                TRUE,
                FALSE,
                TRUE,
                remainSlots,
                outSlots,
                slotBases,
                bucketFill);
            if (picked == 0xFFFF) {
                typed = FALSE;
                continue;
            }
        } else {
            bool8 excludeThemed = typed && typeMatched >= typeTarget;
            picked = EcologyPickWeightedLandFamily(
                rng,
                groupId,
                FALSE,
                excludeThemed,
                TRUE,
                remainSlots,
                outSlots,
                slotBases,
                bucketFill);
            if (picked == 0xFFFF) {
                break;
            }
        }
        if (!EcologyTryAssignWithPairing(
                picked,
                groupId,
                ECOLOGY_METHOD_LAND,
                outSlots,
                outLandSlotTimeMasks,
                outSlotCapacity,
                slotBases,
                bucketFill,
                familyPlacementCount)) {
            continue;
        }
    }
}

static u16 EcologyPickWeightedFamily(
    EcologyRng *rng,
    u8 groupId,
    u8 method,
    bool8 excludeVeryRare,
    u16 remainSlots,
    const u16 *outSlots,
    const u16 *slotBases,
    const u16 *bucketFill)
{
    u16 i;
    u16 count;
    u16 totalWeight = 0;
    u16 pick;
    u16 cursor;

    if (method == ECOLOGY_METHOD_LAND) {
        return EcologyPickWeightedLandFamily(
            rng,
            groupId,
            FALSE,
            FALSE,
            excludeVeryRare,
            remainSlots,
            outSlots,
            slotBases,
            bucketFill);
    }

    count = EcologyBucketEntryCount(groupId, method);
    for (i = 0; i < count; i++) {
        EcologyGroupBucketEntry entry = EcologyBucketEntryAt(groupId, method, i);
        u8 rarity = ECO_FAMILY_INFO(entry.familyId).rarity;
        if (excludeVeryRare && rarity == ECOLOGY_RARITY_VERY_RARE) {
            continue;
        }
        if (!EcologyFamilyAllowedOnMethod(method, rarity)) {
            continue;
        }
        if (!EcologyFamilyEligibleForFill(
                groupId, entry.familyId, remainSlots, outSlots, slotBases, bucketFill)) {
            continue;
        }
        totalWeight += EcologyPickWeight(rarity);
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
        if (excludeVeryRare && rarity == ECOLOGY_RARITY_VERY_RARE) {
            continue;
        }
        if (!EcologyFamilyAllowedOnMethod(method, rarity)) {
            continue;
        }
        if (!EcologyFamilyEligibleForFill(
                groupId, entry.familyId, remainSlots, outSlots, slotBases, bucketFill)) {
            continue;
        }
        weight = EcologyPickWeight(rarity);
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
    (void)view;
    u16 slotBases[ECOLOGY_NUM_GROUPS * ECOLOGY_METHOD_COUNT];
    u16 bucketFill[ECOLOGY_NUM_GROUPS * ECOLOGY_METHOD_COUNT];
    u16 familyPlacementCount[ECOLOGY_NUM_FAMILIES];
    u16 familyOrder[ECOLOGY_NUM_FAMILIES];
#else
    /* Mom gen: field overlay 131 — keep scratch off the script stack. */
    (void)view;
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
    if (view == NULL || gEcologyCompatView == NULL) {
        ECO_GEN_DBG(23);
        return FALSE;
    }

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
    totalSlots = EcologyGenBuildSlotLayout(slotBases);
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
        statsOut->requiredRouteMiss = 0;
        statsOut->pairingShortfall = 0;
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

    EcologyAssignRequiredRoutes(
        outSlots,
        outLandSlotTimeMasks,
        outSlotCapacity,
        slotBases,
        bucketFill,
        familyPlacementCount,
        statsOut);

    EcologyPlaceUnplacedFamilies(
        &rng,
        outSlots,
        outLandSlotTimeMasks,
        outSlotCapacity,
        slotBases,
        bucketFill,
        familyPlacementCount,
        familyOrder,
        edgeScratch,
        ECOLOGY_GEN_MAX_FAMILY_EDGE_SCRATCH);

    EcologyRunRouteTargetPasses(
        &rng,
        outSlots,
        outLandSlotTimeMasks,
        outSlotCapacity,
        slotBases,
        bucketFill,
        familyPlacementCount,
        familyOrder,
        edgeScratch,
        ECOLOGY_GEN_MAX_FAMILY_EDGE_SCRATCH);

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
                    u16 remainSlots = (u16)(capacity - bucketFill[layoutIndex]);
                    u16 picked = EcologyPickWeightedFamily(
                        &rng,
                        groupId,
                        method,
                        TRUE,
                        remainSlots,
                        outSlots,
                        slotBases,
                        bucketFill);
                    if (++guard > (u16)(capacity + 8u)) {
                        break;
                    }
                    if (picked == 0xFFFF) {
                        break;
                    }
                    if (!EcologyTryAssignWithPairing(
                            picked,
                            groupId,
                            method,
                            outSlots,
                            outLandSlotTimeMasks,
                            outSlotCapacity,
                            slotBases,
                            bucketFill,
                            familyPlacementCount)) {
                        continue;
                    }
                }
            }
            if (statsOut != NULL && bucketFill[layoutIndex] < capacity) {
                statsOut->bucketsPartiallyFilled++;
            }
        }
    }

    for (familyId = 0; familyId < ECOLOGY_NUM_FAMILIES; familyId++) {
        if (EcologyCountDistinctGroups(
                familyId, outSlots, slotBases, bucketFill)
            == 0
            && statsOut != NULL) {
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
