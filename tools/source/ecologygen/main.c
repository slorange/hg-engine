#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "constants/generated/ecology_compat.h"
#include "constants/generated/ecology_strings.h"
#include "ecology/ecology_generate.h"

static const char *sMethodLabels[ECOLOGY_METHOD_COUNT] = {
    "Land",
    "Surf",
    "Old Rod",
    "Good Rod",
    "Super Rod",
    "Rock Smash",
    "Headbutt",
};

static void PrintUsage(const char *argv0)
{
    fprintf(
        stderr,
        "Usage: %s --seed HEX [--out PATH] [--summary]\n"
        "  Generates a per-save ecology assignment using ROM compat tables.\n",
        argv0);
}

static void FormatLandTimeColumn(u8 mask, char *buf, size_t bufSize)
{
    size_t len = 0;
    buf[0] = '\0';
    if (mask == 0 || mask == ECOLOGY_TIME_ALL) {
        return;
    }
    if (mask & ECOLOGY_TIME_MORNING) {
        len += (size_t)snprintf(buf + len, bufSize - len, "%sMorning", len ? ", " : "");
    }
    if (mask & ECOLOGY_TIME_DAY) {
        len += (size_t)snprintf(buf + len, bufSize - len, "%sDay", len ? ", " : "");
    }
    if (mask & ECOLOGY_TIME_NIGHT) {
        len += (size_t)snprintf(buf + len, bufSize - len, "%sNight", len ? ", " : "");
    }
}

static u32 ParseSeed(const char *text)
{
    char *end = NULL;
    unsigned long value = strtoul(text, &end, 0);
    if (end == text || *end != '\0') {
        return 0;
    }
    return (u32)value;
}

static void WriteAssignmentTsv(
    FILE *out,
    const u16 *slots,
    const u8 *landSlotTimeMasks,
    const u16 *slotBases)
{
    u8 groupId;
    fprintf(
        out,
        "group_name\tmethod\tslot_index\tfamily_name\tbase_species\ttype_match\tland_time\n");
    for (groupId = 0; groupId < ECOLOGY_NUM_GROUPS; groupId++) {
        u8 method;
        if ((sEcologyGroupFlags[groupId] & ECOLOGY_GROUP_FLAG_SHUFFLE) == 0) {
            continue;
        }
        for (method = 0; method < ECOLOGY_METHOD_COUNT; method++) {
            u16 layoutIndex = (u16)groupId * (u16)ECOLOGY_METHOD_COUNT + (u16)method;
            u8 capacity = sEcologyGroupMethodSlots[layoutIndex];
            u16 slot;
            for (slot = 0; slot < capacity; slot++) {
                u16 familyId = slots[slotBases[layoutIndex] + slot];
                u8 typeMatch = 0;
                u16 i;
                if (familyId == 0xFFFF) {
                    continue;
                }
                if (method == ECOLOGY_METHOD_LAND) {
                    u16 count = sEcologyGroupLandOffsets[groupId + 1] - sEcologyGroupLandOffsets[groupId];
                    for (i = 0; i < count; i++) {
                        EcologyGroupLandEntry entry =
                            sEcologyGroupLandEntries[sEcologyGroupLandOffsets[groupId] + i];
                        if (entry.familyId == familyId) {
                            typeMatch = (entry.flags & ECOLOGY_EDGE_TYPE_MATCH) != 0;
                            break;
                        }
                    }
                } else {
                    u16 count = sEcologyGroupBucketOffsets[layoutIndex + 1]
                        - sEcologyGroupBucketOffsets[layoutIndex];
                    for (i = 0; i < count; i++) {
                        EcologyGroupBucketEntry entry =
                            sEcologyGroupBucketEntries[sEcologyGroupBucketOffsets[layoutIndex] + i];
                        if (entry.familyId == familyId) {
                            typeMatch = (entry.flags & ECOLOGY_EDGE_TYPE_MATCH) != 0;
                            break;
                        }
                    }
                }
                {
                    char landTime[32];
                    u16 slotIndex = (u16)(slotBases[layoutIndex] + slot);
                    FormatLandTimeColumn(
                        method == ECOLOGY_METHOD_LAND ? landSlotTimeMasks[slotIndex] : 0,
                        landTime,
                        sizeof(landTime));
                    fprintf(
                        out,
                        "%s\t%s\t%u\t%s\t%u\t%u\t%s\n",
                        sEcologyGroupNames[groupId],
                        sMethodLabels[method],
                        (unsigned)slot,
                        sEcologyFamilyNames[familyId],
                        (unsigned)sEcologyFamilyInfo[familyId].baseSpecies,
                        (unsigned)typeMatch,
                        landTime);
                }
            }
        }
    }
}

static void WriteSummary(FILE *out, const u16 *slots, const u16 *slotBases, const EcologyGenStats *stats)
{
    u16 familyId;
    u16 seen[ECOLOGY_NUM_FAMILIES];
    u8 groupId;

    for (familyId = 0; familyId < ECOLOGY_NUM_FAMILIES; familyId++) {
        seen[familyId] = 0;
    }

    for (groupId = 0; groupId < ECOLOGY_NUM_GROUPS; groupId++) {
        u8 method;
        if ((sEcologyGroupFlags[groupId] & ECOLOGY_GROUP_FLAG_SHUFFLE) == 0) {
            continue;
        }
        for (method = 0; method < ECOLOGY_METHOD_COUNT; method++) {
            u16 layoutIndex = (u16)groupId * (u16)ECOLOGY_METHOD_COUNT + (u16)method;
            u8 capacity = sEcologyGroupMethodSlots[layoutIndex];
            u16 slot;
            for (slot = 0; slot < capacity; slot++) {
                u16 familyIdSlot = slots[slotBases[layoutIndex] + slot];
                if (familyIdSlot != 0xFFFF) {
                    seen[familyIdSlot]++;
                }
            }
        }
    }

    fprintf(out, "family_name\tplacements\tdemand\n");
    for (familyId = 0; familyId < ECOLOGY_NUM_FAMILIES; familyId++) {
        fprintf(
            out,
            "%s\t%u\t%u\n",
            sEcologyFamilyNames[familyId],
            (unsigned)seen[familyId],
            (unsigned)sEcologyFamilyInfo[familyId].demand);
    }

    if (stats != NULL) {
        fprintf(
            stderr,
            "ecologygen: compat=0x%08X seed ok | unplaced=%u demand_shortfall=%u partial_buckets=%u\n",
            (unsigned)ECOLOGY_COMPAT_VERSION,
            (unsigned)stats->familiesUnplaced,
            (unsigned)stats->demandShortfall,
            (unsigned)stats->bucketsPartiallyFilled);
    }
}

int main(int argc, char **argv)
{
    u32 seed = 0;
    const char *outPath = NULL;
    int summaryOnly = 0;
    int i;
    u16 slotBases[ECOLOGY_NUM_GROUPS * ECOLOGY_METHOD_COUNT];
    u16 *slots = NULL;
    u8 *landSlotTimeMasks = NULL;
    u16 totalSlots;
    EcologyGenStats stats;
    FILE *out = stdout;

    for (i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--seed") == 0 && i + 1 < argc) {
            seed = ParseSeed(argv[++i]);
        } else if (strcmp(argv[i], "--out") == 0 && i + 1 < argc) {
            outPath = argv[++i];
        } else if (strcmp(argv[i], "--summary") == 0) {
            summaryOnly = 1;
        } else if (strcmp(argv[i], "--help") == 0) {
            PrintUsage(argv[0]);
            return 0;
        } else {
            fprintf(stderr, "Unknown argument: %s\n", argv[i]);
            PrintUsage(argv[0]);
            return 1;
        }
    }

    if (seed == 0) {
        fprintf(stderr, "Missing or invalid --seed (use non-zero hex/dec).\n");
        return 1;
    }

    totalSlots = EcologyGenBuildSlotLayout(slotBases);
    slots = (u16 *)malloc(sizeof(u16) * totalSlots);
    landSlotTimeMasks = (u8 *)malloc(totalSlots);
    if (slots == NULL || landSlotTimeMasks == NULL) {
        fprintf(stderr, "Out of memory (%u slots).\n", (unsigned)totalSlots);
        free(slots);
        free(landSlotTimeMasks);
        return 1;
    }

    if (!EcologyGenerateWorld(NULL, seed, slots, landSlotTimeMasks, totalSlots, &stats)) {
        fprintf(stderr, "EcologyGenerateWorld failed.\n");
        free(slots);
        free(landSlotTimeMasks);
        return 1;
    }

    if (outPath != NULL) {
        out = fopen(outPath, "wb");
        if (out == NULL) {
            perror(outPath);
            free(slots);
            return 1;
        }
    }

    if (summaryOnly) {
        WriteSummary(out, slots, slotBases, &stats);
    } else {
        WriteAssignmentTsv(out, slots, landSlotTimeMasks, slotBases);
        fprintf(stderr, "ecologygen: wrote %u slot assignments\n", (unsigned)totalSlots);
    }

    if (outPath != NULL) {
        fclose(out);
    }
    free(slots);
    free(landSlotTimeMasks);
    return 0;
}
