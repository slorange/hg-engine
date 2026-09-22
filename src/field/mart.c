#include "debug.h"
#include "types.h"

#include "constants/item.h"

#include "pokemon.h"
#include "save.h"
#include "script.h"

#ifdef MART_EXPANSION

struct MartItem {
    u16 item_id;
    u16 override_cost;
};

struct BadgeMartItems {
    u16 item_id;
    u8 required_badges;
};

// note: limited to 203 items (~34 pages)
const struct BadgeMartItems sBadgeMart[] = {
    { ITEM_POKE_BALL, 0 },
    { ITEM_GREAT_BALL, 2 },
    { ITEM_ULTRA_BALL, 4 },
    { ITEM_NET_BALL, 6 },
    { ITEM_REPEAT_BALL, 6 },
    { ITEM_TIMER_BALL, 8 },
    { ITEM_REPEL, 0 },
    { ITEM_SUPER_REPEL, 4 },
    { ITEM_MAX_REPEL, 8 },
    { ITEM_ESCAPE_ROPE, 0 },
    { ITEM_POKE_DOLL, 0 },
    { ITEM_SITRUS_BERRY, 4 },
    { ITEM_LUM_BERRY, 6 },
    { ITEM_TM070, 1 },
    { ITEM_CLEANSE_TAG, 1 },
    { ITEM_WHITE_HERB, 3 },
    { ITEM_MENTAL_HERB, 3 },
    { ITEM_POWER_HERB, 3 },
    { ITEM_MUSCLE_BAND, 5 },
    { ITEM_WISE_GLASSES, 5 },
    { ITEM_BIG_ROOT, 6 },
    { ITEM_EXPERT_BELT, 7 },
    { ITEM_LIGHT_CLAY, 7 },
    { ITEM_METRONOME, 8 },
    { ITEM_LEFTOVERS, 9 },
    { ITEM_SHELL_BELL, 10 },
    { ITEM_FOCUS_SASH, 10 },
    { ITEM_CHOICE_BAND, 11 },
    { ITEM_CHOICE_SPECS, 11 },
    { ITEM_LIFE_ORB, 12 },
    { ITEM_CHOICE_SCARF, 12 },
};

void LONG_CALL InitMartUI(void *taskManager, FieldSystem *fieldSystem, const u16 *items, int kind, int buySell, int decoWhich, const struct MartItem *priceOverrides);

u16 sCherrygroveCityMart[] = {
    0xFFFF
};

u16 sVioletCityMart[] = {
    ITEM_RAZOR_FANG, ITEM_COBA_BERRY, 0xFFFF
};

u16 sAzaleaCityMart[] = {
    ITEM_KINGS_ROCK, ITEM_SILVER_POWDER, ITEM_TANGA_BERRY, 0xFFFF
};

u16 sGoldenrodDepartmentUpper2F[] = {
    ITEM_POKE_BALL, ITEM_GREAT_BALL, ITEM_ULTRA_BALL, ITEM_ESCAPE_ROPE, ITEM_POKE_DOLL, ITEM_REPEL, ITEM_SUPER_REPEL, ITEM_MAX_REPEL, ITEM_CHERI_BERRY, ITEM_CHESTO_BERRY, ITEM_PECHA_BERRY, ITEM_RAWST_BERRY, ITEM_ASPEAR_BERRY, ITEM_LEPPA_BERRY, ITEM_ORAN_BERRY, ITEM_PERSIM_BERRY, 0xFFFF
};

u16 sGoldenrodDepartmentLower2F[] = {
    ITEM_LINKING_CORD, ITEM_CHILAN_BERRY, ITEM_SILK_SCARF, ITEM_GRIP_CLAW, ITEM_STICKY_BARB, ITEM_SHED_SHELL, 0xFFFF
};

u16 sGoldenrodDepartment3F[] = {
    ITEM_POWER_BRACER, ITEM_POWER_BELT, ITEM_POWER_LENS, ITEM_POWER_BAND, ITEM_POWER_ANKLET, ITEM_POWER_WEIGHT, ITEM_MACHO_BRACE, 0xFFFF
};

u16 sGoldenrodDepartment4F[] = {
    ITEM_PROTEIN, ITEM_IRON, ITEM_CALCIUM, ITEM_ZINC, ITEM_CARBOS, ITEM_HP_UP, ITEM_RARE_CANDY, ITEM_PP_UP, ITEM_PP_MAX, 0xFFFF
};

u16 sGoldenrodDepartment5F[] = {
    ITEM_TM016, ITEM_TM017, ITEM_TM033, ITEM_TM043, ITEM_TM054, ITEM_TM063, ITEM_TM064, ITEM_TM083, 0xFFFF
};

u16 sGoldenrodHerbs[] = {
    ITEM_POMEG_BERRY, ITEM_KELPSY_BERRY, ITEM_QUALOT_BERRY, ITEM_HONDEW_BERRY, ITEM_GREPA_BERRY, ITEM_TAMATO_BERRY, 0xFFFF
};

u16 sEcruteakMart[] = {
    ITEM_FIRE_STONE, ITEM_CHARCOAL, ITEM_OCCA_BERRY, ITEM_MAGMARIZER, ITEM_FLAME_ORB, 0xFFFF
};

u16 sOlivineMart[] = {
    ITEM_SECRET_MEDICINE, ITEM_METAL_COAT, ITEM_BABIRI_BERRY, 0xFFFF
};

u16 sCianwoodPharmacy[] = {
    ITEM_POKE_BALL, ITEM_DAWN_STONE, ITEM_BLACK_BELT, ITEM_CHOPLE_BERRY, 0xFFFF
};

u16 sBlackthornAndBattleFrontierMart[] = {
    ITEM_DRAGON_SCALE, ITEM_DRAGON_FANG, ITEM_HABAN_BERRY, ITEM_HEART_SCALE, 0xFFFF
};

u16 sIndigoPlateau[] = {
    ITEM_ULTRA_BALL, ITEM_TIMER_BALL, ITEM_MAX_REPEL, ITEM_LUM_BERRY,
    ITEM_LEFTOVERS, ITEM_SHELL_BELL, ITEM_FOCUS_SASH,
    ITEM_CHOICE_BAND, ITEM_CHOICE_SPECS, ITEM_CHOICE_SCARF, ITEM_LIFE_ORB,
    0xFFFF
};

u16 sVermilionAndSafariMart[] = {
    ITEM_THUNDER_STONE, ITEM_ELECTIRIZER, ITEM_MAGNET, ITEM_WACAN_BERRY, 0xFFFF
};

u16 sSaffronMart[] = {
    ITEM_UP_GRADE, ITEM_DUBIOUS_DISC, ITEM_TWISTED_SPOON, ITEM_PAYAPA_BERRY, 0xFFFF
};

u16 sLavenderMart[] = {
    ITEM_DUSK_STONE, ITEM_REAPER_CLOTH, ITEM_BLACK_GLASSES, ITEM_SPELL_TAG, ITEM_KASIB_BERRY, ITEM_COLBUR_BERRY, 0xFFFF
};

u16 sCeruleanMart[] = {
    ITEM_WATER_STONE, ITEM_DEEP_SEA_TOOTH, ITEM_DEEP_SEA_SCALE, ITEM_MYSTIC_WATER, ITEM_PASSHO_BERRY, 0xFFFF
};

u16 sCeladonDepartmentUpper2F[] = {
    ITEM_CHERI_BERRY, ITEM_CHESTO_BERRY, ITEM_PECHA_BERRY, ITEM_RAWST_BERRY, ITEM_ASPEAR_BERRY, ITEM_LEPPA_BERRY, ITEM_ORAN_BERRY, ITEM_PERSIM_BERRY, 0xFFFF
};

u16 sCeladonDepartmentLower2F[] = {
    ITEM_POKE_BALL, ITEM_GREAT_BALL, ITEM_ULTRA_BALL, ITEM_ESCAPE_ROPE, ITEM_POKE_DOLL, ITEM_REPEL, ITEM_SUPER_REPEL, ITEM_MAX_REPEL, 0xFFFF
};

u16 sCeladonDepartment3F[] = {
    ITEM_TM012, ITEM_TM020, ITEM_TM021, ITEM_TM028, ITEM_TM041, ITEM_TM076, ITEM_TM078, ITEM_TM087, 0xFFFF
};

u16 sCeladonDepartment4F[] = {
    ITEM_LINKING_CORD, ITEM_SUN_STONE, ITEM_LEAF_STONE, ITEM_RINDO_BERRY, ITEM_MIRACLE_SEED, ITEM_GRIP_CLAW, ITEM_STICKY_BARB, ITEM_SHED_SHELL, 0xFFFF
};

u16 sCeladonDepartmentLeft5F[] = {
    ITEM_POWER_BRACER, ITEM_POWER_BELT, ITEM_POWER_LENS, ITEM_POWER_BAND, ITEM_POWER_ANKLET, ITEM_POWER_WEIGHT, ITEM_MACHO_BRACE, 0xFFFF
};

u16 sCeladonDepartmentRight5F[] = {
    ITEM_PROTEIN, ITEM_IRON, ITEM_CALCIUM, ITEM_ZINC, ITEM_CARBOS, ITEM_HP_UP, ITEM_RARE_CANDY, ITEM_PP_UP, ITEM_PP_MAX, 0xFFFF
};

u16 sFuschiaMart[] = {
    ITEM_SHINY_STONE, ITEM_POISON_BARB, ITEM_KEBIA_BERRY, ITEM_TOXIC_ORB, ITEM_BLACK_SLUDGE, 0xFFFF
};

u16 sPewterMart[] = {
    ITEM_HARD_STONE, ITEM_CHARTI_BERRY, 0xFFFF
};

u16 sViridianMart[] = {
    ITEM_PROTECTOR, ITEM_SOFT_SAND, ITEM_SHUCA_BERRY, 0xFFFF
};

u16 sMtMoonSquare[] = {
    ITEM_MOON_STONE, 0xFFFF
};

u16 sMahoganyPreRocketHideout[] = {
    ITEM_TINY_MUSHROOM, ITEM_POKE_BALL, ITEM_POTION, 0xFFFF
};

u16 sMahoganyPostRocketHideout[] = {
    ITEM_POKE_BALL, ITEM_NEVER_MELT_ICE, ITEM_YACHE_BERRY, ITEM_RAZOR_CLAW, 0xFFFF
};

BOOL ScrCmd_MartBuy(SCRIPTCONTEXT *ctx)
{
    u16 unused UNUSED = ScriptGetVar(ctx);

    u16 items[NELEMS(sBadgeMart) + 1];
    struct PlayerProfile *profile;
    u8 badgeCount;
    u8 index = 0;
    u32 i;

    profile = Sav2_PlayerData_GetProfileAddr(ctx->fsys->savedata);
    badgeCount = PlayerProfile_CountBadges(profile);

    for (i = 0; i < NELEMS(sBadgeMart); i++) {
        if (badgeCount >= sBadgeMart[i].required_badges) {
            items[index] = sBadgeMart[i].item_id;
            index++;
        }
    }

    items[index] = 0xFFFF;
    InitMartUI(ctx->taskman, ctx->fsys, items, 0, 0, 0, 0); // this doesn't honor price overrides
    return TRUE;
}

#endif // MART_EXPANSION

#ifdef POKEATHLON_SHOP_EXPANSION

const struct MartItem sPokeathlonShop_Sunday[] = {
    { ITEM_RED_APRICORN, 200 },
    { ITEM_BLUE_APRICORN, 200 },
    { ITEM_BLACK_APRICORN, 200 },
    { ITEM_MOOMOO_MILK, 100 },
    { ITEM_KINGS_ROCK, 3000 },
    { ITEM_HEART_SCALE, 1000 },
    { 0xFFFF, 0 },
};

const struct MartItem sPokeathlonShop_Monday[] = {
    { ITEM_RED_APRICORN, 200 },
    { ITEM_BLUE_APRICORN, 200 },
    { ITEM_GREEN_APRICORN, 200 },
    { ITEM_MOOMOO_MILK, 100 },
    { ITEM_MOON_STONE, 3000 },
    { ITEM_RARE_CANDY, 2000 },
    { 0xFFFF, 0 },
};

const struct MartItem sPokeathlonShop_Tuesday[] = {
    { ITEM_YELLOW_APRICORN, 200 },
    { ITEM_PINK_APRICORN, 200 },
    { ITEM_WHITE_APRICORN, 200 },
    { ITEM_MOOMOO_MILK, 100 },
    { ITEM_FIRE_STONE, 2500 },
    { ITEM_PP_UP, 1000 },
    { 0xFFFF, 0 },
};

const struct MartItem sPokeathlonShop_Wednesday[] = {
    { ITEM_BLUE_APRICORN, 200 },
    { ITEM_PINK_APRICORN, 200 },
    { ITEM_BLACK_APRICORN, 200 },
    { ITEM_MOOMOO_MILK, 100 },
    { ITEM_WATER_STONE, 2500 },
    { ITEM_HEART_SCALE, 1000 },
    { 0xFFFF, 0 },
};

const struct MartItem sPokeathlonShop_Thursday[] = {
    { ITEM_YELLOW_APRICORN, 200 },
    { ITEM_PINK_APRICORN, 200 },
    { ITEM_WHITE_APRICORN, 200 },
    { ITEM_MOOMOO_MILK, 100 },
    { ITEM_THUNDER_STONE, 2500 },
    { ITEM_PP_UP, 1000 },
    { 0xFFFF, 0 },
};

const struct MartItem sPokeathlonShop_Friday[] = {
    { ITEM_RED_APRICORN, 200 },
    { ITEM_YELLOW_APRICORN, 200 },
    { ITEM_GREEN_APRICORN, 200 },
    { ITEM_MOOMOO_MILK, 100 },
    { ITEM_METAL_COAT, 2500 },
    { ITEM_NUGGET, 500 },
    { 0xFFFF, 0 },
};

const struct MartItem sPokeathlonShop_Saturday[] = {
    { ITEM_GREEN_APRICORN, 200 },
    { ITEM_WHITE_APRICORN, 200 },
    { ITEM_BLACK_APRICORN, 200 },
    { ITEM_MOOMOO_MILK, 100 },
    { ITEM_LEAF_STONE, 2500 },
    { ITEM_RARE_CANDY, 2000 },
    { 0xFFFF, 0 },
};

const struct MartItem sPokeathlonShop_NatdexSunday[] = {
    { ITEM_RED_APRICORN, 200 },
    { ITEM_BLUE_APRICORN, 200 },
    { ITEM_BLACK_APRICORN, 200 },
    { ITEM_MOOMOO_MILK, 100 },
    { ITEM_KINGS_ROCK, 3000 },
    { ITEM_HEART_SCALE, 1000 },
    { ITEM_FULL_RESTORE, 500 },
    { ITEM_NUGGET, 500 },
    { ITEM_SUN_STONE, 3000 },
    { ITEM_FIRE_STONE, 2500 },
    { ITEM_SHINY_STONE, 3000 },
    { ITEM_DAWN_STONE, 3000 },
    { 0xFFFF, 0 },
};

const struct MartItem sPokeathlonShop_NatdexMonday[] = {
    { ITEM_RED_APRICORN, 200 },
    { ITEM_BLUE_APRICORN, 200 },
    { ITEM_GREEN_APRICORN, 200 },
    { ITEM_MOOMOO_MILK, 100 },
    { ITEM_MOON_STONE, 3000 },
    { ITEM_RARE_CANDY, 2000 },
    { ITEM_FULL_RESTORE, 500 },
    { ITEM_KINGS_ROCK, 3000 },
    { ITEM_SUN_STONE, 3000 },
    { ITEM_WATER_STONE, 2500 },
    { ITEM_SHINY_STONE, 3000 },
    { ITEM_DUSK_STONE, 3000 },
    { 0xFFFF, 0 },
};

const struct MartItem sPokeathlonShop_NatdexTuesday[] = {
    { ITEM_YELLOW_APRICORN, 200 },
    { ITEM_PINK_APRICORN, 200 },
    { ITEM_WHITE_APRICORN, 200 },
    { ITEM_MOOMOO_MILK, 100 },
    { ITEM_FIRE_STONE, 2500 },
    { ITEM_PP_UP, 1000 },
    { ITEM_FULL_RESTORE, 500 },
    { ITEM_METAL_COAT, 2500 },
    { ITEM_WATER_STONE, 2500 },
    { ITEM_LEAF_STONE, 2500 },
    { ITEM_DUSK_STONE, 3000 },
    { ITEM_DAWN_STONE, 3000 },
    { 0xFFFF, 0 },
};

const struct MartItem sPokeathlonShop_NatdexWednesday[] = {
    { ITEM_BLUE_APRICORN, 200 },
    { ITEM_PINK_APRICORN, 200 },
    { ITEM_BLACK_APRICORN, 200 },
    { ITEM_MOOMOO_MILK, 100 },
    { ITEM_WATER_STONE, 2500 },
    { ITEM_HEART_SCALE, 1000 },
    { ITEM_FULL_RESTORE, 500 },
    { ITEM_DRAGON_SCALE, 2500 },
    { ITEM_THUNDER_STONE, 2500 },
    { ITEM_MOON_STONE, 3000 },
    { ITEM_SHINY_STONE, 3000 },
    { ITEM_DAWN_STONE, 3000 },
    { 0xFFFF, 0 },
};

const struct MartItem sPokeathlonShop_NatdexThursday[] = {
    { ITEM_YELLOW_APRICORN, 200 },
    { ITEM_PINK_APRICORN, 200 },
    { ITEM_WHITE_APRICORN, 200 },
    { ITEM_MOOMOO_MILK, 100 },
    { ITEM_THUNDER_STONE, 2500 },
    { ITEM_PP_UP, 1000 },
    { ITEM_FULL_RESTORE, 500 },
    { ITEM_KINGS_ROCK, 3000 },
    { ITEM_FIRE_STONE, 2500 },
    { ITEM_LEAF_STONE, 2500 },
    { ITEM_SHINY_STONE, 3000 },
    { ITEM_DUSK_STONE, 3000 },
    { 0xFFFF, 0 },
};

const struct MartItem sPokeathlonShop_NatdexFriday[] = {
    { ITEM_RED_APRICORN, 200 },
    { ITEM_YELLOW_APRICORN, 200 },
    { ITEM_GREEN_APRICORN, 200 },
    { ITEM_MOOMOO_MILK, 100 },
    { ITEM_METAL_COAT, 2500 },
    { ITEM_NUGGET, 500 },
    { ITEM_FULL_RESTORE, 500 },
    { ITEM_DRAGON_SCALE, 2500 },
    { ITEM_WATER_STONE, 2500 },
    { ITEM_SUN_STONE, 3000 },
    { ITEM_DUSK_STONE, 3000 },
    { ITEM_DAWN_STONE, 3000 },
    { 0xFFFF, 0 },
};

const struct MartItem sPokeathlonShop_NatdexSaturday[] = {
    { ITEM_GREEN_APRICORN, 200 },
    { ITEM_WHITE_APRICORN, 200 },
    { ITEM_BLACK_APRICORN, 200 },
    { ITEM_MOOMOO_MILK, 100 },
    { ITEM_LEAF_STONE, 2500 },
    { ITEM_RARE_CANDY, 2000 },
    { ITEM_FULL_RESTORE, 500 },
    { ITEM_METAL_COAT, 2500 },
    { ITEM_THUNDER_STONE, 2500 },
    { ITEM_SHINY_STONE, 3000 },
    { ITEM_DUSK_STONE, 3000 },
    { ITEM_DAWN_STONE, 3000 },
    { 0xFFFF, 0 },
};

#endif // POKEATHLON_SHOP_EXPANSION
