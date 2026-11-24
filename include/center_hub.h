#ifndef CENTER_HUB_H
#define CENTER_HUB_H
#include "pokemon.h"
#define CENTER_HUB_MAP 169
#define CENTER_HUB_BASEMENT_MAP 170
#define CENTER_HUB_DEFAULT_ID 5
typedef struct CenterHubDoor {
    u16 interior;
    u16 exterior;
    u16 exteriorWarp;
} CenterHubDoor;
extern const CenterHubDoor gCenterHubDoors[24];
unsigned CenterHub_GetOrigin(const u8 record[3]);
void CenterHub_ResolveTransition(u8 record[3], int sourceMap, Location *destination);
void Home_ResolveTransition(unsigned startCity, int sourceMap, Location *destination);
#endif
