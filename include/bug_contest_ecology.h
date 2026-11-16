#ifndef BUG_CONTEST_ECOLOGY_H
#define BUG_CONTEST_ECOLOGY_H

#include "pokemon.h"

// Retail overlay 24 ABI. Keep its ten unused encounter entries in place:
// expanding them would move the contestants and ranking fields used by vanilla.
typedef struct BugContestEntry {
    u16 species;
    u8 lvlmin, lvlmax, rate, score, padding[2];
} BugContestEntry;

typedef struct BugContestantData {
    u8 national, day;
    u16 species, score, randmod;
} BugContestantData;

typedef struct BugContestant {
    u8 id;
    u16 score;
    BugContestantData data;
} BugContestant;

typedef struct BugContest {
    u32 heapId;
    void *saveData;
    struct Party *partyBackup;
    struct Party *partyCurrent;
    struct PartyPokemon *mon;
    u8 leadIndex, partyCount, weekday, flags;
    u16 sportBalls, prize;
    u32 elapsedTime;
    BugContestEntry encounters[10];
    BugContestant contestants[6];
    u8 ranking[6];
} BugContest;

typedef char BugContestSizeCheck[sizeof(BugContest) == 0xC0 ? 1 : -1];
typedef char BugContestantsOffsetCheck[__builtin_offsetof(BugContest, contestants) == 0x70 ? 1 : -1];

#endif
