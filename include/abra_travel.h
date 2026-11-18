#ifndef ABRA_TRAVEL_H
#define ABRA_TRAVEL_H
#include "script.h"
#define ABRA_TRAVEL_FARE 400
BOOL AbraTravel_Command(SCRIPTCONTEXT *ctx, unsigned mode);
BOOL AbraTravel_Resolve(const u16 *spawns, SCRIPT_STATE *flags, unsigned map,
                        Location *destination, Location *special);
#endif
