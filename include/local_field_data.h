#ifndef LOCAL_FIELD_DATA_H
#define LOCAL_FIELD_DATA_H

#include "types.h"

#include "pokemon.h"

typedef struct PlayerSaveData {
    u16 hasRunningShoes;
    u16 runningShoesLock;
    s32 state;
} PlayerSaveData;

typedef struct LocalFieldData {
    Location currentPosition;
    Location entrancePosition;
    Location previousPosition;
    Location dynamicWarp;
    Location specialSpawn;
    u16 musicId;
    u16 weather;
    u16 lastSpawn;
    u8 cameraType;
    PlayerSaveData player;
} LocalFieldData;

#endif // LOCAL_FIELD_DATA_H
