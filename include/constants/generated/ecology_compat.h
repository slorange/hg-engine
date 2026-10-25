#ifndef CONSTANTS_GENERATED_ECOLOGY_COMPAT_H
#define CONSTANTS_GENERATED_ECOLOGY_COMPAT_H

#ifdef ECOLOGY_STANDALONE
#include "ecology/ecology_standalone_types.h"
#else
#include "types.h"
#endif

#define ECOLOGY_COMPAT_VERSION 0x385B5715u

#define ECOLOGY_TIME_MORNING  (1u << 0)
#define ECOLOGY_TIME_DAY      (1u << 1)
#define ECOLOGY_TIME_NIGHT    (1u << 2)
#define ECOLOGY_TIME_ALL      (ECOLOGY_TIME_MORNING | ECOLOGY_TIME_DAY | ECOLOGY_TIME_NIGHT)

#define ECOLOGY_LAND_TIME_ALL 0u

enum EcologyMethod {
    ECOLOGY_METHOD_LAND = 0,
    ECOLOGY_METHOD_SURF,
    ECOLOGY_METHOD_OLD_ROD,
    ECOLOGY_METHOD_GOOD_ROD,
    ECOLOGY_METHOD_SUPER_ROD,
    ECOLOGY_METHOD_ROCK_SMASH,
    ECOLOGY_METHOD_HEADBUTT,
    ECOLOGY_METHOD_COUNT,
};

enum EcologyRarity {
    ECOLOGY_RARITY_NORMAL = 0,
    ECOLOGY_RARITY_COMMON,
    ECOLOGY_RARITY_RARE,
    ECOLOGY_RARITY_VERY_RARE,
};

#define ECOLOGY_EDGE_TYPE_MATCH (1u << 0)

#define ECOLOGY_WATER_DRY   (1u << 0)
#define ECOLOGY_WATER_FRESH (1u << 1)
#define ECOLOGY_WATER_SALT  (1u << 2)
#define ECOLOGY_WATER_CAVE  (1u << 3)

#define ECOLOGY_GROUP_FLAG_SHUFFLE (1u << 0)

#define ECOLOGY_TYPED_LAND_SLOTS_PER_TYPE 2u

#define ECOLOGY_GEN_MAX_SLOTS_PER_BUCKET 6u
#define ECOLOGY_GEN_TOTAL_SLOTS 1012u

typedef struct EcologyFamilyInfo {
    u16 baseSpecies;
    u16 dexIndex;
    u8 rarity;
    u8 demand;
    u8 landTimeMask;
    u8 padding;
} EcologyFamilyInfo;

typedef struct EcologyGroupInfo {
    u16 encdataOffset;
    u8 encdataCount;
    u8 landPeriodMask;
    u8 methodMask;
    u8 waterMask;
} EcologyGroupInfo;

typedef struct EcologyCompatEdge {
    u8 groupId;
    u8 method;
    u8 flags;
    u8 padding;
} EcologyCompatEdge;

typedef struct EcologyGroupLandEntry {
    u16 familyId;
    u8 flags;
    u8 padding;
} EcologyGroupLandEntry;

typedef struct EcologyGroupBucketEntry {
    u16 familyId;
    u8 flags;
    u8 padding;
} EcologyGroupBucketEntry;

#define ECOLOGY_NUM_FAMILIES 176
#define ECOLOGY_NUM_GROUPS 94
#define ECOLOGY_NUM_EDGES 8428

extern const EcologyFamilyInfo sEcologyFamilyInfo[ECOLOGY_NUM_FAMILIES];
extern const EcologyGroupInfo sEcologyGroups[ECOLOGY_NUM_GROUPS];
extern const u8 sEcologyGroupEncdataIds[];
extern const EcologyGroupLandEntry sEcologyGroupLandEntries[];
extern const u16 sEcologyGroupLandOffsets[ECOLOGY_NUM_GROUPS + 1];
extern const EcologyGroupBucketEntry sEcologyGroupBucketEntries[];
extern const u16 sEcologyGroupBucketOffsets[ECOLOGY_NUM_GROUPS * ECOLOGY_METHOD_COUNT + 1];
extern const u8 sEcologyGroupFlags[ECOLOGY_NUM_GROUPS];
extern const u8 sEcologyGroupMethodSlots[ECOLOGY_NUM_GROUPS * ECOLOGY_METHOD_COUNT];
extern const u8 sEcologyGroupLocationTypeCount[ECOLOGY_NUM_GROUPS];

#endif
