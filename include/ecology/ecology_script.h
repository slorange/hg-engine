#ifndef ECOLOGY_ECOLOGY_SCRIPT_H
#define ECOLOGY_ECOLOGY_SCRIPT_H

#include "../config.h"
#include "../types.h"

#if defined(IMPLEMENT_ECOLOGY_GENERATION)
void EcologyRunNewGameGeneration(void *saveData);
void EcologySetGenDebugStage(u8 stage);
u8 EcologyGetGenDebugStage(void);
#endif

#endif
