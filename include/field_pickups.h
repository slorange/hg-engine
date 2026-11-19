#ifndef FIELD_PICKUPS_H
#define FIELD_PICKUPS_H

#include "script.h"

enum FieldPickupAction {
    FIELD_PICKUP_CHECK_GROUND,
    FIELD_PICKUP_CHECK_HIDDEN,
    FIELD_PICKUP_GRANT,
};

void FieldPickup_Run(SCRIPTCONTEXT *ctx, u16 action);

#endif
