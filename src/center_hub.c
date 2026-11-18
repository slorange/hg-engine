#include "config.h"
#include "center_hub.h"

#ifdef SHARED_POKEMON_CENTER
// Persisted IDs: append entries, never reorder this table.
// Exterior/warp pairs are the original Centers' front-door destinations.
const CenterHubDoor gCenterHubDoors[24] = {
    {69, 67, 0},     // 1 Cherrygrove
    {81, 78, 5},     // 2 Ecruteak
    {158, 73, 7},    // 3 Violet
    {166, 74, 3},    // 4 Azalea
    {169, 36, 3},    // 5 Route 32 (old-save fallback)
    {185, 76, 5},    // 6 Goldenrod
    {226, 77, 1},    // 7 Olivine
    {236, 75, 1},    // 8 Cianwood
    {246, 87, 3},    // 9 Mahogany
    {293, 89, 6},    // 10 Blackthorn
    {358, 54, 1},    // 11 Vermilion
    {393, 55, 2},    // 12 Celadon
    {407, 59, 13},   // 13 Saffron
    {428, 52, 3},    // 14 Cerulean
    {434, 53, 0},    // 15 Lavender
    {466, 18, 2},    // 16 Route 10
    {475, 51, 4},    // 17 Pewter
    {482, 56, 9},    // 18 Fuchsia
    {501, 50, 4},    // 19 Viridian
    {508, 57, 0},    // 20 Cinnabar
    {511, 11, 1},    // 21 Route 3
    {514, 90, 1},    // 22 Mt. Silver
    {528, 411, 4},   // 23 Frontier Access
    {534, 174, 2},   // 24 Safari Zone Gate
};

unsigned CenterHub_GetOrigin(const u8 record[3])
{
    if (record[0] == 'C' && record[1] == 'H'
        && record[2] > 0 && record[2] <= NELEMS(gCenterHubDoors))
        return record[2];
    return CENTER_HUB_DEFAULT_ID;
}

void CenterHub_ResolveTransition(u8 record[3], int sourceMap, Location *destination)
{
    unsigned i;
    unsigned origin = CenterHub_GetOrigin(record);
    const CenterHubDoor *door = &gCenterHubDoors[origin - 1];
    if (sourceMap == CENTER_HUB_MAP) {
        if (destination->mapId == 36 && destination->warpId == 3) {
            destination->mapId = door->exterior;
            destination->warpId = door->exteriorWarp;
            return;
        }
    }
    // Shared basement and Union Room returns must retain the saved origin.
    if (destination->mapId == CENTER_HUB_MAP
        && (sourceMap == CENTER_HUB_BASEMENT_MAP || sourceMap == 2))
        return;
    for (i = 0; i < NELEMS(gCenterHubDoors); i++) {
        if (destination->mapId != gCenterHubDoors[i].interior)
            continue;
        record[0] = 'C';
        record[1] = 'H';
        record[2] = i + 1;
        destination->mapId = CENTER_HUB_MAP;
        if (destination->warpId != -1) {
            // Ecruteak has an extra Union Room anchor before its stairs.
            destination->warpId = destination->warpId == 0 ? 0 : 1;
        }
        return;
    }
}

#ifndef CENTER_HUB_HOST_TEST
#include "local_field_data.h"
#include "map_events_internal.h"
#include "save.h"
typedef char CenterHubSaveOffsetCheck[
    __builtin_offsetof(struct SAVE_MISC_DATA, centerHubOrigin) == 0x2DD ? 1 : -1];
typedef char CenterHubSaveSizeCheck[
    sizeof(((struct SAVE_MISC_DATA *)0)->centerHubOrigin) == 3 ? 1 : -1];
extern LocalFieldData *LONG_CALL CenterHub_SaveLocalGet(void *saveData);
extern void LONG_CALL CenterHub_InitMapEvents(FieldSystem *fieldSystem, u32 map);

// Full replacement of sub_02052F94, retaining vanilla's ordering and dynamic
// warp bookkeeping. Redirect before loading the destination map's events.
void CenterHub_LoadMap(FieldSystem *fieldSystem, Location *destination)
{
    LocalFieldData *local = CenterHub_SaveLocalGet(fieldSystem->savedata);
    if (destination != NULL) {
        Location next = *destination;
        struct SAVE_MISC_DATA *misc = Sav2_Misc_get(fieldSystem->savedata);
        CenterHub_ResolveTransition(misc->centerHubOrigin,
                                    fieldSystem->location->mapId, &next);
        local->previousPosition = *fieldSystem->location;
        *fieldSystem->location = next;
    }
    CenterHub_InitMapEvents(fieldSystem, fieldSystem->location->mapId);
    if (fieldSystem->location->warpId != -1) {
        u32 warpId = fieldSystem->location->warpId;
        if (warpId < fieldSystem->map_events->num_warp_events) {
            const WARP_EVENT *warp = &fieldSystem->map_events->warp_events[warpId];
            fieldSystem->location->x = warp->x;
            fieldSystem->location->z = warp->y;
            if (warp->anchor == 0x100)
                local->dynamicWarp = local->entrancePosition;
        }
    }
}

// Keep the original spawn table; resolve only the shared interior's identity.
u16 CenterHub_GetBlackoutSpawn(u32 map)
{
    const u16 *spawn = (const u16 *)0x020F9E80;
    unsigned i;
    if (map == CENTER_HUB_MAP) {
        struct SAVE_MISC_DATA *misc = Sav2_Misc_get(SaveBlock2_get());
        map = gCenterHubDoors[CenterHub_GetOrigin(misc->centerHubOrigin) - 1].interior;
    }
    for (i = 0; i < 30; i++, spawn += 9) {
        if (spawn[1] == map && (spawn[0] & 0x100))
            return i + 1;
    }
    return 0;
}
#endif
#endif
