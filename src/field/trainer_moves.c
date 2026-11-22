#include "battle.h"
#include "constants/file.h"
#include "constants/item.h"
#include "constants/move_effects.h"
#include "constants/generated/learnsets.h"
#include "pokemon.h"

#define TRAINER_TM_COUNT 92
#define TRAINER_HM_COUNT 8
#define TRAINER_MOVE_SLOTS 4
#define FREE_TRAINER_MOVE 0xFF
#define TRAINER_STATUS_TYPE 0xFF

struct TrainerMoveCandidate {
    u32 groupMask;
    u16 move;
    u16 score;
    u8 type;
    u8 tm;
    u16 utilityAttackScore;
};

// Earliest badge gate across Gym rewards, shops, and Game Corner prizes.
// Omitted entries have no qualifying source.
static const u8 sTrainerTmUnlocks[TRAINER_TM_COUNT] = {
    [1 - 1] = 6 + 1,
    [2 - 1] = 0 + 1,
    [3 - 1] = 0 + 1,
    [4 - 1] = 4 + 1,
    [5 - 1] = 4 + 1,
    [6 - 1] = 0 + 1,
    [7 - 1] = 0 + 1,
    [8 - 1] = 4 + 1,
    [9 - 1] = 0 + 1,
    [11 - 1] = 0 + 1,
    [12 - 1] = 0 + 1,
    [13 - 1] = 10 + 1,
    [14 - 1] = 8 + 1,
    [15 - 1] = 8 + 1,
    [16 - 1] = 0 + 1,
    [17 - 1] = 0 + 1,
    [18 - 1] = 0 + 1,
    [19 - 1] = 4 + 1,
    [20 - 1] = 2 + 1,
    [21 - 1] = 0 + 1,
    [22 - 1] = 8 + 1,
    [23 - 1] = 6 + 1,
    [24 - 1] = 10 + 1,
    [25 - 1] = 8 + 1,
    [26 - 1] = 12 + 1,
    [27 - 1] = 4 + 1,
    [28 - 1] = 0 + 1,
    [29 - 1] = 10 + 1,
    [30 - 1] = 6 + 1,
    [31 - 1] = 0 + 1,
    [32 - 1] = 4 + 1,
    [33 - 1] = 0 + 1,
    [34 - 1] = 0 + 1,
    [35 - 1] = 10 + 1,
    [36 - 1] = 8 + 1,
    [37 - 1] = 0 + 1,
    [38 - 1] = 8 + 1,
    [39 - 1] = 0 + 1,
    [40 - 1] = 0 + 1,
    [41 - 1] = 0 + 1,
    [42 - 1] = 2 + 1,
    [43 - 1] = 0 + 1,
    [44 - 1] = 0 + 1,
    [45 - 1] = 0 + 1,
    [46 - 1] = 0 + 1,
    [47 - 1] = 0 + 1,
    [48 - 1] = 0 + 1,
    [49 - 1] = 0 + 1,
    [50 - 1] = 8 + 1,
    [51 - 1] = 4 + 1,
    [52 - 1] = 8 + 1,
    [53 - 1] = 8 + 1,
    [54 - 1] = 0 + 1,
    [55 - 1] = 4 + 1,
    [56 - 1] = 0 + 1,
    [57 - 1] = 0 + 1,
    [58 - 1] = 0 + 1,
    [59 - 1] = 8 + 1,
    [60 - 1] = 4 + 1,
    [61 - 1] = 2 + 1,
    [62 - 1] = 0 + 1,
    [63 - 1] = 0 + 1,
    [64 - 1] = 0 + 1,
    [65 - 1] = 2 + 1,
    [66 - 1] = 0 + 1,
    [67 - 1] = 0 + 1,
    [68 - 1] = 8 + 1,
    [69 - 1] = 0 + 1,
    [70 - 1] = 1 + 1,
    [71 - 1] = 8 + 1,
    [72 - 1] = 2 + 1,
    [73 - 1] = 2 + 1,
    [74 - 1] = 2 + 1,
    [75 - 1] = 6 + 1,
    [76 - 1] = 0 + 1,
    [77 - 1] = 0 + 1,
    [78 - 1] = 0 + 1,
    [79 - 1] = 6 + 1,
    [80 - 1] = 4 + 1,
    [81 - 1] = 6 + 1,
    [82 - 1] = 0 + 1,
    [83 - 1] = 0 + 1,
    [84 - 1] = 6 + 1,
    [85 - 1] = 6 + 1,
    [86 - 1] = 2 + 1,
    [87 - 1] = 0 + 1,
    [88 - 1] = 0 + 1,
    [89 - 1] = 4 + 1,
    [90 - 1] = 0 + 1,
    [91 - 1] = 6 + 1,
    [92 - 1] = 8 + 1,
};

enum TrainerStatusGroup {
    TRAINER_STATUS_SETUP,
    TRAINER_STATUS_SLEEP,
    TRAINER_STATUS_RECOVERY,
    TRAINER_STATUS_PARALYSIS,
    TRAINER_STATUS_POISON,
    TRAINER_STATUS_PROTECT,
    TRAINER_STATUS_CONFUSION,
    TRAINER_STATUS_LOWER_ATTACK,
    TRAINER_STATUS_LOWER_SP_ATTACK,
    TRAINER_STATUS_LOWER_DEFENSE,
    TRAINER_STATUS_LOWER_SP_DEFENSE,
    TRAINER_STATUS_LOWER_SPEED,
    TRAINER_STATUS_LOWER_ACCURACY,
    TRAINER_STATUS_WEATHER,
    TRAINER_STATUS_TERRAIN,
    TRAINER_STATUS_HAZARD,
    TRAINER_STATUS_CURE,
    TRAINER_STATUS_AIM,
    TRAINER_STATUS_ABILITY,
    TRAINER_STATUS_SCREEN_PHYSICAL,
    TRAINER_STATUS_SCREEN_SPECIAL,
    TRAINER_STATUS_SELF_KO,
};

struct TrainerStatusMove {
    u32 groups;
    u16 move;
    u8 tier;
};

static const struct TrainerStatusMove sTrainerStatusMoves[] = {
    // C tier
    { (1u << TRAINER_STATUS_SETUP), MOVE_ACUPRESSURE, 1 },
    { 0, MOVE_ATTRACT, 1 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_CHARGE, 1 },
    { 0, MOVE_CONVERSION, 1 },
    { 0, MOVE_CONVERSION_2, 1 },
    { 0, MOVE_COPYCAT, 1 },
    { (1u << TRAINER_STATUS_SLEEP), MOVE_DARK_VOID, 1 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_DEFENSE_CURL, 1 },
    { (1u << TRAINER_STATUS_ABILITY), MOVE_ENTRAINMENT, 1 },
    { (1u << TRAINER_STATUS_LOWER_ACCURACY), MOVE_FLASH, 1 },
    { (1u << TRAINER_STATUS_CONFUSION), MOVE_FLATTER, 1 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_GROWTH, 1 },
    { (1u << TRAINER_STATUS_LOWER_ATTACK), MOVE_GROWL, 1 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_HARDEN, 1 },
    { 0, MOVE_HEART_SWAP, 1 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_HOWL, 1 },
    { (1u << TRAINER_STATUS_LOWER_DEFENSE), MOVE_LEER, 1 },
    { (1u << TRAINER_STATUS_AIM), MOVE_LOCK_ON, 1 },
    { 0, MOVE_METRONOME, 1 },
    { (1u << TRAINER_STATUS_AIM), MOVE_MIND_READER, 1 },
    { (1u << TRAINER_STATUS_RECOVERY), MOVE_PAIN_SPLIT, 1 },
    { (1u << TRAINER_STATUS_LOWER_ATTACK), MOVE_PLAY_NICE, 1 },
    { 0, MOVE_POWER_TRICK, 1 },
    { 0, MOVE_PSYCHO_SHIFT, 1 },
    { (1u << TRAINER_STATUS_ABILITY), MOVE_ROLE_PLAY, 1 },
    { (1u << TRAINER_STATUS_LOWER_ACCURACY), MOVE_SAND_ATTACK, 1 },
    { (1u << TRAINER_STATUS_ABILITY), MOVE_SIMPLE_BEAM, 1 },
    { (1u << TRAINER_STATUS_SLEEP), MOVE_SING, 1 },
    { (1u << TRAINER_STATUS_ABILITY), MOVE_SKILL_SWAP, 1 },
    { (1u << TRAINER_STATUS_LOWER_ACCURACY), MOVE_SMOKESCREEN, 1 },
    { 0, MOVE_SOAK, 1 },
    { (1u << TRAINER_STATUS_CONFUSION), MOVE_SUPERSONIC, 1 },
    { (1u << TRAINER_STATUS_CONFUSION), MOVE_SWAGGER, 1 },
    { (1u << TRAINER_STATUS_RECOVERY), MOVE_SWALLOW, 1 },
    { (1u << TRAINER_STATUS_LOWER_DEFENSE), MOVE_TAIL_WHIP, 1 },
    { (1u << TRAINER_STATUS_LOWER_ATTACK) | (1u << TRAINER_STATUS_LOWER_SP_ATTACK), MOVE_TEARFUL_LOOK, 1 },
    { 0, MOVE_TRANSFORM, 1 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_WITHDRAW, 1 },
    { (1u << TRAINER_STATUS_ABILITY), MOVE_WORRY_SEED, 1 },
    // B tier
    { (1u << TRAINER_STATUS_RECOVERY), MOVE_AQUA_RING, 2 },
    { (1u << TRAINER_STATUS_CURE), MOVE_AROMATHERAPY, 2 },
    { (1u << TRAINER_STATUS_SCREEN_PHYSICAL) | (1u << TRAINER_STATUS_SCREEN_SPECIAL), MOVE_AURORA_VEIL, 2 },
    { (1u << TRAINER_STATUS_LOWER_ATTACK), MOVE_BABY_DOLL_EYES, 2 },
    { 0, MOVE_BATON_PASS, 2 },
    { (1u << TRAINER_STATUS_LOWER_SP_ATTACK), MOVE_CAPTIVATE, 2 },
    { (1u << TRAINER_STATUS_LOWER_SPEED), MOVE_COTTON_SPORE, 2 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_DEFEND_ORDER, 2 },
    { 0, MOVE_DEFOG, 2 },
    { 0, MOVE_DESTINY_BOND, 2 },
    { (1u << TRAINER_STATUS_TERRAIN), MOVE_ELECTRIC_TERRAIN, 2 },
    { (1u << TRAINER_STATUS_PROTECT), MOVE_ENDURE, 2 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_FOCUS_ENERGY, 2 },
    { (1u << TRAINER_STATUS_ABILITY), MOVE_GASTRO_ACID, 2 },
    { (1u << TRAINER_STATUS_TERRAIN), MOVE_GRASSY_TERRAIN, 2 },
    { 0, MOVE_GRAVITY, 2 },
    { (1u << TRAINER_STATUS_WEATHER), MOVE_HAIL, 2 },
    { 0, MOVE_HAZE, 2 },
    { (1u << TRAINER_STATUS_CURE), MOVE_HEAL_BELL, 2 },
    { (1u << TRAINER_STATUS_SLEEP), MOVE_HYPNOSIS, 2 },
    { (1u << TRAINER_STATUS_RECOVERY), MOVE_INGRAIN, 2 },
    { (1u << TRAINER_STATUS_RECOVERY), MOVE_LIFE_DEW, 2 },
    { 0, MOVE_MAGNET_RISE, 2 },
    { (1u << TRAINER_STATUS_LOWER_SP_DEFENSE), MOVE_METAL_SOUND, 2 },
    { (1u << TRAINER_STATUS_LOWER_ATTACK) | (1u << TRAINER_STATUS_LOWER_SP_ATTACK), MOVE_NOBLE_ROAR, 2 },
    { (1u << TRAINER_STATUS_POISON), MOVE_POISON_GAS, 2 },
    { (1u << TRAINER_STATUS_POISON), MOVE_POISON_POWDER, 2 },
    { (1u << TRAINER_STATUS_WEATHER), MOVE_RAIN_DANCE, 2 },
    { (1u << TRAINER_STATUS_RECOVERY), MOVE_REST, 2 },
    { 0, MOVE_SAFEGUARD, 2 },
    { (1u << TRAINER_STATUS_WEATHER), MOVE_SANDSTORM, 2 },
    { (1u << TRAINER_STATUS_LOWER_SPEED), MOVE_SCARY_FACE, 2 },
    { (1u << TRAINER_STATUS_LOWER_DEFENSE), MOVE_SCREECH, 2 },
    { (1u << TRAINER_STATUS_WEATHER), MOVE_SNOWSCAPE, 2 },
    { (1u << TRAINER_STATUS_HAZARD), MOVE_SPIKES, 2 },
    { (1u << TRAINER_STATUS_HAZARD), MOVE_STEALTH_ROCK, 2 },
    { (1u << TRAINER_STATUS_HAZARD), MOVE_STICKY_WEB, 2 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_STOCKPILE, 2 },
    { (1u << TRAINER_STATUS_LOWER_SPEED), MOVE_STRING_SHOT, 2 },
    { (1u << TRAINER_STATUS_WEATHER), MOVE_SUNNY_DAY, 2 },
    { (1u << TRAINER_STATUS_CONFUSION), MOVE_SWEET_KISS, 2 },
    { 0, MOVE_TAILWIND, 2 },
    { (1u << TRAINER_STATUS_CONFUSION), MOVE_TEETER_DANCE, 2 },
    { (1u << TRAINER_STATUS_LOWER_ATTACK) | (1u << TRAINER_STATUS_LOWER_DEFENSE), MOVE_TICKLE, 2 },
    { 0, MOVE_TORMENT, 2 },
    { (1u << TRAINER_STATUS_HAZARD), MOVE_TOXIC_SPIKES, 2 },
    { (1u << TRAINER_STATUS_POISON) | (1u << TRAINER_STATUS_LOWER_SPEED), MOVE_TOXIC_THREAD, 2 },
    { 0, MOVE_TRICK_ROOM, 2 },
    { (1u << TRAINER_STATUS_LOWER_ATTACK) | (1u << TRAINER_STATUS_LOWER_SP_ATTACK) | (1u << TRAINER_STATUS_LOWER_SPEED), MOVE_VENOM_DRENCH, 2 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_WORK_UP, 2 },
    { (1u << TRAINER_STATUS_PROTECT), MOVE_PROTECT, 2 },
    { 0, MOVE_SUBSTITUTE, 2 },
    { (1u << TRAINER_STATUS_SELF_KO), MOVE_SELF_DESTRUCT, 2 },
    // A tier
    { (1u << TRAINER_STATUS_SETUP), MOVE_ACID_ARMOR, 3 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_AGILITY, 3 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_AMNESIA, 3 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_AUTOTOMIZE, 3 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_BULK_UP, 3 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_CALM_MIND, 3 },
    { (1u << TRAINER_STATUS_LOWER_ATTACK), MOVE_CHARM, 3 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_COIL, 3 },
    { (1u << TRAINER_STATUS_CONFUSION), MOVE_CONFUSE_RAY, 3 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_COSMIC_POWER, 3 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_CURSE, 3 },
    { (1u << TRAINER_STATUS_PROTECT), MOVE_DETECT, 3 },
    { 0, MOVE_DISABLE, 3 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_DOUBLE_TEAM, 3 },
    { (1u << TRAINER_STATUS_LOWER_SP_ATTACK), MOVE_EERIE_IMPULSE, 3 },
    { 0, MOVE_ENCORE, 3 },
    { (1u << TRAINER_STATUS_LOWER_SP_DEFENSE), MOVE_FAKE_TEARS, 3 },
    { (1u << TRAINER_STATUS_LOWER_ATTACK), MOVE_FEATHER_DANCE, 3 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_HONE_CLAWS, 3 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_IRON_DEFENSE, 3 },
    { (1u << TRAINER_STATUS_SCREEN_SPECIAL), MOVE_LIGHT_SCREEN, 3 },
    { (1u << TRAINER_STATUS_SLEEP), MOVE_LOVELY_KISS, 3 },
    { (1u << TRAINER_STATUS_RECOVERY), MOVE_MOONLIGHT, 3 },
    { (1u << TRAINER_STATUS_RECOVERY), MOVE_MORNING_SUN, 3 },
    { (1u << TRAINER_STATUS_SCREEN_PHYSICAL), MOVE_REFLECT, 3 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_ROCK_POLISH, 3 },
    { (1u << TRAINER_STATUS_SLEEP), MOVE_SLEEP_POWDER, 3 },
    { (1u << TRAINER_STATUS_PARALYSIS), MOVE_STUN_SPORE, 3 },
    { (1u << TRAINER_STATUS_RECOVERY), MOVE_SYNTHESIS, 3 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_TAKE_HEART, 3 },
    { 0, MOVE_TAUNT, 3 },
    { (1u << TRAINER_STATUS_PARALYSIS), MOVE_THUNDER_WAVE, 3 },
    { (1u << TRAINER_STATUS_POISON), MOVE_TOXIC, 3 },
    { 0, MOVE_WILL_O_WISP, 3 },
    { (1u << TRAINER_STATUS_RECOVERY), MOVE_WISH, 3 },
    { (1u << TRAINER_STATUS_SLEEP), MOVE_YAWN, 3 },
    { (1u << TRAINER_STATUS_SELF_KO), MOVE_EXPLOSION, 3 },
    // S tier
    { (1u << TRAINER_STATUS_SETUP), MOVE_BELLY_DRUM, 4 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_COTTON_GUARD, 4 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_DRAGON_DANCE, 4 },
    { (1u << TRAINER_STATUS_PARALYSIS), MOVE_GLARE, 4 },
    { 0, MOVE_LEECH_SEED, 4 },
    { (1u << TRAINER_STATUS_RECOVERY), MOVE_MILK_DRINK, 4 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_MINIMIZE, 4 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_NASTY_PLOT, 4 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_QUIVER_DANCE, 4 },
    { (1u << TRAINER_STATUS_RECOVERY), MOVE_RECOVER, 4 },
    { (1u << TRAINER_STATUS_RECOVERY), MOVE_ROOST, 4 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_SHELL_SMASH, 4 },
    { (1u << TRAINER_STATUS_RECOVERY), MOVE_SLACK_OFF, 4 },
    { (1u << TRAINER_STATUS_RECOVERY), MOVE_SOFT_BOILED, 4 },
    { (1u << TRAINER_STATUS_SLEEP), MOVE_SPORE, 4 },
    { (1u << TRAINER_STATUS_RECOVERY), MOVE_STRENGTH_SAP, 4 },
    { (1u << TRAINER_STATUS_PROTECT), MOVE_SPIKY_SHIELD, 4 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_SWORDS_DANCE, 4 },
    { (1u << TRAINER_STATUS_SETUP), MOVE_TAIL_GLOW, 4 },
    { (1u << TRAINER_STATUS_PARALYSIS), MOVE_NUZZLE, 4 },
    { 0, MOVE_FAKE_OUT, 4 },
    { (1u << TRAINER_STATUS_HAZARD), MOVE_STONE_AXE, 4 },
};

static const u16 sTrainerMoveBlacklist[] = {
    MOVE_AFTER_YOU, MOVE_FOLLOW_ME, MOVE_HELPING_HAND, MOVE_RAGE_POWDER,
    MOVE_QUASH, MOVE_WIDE_GUARD, MOVE_HEAL_PULSE, MOVE_TELEPORT,
    MOVE_SPLASH, MOVE_SKETCH, MOVE_GRUDGE, MOVE_SPITE,
    MOVE_EMBARGO, MOVE_SWEET_SCENT, MOVE_ROAR, MOVE_WHIRLWIND,
    MOVE_BLOCK, MOVE_MEAN_LOOK, MOVE_PERISH_SONG, MOVE_HEALING_WISH,
    MOVE_LUNAR_DANCE, MOVE_MEMENTO, MOVE_PARTING_SHOT, MOVE_RECYCLE,
    MOVE_SWITCHEROO, MOVE_TRICK, MOVE_SNATCH, MOVE_MAGIC_COAT,
    MOVE_IMPRISON, MOVE_QUICK_GUARD, MOVE_GUARD_SPLIT, MOVE_POWER_SPLIT,
    MOVE_GUARD_SWAP, MOVE_POWER_SWAP, MOVE_PSYCH_UP, MOVE_MIMIC,
    MOVE_KINESIS, MOVE_LASER_FOCUS, MOVE_MIST, MOVE_MISTY_TERRAIN,
    MOVE_BELCH, MOVE_DREAM_EATER, MOVE_SNORE, MOVE_SLEEP_TALK,
};
static u16 ScoreTrainerAttack(u16 move, const struct BattleMove *data, u8 level)
{
    u16 power = data->power;
    u8 accuracy = data->accuracy ? data->accuracy : 100;

    switch (data->effect) {
    case MOVE_EFFECT_HIT_TWICE:
    case MOVE_EFFECT_HIT_TWICE_AND_FLINCH:
        power *= 2;
        break;
    case MOVE_EFFECT_HIT_THREE_TIMES:
    case MOVE_EFFECT_HIT_THREE_TIMES_ALWAYS_CRITICAL:
    case MOVE_EFFECT_MULTI_HIT:
    case MOVE_EFFECT_POISON_MULTI_HIT:
        power *= 3;
        break;
    case MOVE_EFFECT_HIT_THREE_TIMES_INCREMENT_BASE_POWER_10:
        power = 60;
        break;
    case MOVE_EFFECT_HIT_THREE_TIMES_INCREMENT_BASE_POWER_20:
        power = 120;
        break;
    case MOVE_EFFECT_BEAT_UP:
        power = 40;
        break;
    case MOVE_EFFECT_LEVEL_DAMAGE_FLAT:
        power = level;
        break;
    case MOVE_EFFECT_DECREASE_POWER_WITH_LESS_USER_HP:
        if (move == MOVE_ERUPTION || move == MOVE_WATER_SPOUT) {
            return power * accuracy * 7 / 10;
        }
        break;
    case MOVE_EFFECT_POWER_BASED_ON_LOW_SPEED:
    case MOVE_EFFECT_INCREASE_POWER_WITH_WEIGHT:
    case MOVE_EFFECT_HEAVY_SLAM:
        power = 70;
        break;
    case MOVE_EFFECT_CHARGE_TURN_HIGH_CRIT:
    case MOVE_EFFECT_CHARGE_TURN_HIGH_CRIT_FLINCH:
    case MOVE_EFFECT_CHARGE_TURN_DEF_UP:
    case MOVE_EFFECT_CHARGE_TURN_SUN_SKIPS:
    case MOVE_EFFECT_CHARGE_TURN_SP_ATK_UP:
    case MOVE_EFFECT_CHARGE_TURN_SP_ATK_UP_RAIN_SKIPS:
    case MOVE_EFFECT_CHARGE_TURN_PARALYZE_HIT:
    case MOVE_EFFECT_CHARGE_TURN_BURN_HIT:
    case MOVE_EFFECT_FLY:
    case MOVE_EFFECT_DIVE:
    case MOVE_EFFECT_DIG:
    case MOVE_EFFECT_BOUNCE:
    case MOVE_EFFECT_SHADOW_FORCE:
        return power * accuracy * 4 / 10;
    case MOVE_EFFECT_RECHARGE_AFTER:
    case MOVE_EFFECT_HIT_IN_3_TURNS:
        return power * accuracy * 6 / 10;
    case MOVE_EFFECT_HIT_LAST_WHIFF_IF_HIT:
        return power * accuracy * 4 / 10;
    case MOVE_EFFECT_FAIL_IF_NOT_USED_ALL_OTHER_MOVES:
        return power * accuracy * 35 / 100;
    case MOVE_EFFECT_RECOIL_QUARTER:
    case MOVE_EFFECT_USER_DEF_SP_DEF_DOWN_HIT:
    case MOVE_EFFECT_USER_DEF_SP_DEF_SPEED_DOWN_HIT:
    case MOVE_EFFECT_USER_DEF_DOWN_HIT:
    case MOVE_EFFECT_USER_DEF_DOWN_HIT_REMOVE_PROTECT:
    case MOVE_EFFECT_USER_SPEED_DOWN_HIT:
    case MOVE_EFFECT_USER_SPEED_DOWN_2_HIT:
    case MOVE_EFFECT_CRASH_ON_MISS:
    case MOVE_EFFECT_CONFUSE_HIT_CRASH_ON_MISS:
        return power * accuracy * 9 / 10;
    case MOVE_EFFECT_RECOIL_THIRD:
    case MOVE_EFFECT_RECOIL_BURN_HIT:
    case MOVE_EFFECT_RECOIL_PARALYZE_HIT:
        return power * accuracy * 85 / 100;
    case MOVE_EFFECT_RECOIL_HALF:
        return power * accuracy * 7 / 10;
    case MOVE_EFFECT_USER_SP_ATK_DOWN_2:
        return power * accuracy * 75 / 100;
    case MOVE_EFFECT_USER_ATK_DEF_DOWN_HIT:
    case MOVE_EFFECT_CONTINUE_AND_CONFUSE_SELF:
        return power * accuracy * 8 / 10;
    case MOVE_EFFECT_DOUBLE_POWER_EACH_TURN_LOCK_INTO:
        if (move == MOVE_ROLLOUT) {
            return power * accuracy * 2;
        }
        return power * accuracy * 8 / 10;
    }

    // Keep hundredths so accuracy differences do not get truncated.
    int score = power * accuracy;
    switch (move) {
    case MOVE_RAPID_SPIN:
        return score * 130 / 100;
    case MOVE_KNOCK_OFF:
        return score * 125 / 100;
    case MOVE_FLAME_CHARGE:
    case MOVE_SNARL:
    case MOVE_ROCK_TOMB:
    case MOVE_ICY_WIND:
    case MOVE_FREEZE_DRY:
        return score * 120 / 100;
    case MOVE_PSYSHIELD_BASH:
    case MOVE_U_TURN:
    case MOVE_VOLT_SWITCH:
        return score * 110 / 100;
    default:
        if (data->priority > 0 && data->power <= 40) {
            return score * 140 / 100;
        }
        return score;
    }
}

static void AddTrainerMove(struct TrainerMoveCandidate *pool, int *count, u16 move, u8 tm, u8 level, u32 stabTypes)
{
    if (move == MOVE_NONE || move > NUM_OF_MOVES) {
        return;
    }
    for (int i = 0; i < *count; i++) {
        if (pool[i].move == move) {
            return;
        }
    }
    for (u32 i = 0; i < NELEMS(sTrainerMoveBlacklist); i++) {
        if (sTrainerMoveBlacklist[i] == move) {
            return;
        }
    }

    struct BattleMove data;
    ReadWholeNarcMemberByIdPair(&data, ARC_MOVE_DATA, move);
    if ((data.flag & FLAG_UNUSED_MOVE) || data.effect == MOVE_EFFECT_ONE_HIT_KO) {
        return;
    }

    struct TrainerMoveCandidate candidate = { 0, move, 0, data.type, tm, 0 };
    for (u32 i = 0; i < NELEMS(sTrainerStatusMoves); i++) {
        if (sTrainerStatusMoves[i].move == move) {
            candidate.type = TRAINER_STATUS_TYPE;
            candidate.score = sTrainerStatusMoves[i].tier;
            candidate.groupMask = sTrainerStatusMoves[i].groups;
            break;
        }
    }
    if (data.split == SPLIT_STATUS && candidate.type != TRAINER_STATUS_TYPE) {
        return;
    }
    if (data.split != SPLIT_STATUS && move != MOVE_EXPLOSION && move != MOVE_SELF_DESTRUCT) {
        u16 score = ScoreTrainerAttack(move, &data, level);
        if (stabTypes & (1u << data.type)) {
            score = score * 3 / 2;
        }
        if (candidate.type == TRAINER_STATUS_TYPE) {
            candidate.utilityAttackScore = score;
        } else {
            candidate.score = score;
        }
    }
    pool[(*count)++] = candidate;
}

static void SetTrainerFallbackMoves(struct PartyPokemon *mon, const u32 *learnset, u8 level)
{
    u16 moves[TRAINER_MOVE_SLOTS];
    int count = 0;
    for (int i = 0; i < MAX_LEVELUP_MOVES && LEVEL_UP_LEARNSET_MOVE(learnset[i]) != LEVEL_UP_LEARNSET_END; i++) {
        u16 move = LEVEL_UP_LEARNSET_MOVE(learnset[i]);
        if (move == MOVE_NONE || LEVEL_UP_LEARNSET_LEVEL(learnset[i]) > level) {
            continue;
        }
        int slot = 0;
        while (slot < count && moves[slot] != move) {
            slot++;
        }
        if (slot < count) {
            continue;
        }
        if (count == TRAINER_MOVE_SLOTS) {
            for (int j = 1; j < count; j++) {
                moves[j - 1] = moves[j];
            }
            count--;
        }
        moves[count++] = move;
    }
    for (int slot = 0; slot < count; slot++) {
        SetPartyPokemonMoveAtPos(mon, moves[slot], slot);
    }
}

static void BuildTrainerMonMoves(struct PartyPokemon *mon, u8 *tmCopies, u8 badgeCount)
{
    // Cut, Fly, Surf, Strength, Whirlpool, Rock Smash, Waterfall, Rock Climb.
    static const u8 hmBadges[TRAINER_HM_COUNT] = { 2, 5, 6, 7, 10, 3, 13, 16 };
    struct TrainerMoveCandidate pool[MAX_LEVELUP_MOVES + TRAINER_TM_COUNT + TRAINER_HM_COUNT];
    u32 learnset[MAX_LEVELUP_MOVES];
    u16 species = GetMonData(mon, MON_DATA_SPECIES, NULL);
    u8 form = GetMonData(mon, MON_DATA_FORM, NULL);
    u8 level = GetMonData(mon, MON_DATA_LEVEL, NULL);
    u32 stabTypes = (1u << GetMonData(mon, MON_DATA_TYPE_1, NULL))
        | (1u << GetMonData(mon, MON_DATA_TYPE_2, NULL));
    u32 attackTypes = 0;
    u32 statusGroups = 0;
    int count = 0;

    LoadLevelUpLearnset_HandleAlternateForm(species, form, learnset);
    for (int i = 0; i < MAX_LEVELUP_MOVES && LEVEL_UP_LEARNSET_MOVE(learnset[i]) != LEVEL_UP_LEARNSET_END; i++) {
        if (LEVEL_UP_LEARNSET_LEVEL(learnset[i]) <= level) {
            AddTrainerMove(pool, &count, LEVEL_UP_LEARNSET_MOVE(learnset[i]), FREE_TRAINER_MOVE, level, stabTypes);
        }
    }
    // Add free sources before TMs so teaching never spends a redundant copy.
    for (int i = 0; i < TRAINER_HM_COUNT; i++) {
        if (badgeCount >= hmBadges[i] && GetTMHMCompatBySpeciesAndForm(species, form, TRAINER_TM_COUNT + i)) {
            AddTrainerMove(pool, &count, ItemToMachineMove(ITEM_HM01 + i), FREE_TRAINER_MOVE, level, stabTypes);
        }
    }
    for (int i = 0; i < TRAINER_TM_COUNT; i++) {
        if (tmCopies[i] && GetTMHMCompatBySpeciesAndForm(species, form, i)) {
            AddTrainerMove(pool, &count, ItemToMachineMove(ITEM_TM001 + i), i, level, stabTypes);
        }
    }

    ClearMonMoves(mon);
    for (int slot = 0; slot < TRAINER_MOVE_SLOTS; slot++) {
        int bestAttack = -1;
        int bestStatus = -1;
        u16 attackScore = 0;
        u16 statusScore = 0;
        for (int i = 0; i < count; i++) {
            const struct TrainerMoveCandidate *move = &pool[i];
            if (move->move == MOVE_NONE || (move->tm != FREE_TRAINER_MOVE && !tmCopies[move->tm])) {
                continue;
            }
            BOOL utility = move->type == TRAINER_STATUS_TYPE;
            if ((utility && slot == 0 && move->utilityAttackScore)
                || (!utility && !(attackTypes & (1u << move->type)))) {
                u16 score = utility ? move->utilityAttackScore : move->score;
                if (bestAttack < 0 || score > attackScore || (score == attackScore && (gf_rand() & 1))) {
                    bestAttack = i;
                    attackScore = score;
                }
            }
            if (utility) {
                if (!(statusGroups & move->groupMask) && (bestStatus < 0 || move->score > statusScore
                    || (move->score == statusScore && (gf_rand() & 1)))) {
                    bestStatus = i;
                    statusScore = move->score;
                }
            }
        }

        int chosen = bestAttack;
        if (bestStatus >= 0 && (bestAttack < 0 || (slot != 0 && (gf_rand() & 1)))) {
            chosen = bestStatus;
        }
        if (chosen < 0) {
            if (slot == 0) {
                SetTrainerFallbackMoves(mon, learnset, level);
            }
            break;
        }
        struct TrainerMoveCandidate *move = &pool[chosen];
        SetPartyPokemonMoveAtPos(mon, move->move, slot);
        if (move->type == TRAINER_STATUS_TYPE) {
            statusGroups |= move->groupMask;
        } else {
            attackTypes |= 1u << move->type;
        }
        if (move->tm != FREE_TRAINER_MOVE) {
            tmCopies[move->tm]--;
        }
        move->move = MOVE_NONE;
    }
}

void BuildGeneratedTrainerMovesets(struct PartyPokemon **party, const int *order, int count, u8 badgeCount)
{
    u8 tmCopies[TRAINER_TM_COUNT] = {0};
    u8 eligibleTms[TRAINER_TM_COUNT];
    u8 numEligible = 0;

    for (int i = 0; i < TRAINER_TM_COUNT; i++) {
        if (sTrainerTmUnlocks[i] && sTrainerTmUnlocks[i] <= badgeCount + 1) {
            eligibleTms[numEligible++] = i;
        }
    }
    for (int roll = 0; numEligible && roll < badgeCount * 5; roll++) {
        tmCopies[eligibleTms[gf_rand() % numEligible]]++;
    }
    for (int i = count - 1; i >= 0; i--) {
        BuildTrainerMonMoves(party[order[i]], tmCopies, badgeCount);
    }
}
