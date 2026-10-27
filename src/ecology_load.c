#include "../include/config.h"

#ifdef IMPLEMENT_ECOLOGY_GENERATION

#include "../include/constants/file.h"
#include "../include/constants/generated/ecology_compat.h"
#include "../include/ecology/ecology_compat_view.h"
#include "../include/types.h"

const EcologyCompatView *gEcologyCompatView = NULL;

static EcologyCompatView sEcologyCompatViewStorage;
static void *sEcologyCompatBlob;

static bool8 EcologyCompatHeaderValid(const EcologyCompatBlobHeader *hdr)
{
    if (hdr == NULL) {
        return FALSE;
    }
    if (hdr->magic != ECOLOGY_COMPAT_BLOB_MAGIC) {
        return FALSE;
    }
    if (hdr->version != ECOLOGY_COMPAT_VERSION) {
        return FALSE;
    }
    if (hdr->numFamilies != ECOLOGY_NUM_FAMILIES || hdr->numGroups != ECOLOGY_NUM_GROUPS) {
        return FALSE;
    }
    if (hdr->headerSize < sizeof(EcologyCompatBlobHeader)) {
        return FALSE;
    }
    return TRUE;
}

static bool8 EcologyCompatMethodSlotsValid(const EcologyCompatBlobHeader *hdr, u8 *base)
{
    u32 slotCount = (u32)hdr->numGroups * (u32)ECOLOGY_METHOD_COUNT;
    u32 i;

    for (i = 0; i < slotCount; i++) {
        if (base[hdr->offMethodSlots + i] > ECOLOGY_GEN_MAX_SLOTS_PER_BUCKET) {
            return FALSE;
        }
    }
    return TRUE;
}

bool8 EcologyCompatBindBlob(void *blob)
{
    const EcologyCompatBlobHeader *hdr;
    u8 *base;

    if (blob == NULL) {
        return FALSE;
    }

    hdr = (const EcologyCompatBlobHeader *)blob;
    if (!EcologyCompatHeaderValid(hdr)) {
        return FALSE;
    }

    base = (u8 *)blob;
    if (!EcologyCompatMethodSlotsValid(hdr, base)) {
        return FALSE;
    }
    sEcologyCompatViewStorage.familyInfo =
        (const EcologyFamilyInfo *)(base + hdr->offFamilyInfo);
    sEcologyCompatViewStorage.groups = (const EcologyGroupInfo *)(base + hdr->offGroups);
    sEcologyCompatViewStorage.groupEncdataIds = base + hdr->offEncdataIds;
    sEcologyCompatViewStorage.landEntries =
        (const EcologyGroupLandEntry *)(base + hdr->offLandEntries);
    sEcologyCompatViewStorage.landOffsets = (const u16 *)(base + hdr->offLandOffsets);
    sEcologyCompatViewStorage.bucketEntries =
        (const EcologyGroupBucketEntry *)(base + hdr->offBucketEntries);
    sEcologyCompatViewStorage.bucketOffsets = (const u16 *)(base + hdr->offBucketOffsets);
    sEcologyCompatViewStorage.groupFlags = base + hdr->offGroupFlags;
    sEcologyCompatViewStorage.methodSlots = base + hdr->offMethodSlots;
    sEcologyCompatViewStorage.locationTypeCount = base + hdr->offLocationTypeCount;

    gEcologyCompatView = &sEcologyCompatViewStorage;
    sEcologyCompatBlob = blob;
    return TRUE;
}

void EcologyCompatUnbind(void)
{
    gEcologyCompatView = NULL;
    sEcologyCompatBlob = NULL;
}

void *EcologyCompatLoadFromFilesystem(void)
{
    return AllocAndReadWholeNarcMemberByIdPair(
        ARC_CODE_ADDONS, CODE_ADDON_ECOLOGY_COMPAT, HEAPID_DEFAULT);
}

#endif
