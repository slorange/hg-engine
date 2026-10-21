#ifndef HEAL_AFTER_BATTLE_H
#define HEAL_AFTER_BATTLE_H

#include "config.h"
#include "types.h"

#ifdef HEAL_AFTER_BATTLE
void LONG_CALL HealAfterBattle_HealPartyOnFieldStep(void *saveData);
#endif // HEAL_AFTER_BATTLE

#endif // HEAL_AFTER_BATTLE_H
