#ifndef ECOLOGY_ECOLOGY_COMPAT_ACCESS_H
#define ECOLOGY_ECOLOGY_COMPAT_ACCESS_H

#include "ecology/ecology_compat_view.h"

#ifdef ECOLOGY_STANDALONE

#define ECO_FAMILY_INFO(id) (sEcologyFamilyInfo[(id)])
#define ECO_GROUPS(gid) (sEcologyGroups[(gid)])
#define ECO_GROUP_FLAGS(gid) (sEcologyGroupFlags[(gid)])
#define ECO_METHOD_SLOTS(idx) (sEcologyGroupMethodSlots[(idx)])
#define ECO_LAND_OFFSETS(gid) (sEcologyGroupLandOffsets[(gid)])
#define ECO_LAND_ENTRIES(idx) (sEcologyGroupLandEntries[(idx)])
#define ECO_BUCKET_OFFSETS(idx) (sEcologyGroupBucketOffsets[(idx)])
#define ECO_BUCKET_ENTRIES(idx) (sEcologyGroupBucketEntries[(idx)])
#define ECO_LOCATION_TYPE_COUNT(gid) (sEcologyGroupLocationTypeCount[(gid)])
#define ECO_REQUIRED_ROUTE_COUNT (ECOLOGY_NUM_REQUIRED_ROUTES)
#define ECO_REQUIRED_ROUTE(i) (sEcologyRequiredRoutes[(i)])

#else

#define ECO_FAMILY_INFO(id) (gEcologyCompatView->familyInfo[(id)])
#define ECO_GROUPS(gid) (gEcologyCompatView->groups[(gid)])
#define ECO_GROUP_FLAGS(gid) (gEcologyCompatView->groupFlags[(gid)])
#define ECO_METHOD_SLOTS(idx) (gEcologyCompatView->methodSlots[(idx)])
#define ECO_LAND_OFFSETS(gid) (gEcologyCompatView->landOffsets[(gid)])
#define ECO_LAND_ENTRIES(idx) (gEcologyCompatView->landEntries[(idx)])
#define ECO_BUCKET_OFFSETS(idx) (gEcologyCompatView->bucketOffsets[(idx)])
#define ECO_BUCKET_ENTRIES(idx) (gEcologyCompatView->bucketEntries[(idx)])
#define ECO_LOCATION_TYPE_COUNT(gid) (gEcologyCompatView->locationTypeCount[(gid)])
#define ECO_REQUIRED_ROUTE_COUNT (gEcologyCompatView->numRequiredRoutes)
#define ECO_REQUIRED_ROUTE(i) (gEcologyCompatView->requiredRoutes[(i)])

#endif

#endif
