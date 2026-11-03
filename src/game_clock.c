#include "config.h"

#ifdef IMPLEMENT_ACCELERATED_GAME_CLOCK

#include "rtc.h"
#include "types.h"

struct GFRtcWork {
    u32 getDateTimeSuccess;
    u32 getDateTimeLock;
    s32 getDateTimeSleep;
    u32 getDateTimeErrorCode;
    struct RTCDate date;
    struct RTCTime time;
    struct RTCDate date_async;
    struct RTCTime time_async;
    s32 frozenTimeState;
    struct RTCTime frozenTime;
};

extern struct GFRtcWork sRTCWork;

#define GAME_CLOCK_RTC_WORK (&sRTCWork)

static const struct RTCTime *GameClock_GetTimeView(const struct GFRtcWork *work)
{
    if (work->frozenTimeState == 3) {
        return &work->frozenTime;
    }
    return &work->time;
}

static void GameClock_VanillaCopyTime(struct RTCTime *time, struct GFRtcWork *work)
{
    if (time == NULL) {
        return;
    }
    *time = *GameClock_GetTimeView(work);
}

static void GameClock_VanillaCopyDateTime(struct RTCDate *date, struct RTCTime *time,
    struct GFRtcWork *work)
{
    if (date == NULL || time == NULL) {
        return;
    }
    *date = work->date;
    GameClock_VanillaCopyTime(time, work);
}

static s32 GameClock_SecFromTime(const struct RTCTime *time)
{
    return (s32)(time->hour * 3600u + time->minute * 60u + time->second);
}

static u32 GameClock_PhaseSecFromRealTime(const struct RTCTime *real)
{
    u32 tod;

    tod = real->hour * 3600u + real->minute * 60u + real->second;
    return tod % (u32)GAME_CLOCK_REAL_SECONDS_PER_GAME_DAY;
}

static void GameClock_PhaseToTimeOfDay(u32 phaseSec, struct RTCTime *time)
{
    u32 gameSecInDay;

    gameSecInDay = phaseSec * (u32)GAME_CLOCK_GAME_SECONDS_PER_REAL_SECOND;
    if (gameSecInDay >= 86400u) {
        gameSecInDay = 86399u;
    }
    time->hour = gameSecInDay / 3600u;
    time->minute = (gameSecInDay % 3600u) / 60u;
    time->second = gameSecInDay % 60u;
}

static void GameClock_FillScaledDateTime(struct RTCDate *date, struct RTCTime *time,
    struct GFRtcWork *work)
{
    const struct RTCTime *realTime;

    if (work->frozenTimeState == 3) {
        *date = work->date;
        *time = work->frozenTime;
        return;
    }

    if (work->getDateTimeSuccess == 0 || work->getDateTimeLock != 0) {
        GameClock_VanillaCopyDateTime(date, time, work);
        return;
    }

    realTime = &work->time_async;
    *date = work->date_async;
    GameClock_PhaseToTimeOfDay(GameClock_PhaseSecFromRealTime(realTime), time);
}

static s32 GameClock_GetTimeOfDaySecView(struct GFRtcWork *work)
{
    struct RTCTime time;
    struct RTCDate scratch;

    GameClock_FillScaledDateTime(&scratch, &time, work);
    return GameClock_SecFromTime(&time);
}

void LONG_CALL GF_RTC_CopyTime_hook(struct RTCTime *time)
{
    struct RTCDate scratch;

    GameClock_FillScaledDateTime(&scratch, time, GAME_CLOCK_RTC_WORK);
}

void LONG_CALL GF_RTC_CopyDateTime_hook(struct RTCDate *date, struct RTCTime *time)
{
    GameClock_FillScaledDateTime(date, time, GAME_CLOCK_RTC_WORK);
}

s32 LONG_CALL GF_RTC_TimeToSec_hook(void)
{
    return GameClock_GetTimeOfDaySecView(GAME_CLOCK_RTC_WORK);
}

#endif /* IMPLEMENT_ACCELERATED_GAME_CLOCK */
