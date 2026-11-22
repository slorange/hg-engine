#include "config.h"
#include "battle.h"
#include "constants/file.h"
#include "constants/item.h"
#include "constants/species.h"
#include "pokemon.h"

#define TRAINER_ITEM_TYPE_COUNT (TYPE_DARK + 1)

enum TrainerItemAttackRequirement {
    TRAINER_ITEM_ANY_SET,
    TRAINER_ITEM_ANY_ATTACK,
    TRAINER_ITEM_PHYSICAL,
    TRAINER_ITEM_SPECIAL,
};

struct TrainerItemUnlock {
    u16 item;
    u8 badges;
    u8 requirement;
};

static const struct TrainerItemUnlock sTrainerItemUnlocks[] = {
    { ITEM_ORAN_BERRY, 0, TRAINER_ITEM_ANY_SET },
    { ITEM_CHERI_BERRY, 0, TRAINER_ITEM_ANY_SET },
    { ITEM_CHESTO_BERRY, 0, TRAINER_ITEM_ANY_SET },
    { ITEM_PECHA_BERRY, 0, TRAINER_ITEM_ANY_SET },
    { ITEM_RAWST_BERRY, 0, TRAINER_ITEM_ANY_SET },
    { ITEM_ASPEAR_BERRY, 0, TRAINER_ITEM_ANY_SET },
    { ITEM_PERSIM_BERRY, 0, TRAINER_ITEM_ANY_SET },
    { ITEM_MENTAL_HERB, 3, TRAINER_ITEM_ANY_SET },
    { ITEM_SITRUS_BERRY, 4, TRAINER_ITEM_ANY_SET },
    { ITEM_MUSCLE_BAND, 5, TRAINER_ITEM_PHYSICAL },
    { ITEM_WISE_GLASSES, 5, TRAINER_ITEM_SPECIAL },
    { ITEM_METRONOME, 5, TRAINER_ITEM_ANY_ATTACK },
    { ITEM_QUICK_CLAW, 5, TRAINER_ITEM_ANY_SET },
    { ITEM_FOCUS_BAND, 5, TRAINER_ITEM_ANY_SET },
    { ITEM_LUM_BERRY, 6, TRAINER_ITEM_ANY_SET },
    { ITEM_LIECHI_BERRY, 6, TRAINER_ITEM_PHYSICAL },
    { ITEM_PETAYA_BERRY, 6, TRAINER_ITEM_SPECIAL },
    { ITEM_SALAC_BERRY, 6, TRAINER_ITEM_ANY_SET },
    { ITEM_STARF_BERRY, 6, TRAINER_ITEM_ANY_SET },
    { ITEM_EXPERT_BELT, 7, TRAINER_ITEM_ANY_ATTACK },
    { ITEM_SCOPE_LENS, 8, TRAINER_ITEM_ANY_ATTACK },
    { ITEM_RAZOR_CLAW, 8, TRAINER_ITEM_ANY_ATTACK },
    { ITEM_KINGS_ROCK, 8, TRAINER_ITEM_ANY_ATTACK },
    { ITEM_RAZOR_FANG, 8, TRAINER_ITEM_ANY_ATTACK },
    { ITEM_LEFTOVERS, 9, TRAINER_ITEM_ANY_SET },
    { ITEM_BRIGHT_POWDER, 9, TRAINER_ITEM_ANY_SET },
    { ITEM_SHELL_BELL, 10, TRAINER_ITEM_ANY_ATTACK },
    { ITEM_FOCUS_SASH, 10, TRAINER_ITEM_ANY_SET },
    { ITEM_LIFE_ORB, 12, TRAINER_ITEM_ANY_ATTACK },
};

static const struct { u16 species, item; } sTrainerSpeciesItems[] = {
    { SPECIES_PIKACHU, ITEM_LIGHT_BALL },
    { SPECIES_CUBONE, ITEM_THICK_CLUB },
    { SPECIES_MAROWAK, ITEM_THICK_CLUB },
    { SPECIES_FARFETCHD, ITEM_LEEK },
    { SPECIES_DITTO, ITEM_QUICK_POWDER },
    { SPECIES_DITTO, ITEM_METAL_POWDER },
    { SPECIES_CLAMPERL, ITEM_DEEP_SEA_TOOTH },
    { SPECIES_CLAMPERL, ITEM_DEEP_SEA_SCALE },
};

static const struct { u16 booster, berry; } sTrainerTypeItems[TRAINER_ITEM_TYPE_COUNT] = {
    [TYPE_NORMAL]   = { ITEM_SILK_SCARF,      ITEM_CHILAN_BERRY },
    [TYPE_FIGHTING] = { ITEM_BLACK_BELT,      ITEM_CHOPLE_BERRY },
    [TYPE_FLYING]   = { ITEM_SHARP_BEAK,      ITEM_COBA_BERRY },
    [TYPE_POISON]   = { ITEM_POISON_BARB,     ITEM_KEBIA_BERRY },
    [TYPE_GROUND]   = { ITEM_SOFT_SAND,       ITEM_SHUCA_BERRY },
    [TYPE_ROCK]     = { ITEM_HARD_STONE,      ITEM_CHARTI_BERRY },
    [TYPE_BUG]      = { ITEM_SILVER_POWDER,   ITEM_TANGA_BERRY },
    [TYPE_GHOST]    = { ITEM_SPELL_TAG,       ITEM_KASIB_BERRY },
    [TYPE_STEEL]    = { ITEM_METAL_COAT,      ITEM_BABIRI_BERRY },
    [TYPE_FAIRY]    = { ITEM_FAIRY_FEATHER,   ITEM_ROSELI_BERRY },
    [TYPE_FIRE]     = { ITEM_CHARCOAL,        ITEM_OCCA_BERRY },
    [TYPE_WATER]    = { ITEM_MYSTIC_WATER,    ITEM_PASSHO_BERRY },
    [TYPE_GRASS]    = { ITEM_MIRACLE_SEED,    ITEM_RINDO_BERRY },
    [TYPE_ELECTRIC] = { ITEM_MAGNET,          ITEM_WACAN_BERRY },
    [TYPE_PSYCHIC]  = { ITEM_TWISTED_SPOON,   ITEM_PAYAPA_BERRY },
    [TYPE_ICE]      = { ITEM_NEVER_MELT_ICE,  ITEM_YACHE_BERRY },
    [TYPE_DRAGON]   = { ITEM_DRAGON_FANG,     ITEM_HABAN_BERRY },
    [TYPE_DARK]     = { ITEM_BLACK_GLASSES,   ITEM_COLBUR_BERRY },
};

// The live battle table is in a different overlay. Share its source rows.
static const u8 sTrainerTypeMatchups[][3] = {
#include "battle_type_matchups.inc"
};

static void GetTrainerTypeWeaknesses(struct PartyPokemon *mon, u16 *effectiveness)
{
    u8 type1 = GetMonData(mon, MON_DATA_TYPE_1, NULL);
    u8 type2 = GetMonData(mon, MON_DATA_TYPE_2, NULL);

    for (int type = 0; type < TRAINER_ITEM_TYPE_COUNT; type++) {
        effectiveness[type] = 100;
    }
    for (u32 i = 0; i < NELEMS(sTrainerTypeMatchups); i++) {
        const u8 *row = sTrainerTypeMatchups[i];
        if (row[0] < TRAINER_ITEM_TYPE_COUNT && (row[1] == type1 || row[1] == type2)) {
            effectiveness[row[0]] = effectiveness[row[0]] * row[2] / TYPE_MUL_NORMAL;
        }
    }
}

void SetGeneratedTrainerHeldItem(struct PartyPokemon *mon, u8 badgeCount)
{
    u16 pool[NELEMS(sTrainerItemUnlocks) + NELEMS(sTrainerSpeciesItems) + 2 * TRAINER_ITEM_TYPE_COUNT];
    u16 species = GetMonData(mon, MON_DATA_SPECIES, NULL);
    u32 attackTypes = 0;
    BOOL physical = FALSE;
    BOOL special = FALSE;
    int count = 0;

    for (int slot = 0; slot < 4; slot++) {
        u16 move = GetMonData(mon, MON_DATA_MOVE1 + slot, NULL);
        if (move == MOVE_NONE) {
            continue;
        }
        struct BattleMove data;
        ReadWholeNarcMemberByIdPair(&data, ARC_MOVE_DATA, move);
        if (data.split == SPLIT_STATUS) {
            continue;
        }
        physical |= data.split == SPLIT_PHYSICAL;
        special |= data.split == SPLIT_SPECIAL;
        if (data.type < TRAINER_ITEM_TYPE_COUNT) {
            attackTypes |= 1u << data.type;
        }
    }

    for (u32 i = 0; i < NELEMS(sTrainerItemUnlocks); i++) {
        const struct TrainerItemUnlock *entry = &sTrainerItemUnlocks[i];
        if (badgeCount < entry->badges) {
            continue;
        }
        if ((entry->requirement == TRAINER_ITEM_PHYSICAL && !physical)
            || (entry->requirement == TRAINER_ITEM_SPECIAL && !special)
            || (entry->requirement == TRAINER_ITEM_ANY_ATTACK && !physical && !special)) {
            continue;
        }
        pool[count++] = entry->item;
    }

    for (u32 i = 0; i < NELEMS(sTrainerSpeciesItems); i++) {
        if (sTrainerSpeciesItems[i].species == species) {
            pool[count++] = sTrainerSpeciesItems[i].item;
        }
    }

    if (badgeCount >= 2) {
        u16 effectiveness[TRAINER_ITEM_TYPE_COUNT];
        GetTrainerTypeWeaknesses(mon, effectiveness);
        for (int type = 0; type < TRAINER_ITEM_TYPE_COUNT; type++) {
            if (attackTypes & (1u << type)) {
                pool[count++] = sTrainerTypeItems[type].booster;
            }
            // Chilan covers neutral Normal hits as well.
            if (effectiveness[type] > 100 || (type == TYPE_NORMAL && effectiveness[type] == 100)) {
                pool[count++] = sTrainerTypeItems[type].berry;
            }
        }
    }

    u16 item = pool[gf_rand() % count];
    SetMonData(mon, MON_DATA_HELD_ITEM, &item);
}
