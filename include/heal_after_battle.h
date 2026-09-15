#ifndef HEAL_AFTER_BATTLE_H
#define HEAL_AFTER_BATTLE_H

#include "config.h"

struct BattleSystem;

#ifdef HEAL_AFTER_BATTLE
void HealAfterBattle_HealParty(struct BattleSystem *bw);
#endif // HEAL_AFTER_BATTLE

#endif // HEAL_AFTER_BATTLE_H
