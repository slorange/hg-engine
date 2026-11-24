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

#endif

#ifdef OPENWORLD_STORY_SKIP_AND_STARTING_ITEMS
#define VAR_PLAYER_START_CITY 0x4031
#define NEW_BARK_MAP 60
#define NEW_BARK_HOME_WARP 1
#define MOM_HOUSE_MAP 63
#define HOUSE_ENTRY_WARP 0

// Indexed by START_CITY_* in the Mom script. Each outdoor door enters at warp 0.
static const struct {
    u16 exterior;
    u16 exteriorWarp;
    u16 interior;
} sHomeDoors[] = {
    {NEW_BARK_MAP, NEW_BARK_HOME_WARP, MOM_HOUSE_MAP},
    {73, 8, 160},   // Violet
    {74, 4, 163},   // Azalea
    {76, 14, 205},  // Goldenrod
    {78, 1, 85},    // Ecruteak
    {77, 6, 228},   // Olivine
    {75, 7, 385},   // Cianwood
    {87, 4, 133},   // Mahogany
    {89, 4, 290},   // Blackthorn
    {49, 0, 503},   // Pallet
    {50, 1, 497},   // Viridian
    {51, 5, 477},   // Pewter
    {52, 2, 431},   // Cerulean
    {59, 14, 399},  // Saffron
    {53, 2, 436},   // Lavender
    {55, 6, 383},   // Celadon
    {54, 3, 363},   // Vermilion
    {56, 8, 481},   // Fuchsia
};

void Home_ResolveTransition(unsigned startCity, int sourceMap, Location *destination)
{
    if (startCity == 0 || startCity >= NELEMS(sHomeDoors))
        return;

    if (sourceMap == sHomeDoors[startCity].exterior
        && destination->mapId == sHomeDoors[startCity].interior
        && destination->warpId == HOUSE_ENTRY_WARP) {
        destination->mapId = MOM_HOUSE_MAP;
    } else if (sourceMap == NEW_BARK_MAP && destination->mapId == MOM_HOUSE_MAP
               && destination->warpId == HOUSE_ENTRY_WARP) {
        destination->mapId = sHomeDoors[startCity].interior;
    } else if (sourceMap == sHomeDoors[startCity].interior
               && destination->mapId == sHomeDoors[startCity].exterior
               && destination->warpId == sHomeDoors[startCity].exteriorWarp) {
        destination->mapId = NEW_BARK_MAP;
        destination->warpId = NEW_BARK_HOME_WARP;
    }
}
#endif

#if !defined(CENTER_HUB_HOST_TEST) && (defined(SHARED_POKEMON_CENTER) || defined(OPENWORLD_STORY_SKIP_AND_STARTING_ITEMS))
#include "local_field_data.h"
#include "map_events_internal.h"
#include "save.h"
extern LocalFieldData *LONG_CALL CenterHub_SaveLocalGet(void *saveData);
extern void LONG_CALL CenterHub_InitMapEvents(FieldSystem *fieldSystem, u32 map);

// Full replacement of sub_02052F94, retaining vanilla's ordering and dynamic
// warp bookkeeping. Redirect before loading the destination map's events.
void CenterHub_LoadMap(FieldSystem *fieldSystem, Location *destination)
{
    LocalFieldData *local = CenterHub_SaveLocalGet(fieldSystem->savedata);
    if (destination != NULL) {
        Location next = *destination;
#ifdef OPENWORLD_STORY_SKIP_AND_STARTING_ITEMS
        u16 startCity = GetScriptVarPassSave(SavArray_Flags_get(fieldSystem->savedata),
                                            VAR_PLAYER_START_CITY);
        Home_ResolveTransition(startCity, fieldSystem->location->mapId, &next);
#endif
#ifdef SHARED_POKEMON_CENTER
        struct SAVE_MISC_DATA *misc = Sav2_Misc_get(fieldSystem->savedata);
        CenterHub_ResolveTransition(misc->centerHubOrigin,
                                    fieldSystem->location->mapId, &next);
#endif
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

#ifdef SHARED_POKEMON_CENTER
typedef char CenterHubSaveOffsetCheck[
    __builtin_offsetof(struct SAVE_MISC_DATA, centerHubOrigin) == 0x2DD ? 1 : -1];
typedef char CenterHubSaveSizeCheck[
    sizeof(((struct SAVE_MISC_DATA *)0)->centerHubOrigin) == 3 ? 1 : -1];

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
