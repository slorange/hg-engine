#ifndef ECOLOGY_ECOLOGY_COMPAT_VIEW_H
#define ECOLOGY_ECOLOGY_COMPAT_VIEW_H

#include "constants/generated/ecology_compat.h"
#ifdef ECOLOGY_STANDALONE
#include "ecology/ecology_standalone_types.h"
#else
#include "types.h"
#endif

#define ECOLOGY_COMPAT_BLOB_MAGIC 0x314F4345u /* 'ECO1' little-endian */

typedef struct EcologyCompatBlobHeader {
    u32 magic;
    u32 version;
    u16 numFamilies;
    u16 numGroups;
    u16 numLandEntries;
    u16 numBucketEntries;
    u16 encdataBytes;
    u16 headerSize;
    u32 offFamilyInfo;
    u32 offGroups;
    u32 offEncdataIds;
    u32 offLandEntries;
    u32 offLandOffsets;
    u32 offBucketEntries;
    u32 offBucketOffsets;
    u32 offGroupFlags;
    u32 offMethodSlots;
    u32 offLocationTypeCount;
    u16 numRequiredRoutes;
    u16 headerPadding;
    u32 offRequiredRoutes;
} EcologyCompatBlobHeader;

typedef struct EcologyCompatView {
    const EcologyFamilyInfo *familyInfo;
    const EcologyGroupInfo *groups;
    const u8 *groupEncdataIds;
    const EcologyGroupLandEntry *landEntries;
    const u16 *landOffsets;
    const EcologyGroupBucketEntry *bucketEntries;
    const u16 *bucketOffsets;
    const u8 *groupFlags;
    const u8 *methodSlots;
    const u8 *locationTypeCount;
    const EcologyRequiredRoute *requiredRoutes;
    u16 numRequiredRoutes;
} EcologyCompatView;

#ifdef ECOLOGY_STANDALONE

extern const EcologyFamilyInfo sEcologyFamilyInfo[];
extern const EcologyGroupInfo sEcologyGroups[];
extern const u8 sEcologyGroupEncdataIds[];
extern const EcologyGroupLandEntry sEcologyGroupLandEntries[];
extern const u16 sEcologyGroupLandOffsets[];
extern const EcologyGroupBucketEntry sEcologyGroupBucketEntries[];
extern const u16 sEcologyGroupBucketOffsets[];
extern const u8 sEcologyGroupFlags[];
extern const u8 sEcologyGroupMethodSlots[];
extern const u8 sEcologyGroupLocationTypeCount[];
extern const EcologyRequiredRoute sEcologyRequiredRoutes[];

#else

extern const EcologyCompatView *gEcologyCompatView;

bool8 EcologyCompatBindBlob(void *blob);
void EcologyCompatUnbind(void);
void *EcologyCompatLoadFromFilesystem(void);
bool8 EcologyCompatSessionEnsure(void);

#endif

#endif
