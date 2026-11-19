/* Exercise the production transaction with deterministic inventory adapters. */
#include "apricorn_craft.h"
#include "constants/item.h"
#include <assert.h>
extern int puts(const char *);

static BAG_DATA scratch;
static int allocated;
void *sys_AllocMemory(u32 heap, u32 bytes) {
    assert(!allocated && bytes == sizeof(scratch));
    allocated = 1;
    return &scratch;
}
void sys_FreeMemoryEz(void *ptr) { assert(ptr == &scratch); allocated = 0; }
u16 Bag_GetQuantity(BAG_DATA *bag, u16 item, int heap) {
    for (unsigned i = 0; i < NUM_BAG_ITEMS; i++)
        if (bag->items[i].id == item) return bag->items[i].quantity;
    return 0;
}
BOOL Bag_TakeItem(BAG_DATA *bag, u16 item, u16 qty, int heap) {
    for (unsigned i = 0; i < NUM_BAG_ITEMS; i++) {
        if (bag->items[i].id != item) continue;
        if (bag->items[i].quantity < qty) return FALSE;
        bag->items[i].quantity -= qty;
        if (!bag->items[i].quantity) bag->items[i].id = 0;
        return TRUE;
    }
    return FALSE;
}
BOOL Bag_AddItem(BAG_DATA *bag, u16 item, u16 qty, int heap) {
    int empty = -1;
    for (unsigned i = 0; i < NUM_BAG_BALLS; i++) {
        if (bag->balls[i].id == item) {
            if (bag->balls[i].quantity + qty > 999) return FALSE;
            bag->balls[i].quantity += qty;
            return TRUE;
        }
        if (!bag->balls[i].id) empty = i;
    }
    if (empty < 0 || qty > 999) return FALSE;
    bag->balls[empty] = (ITEM_SLOT){item, qty};
    return TRUE;
}
static void clear(void *ptr, unsigned size) { for (unsigned i=0; i<size; i++) ((u8 *)ptr)[i]=0; }
static int equal(const void *a, const void *b, unsigned n) {
    for (unsigned i=0; i<n; i++) if (((const u8 *)a)[i] != ((const u8 *)b)[i]) return 0;
    return 1;
}
static unsigned balls(BAG_DATA *bag, unsigned item) {
    for (unsigned i=0;i<NUM_BAG_BALLS;i++) if (bag->balls[i].id==item) return bag->balls[i].quantity;
    return 0;
}

int main(void) {
    static BAG_DATA bag, before;
    u16 total, units;
    u32 money;
    const unsigned amounts[] = {1, 9, 10, 11, 20, 21, 99};
    for (unsigned j = 0; j < sizeof(amounts) / sizeof(amounts[0]); j++) {
        clear(&bag, sizeof(bag));
        bag.items[0] = (ITEM_SLOT){ITEM_RED_APRICORN, amounts[j]};
        money = 10000;
        before = bag;
        assert(ApricornCraft_Exchange(&bag, &money, FALSE, &total, &units) == APRICORN_CRAFT_OK);
        assert(total == amounts[j] && units == (amounts[j] + 9) / 10);
        assert(money == 10000 && equal(&bag, &before, sizeof(bag)));
        assert(ApricornCraft_Exchange(&bag, &money, TRUE, &total, &units) == APRICORN_CRAFT_OK);
        assert(money == 10000 - units * 100 && !Bag_GetQuantity(&bag, ITEM_RED_APRICORN, 0));
        assert(balls(&bag, ITEM_FAST_BALL) == amounts[j]);
    }

    // Mixed colours and exact funds.
    clear(&bag, sizeof(bag));
    bag.items[0] = (ITEM_SLOT){ITEM_RED_APRICORN, 10};
    bag.items[1] = (ITEM_SLOT){ITEM_YELLOW_APRICORN, 1};
    money = 200;
    assert(ApricornCraft_Exchange(&bag, &money, TRUE, &total, &units) == APRICORN_CRAFT_OK);
    assert(total == 11 && units == 2 && money == 0);
    assert(!Bag_GetQuantity(&bag, ITEM_RED_APRICORN, 0));
    assert(!Bag_GetQuantity(&bag, ITEM_YELLOW_APRICORN, 0));
    assert(balls(&bag, ITEM_FAST_BALL) == 10 && balls(&bag, ITEM_LEVEL_BALL) == 1);
    assert(ApricornCraft_Exchange(&bag, &money, TRUE, &total, &units) == APRICORN_CRAFT_EMPTY);

    // Insufficient funds and a stack overflow after one colour was already simulated.
    clear(&bag, sizeof(bag));
    bag.items[0] = (ITEM_SLOT){ITEM_RED_APRICORN, 10};
    bag.items[1] = (ITEM_SLOT){ITEM_YELLOW_APRICORN, 1};
    money = 199;
    before = bag;
    assert(ApricornCraft_Exchange(&bag, &money, TRUE, &total, &units) == APRICORN_CRAFT_NO_MONEY);
    assert(money == 199 && equal(&bag, &before, sizeof(bag)));
    bag.balls[0] = (ITEM_SLOT){ITEM_LEVEL_BALL, 999};
    before = bag;
    money = 1000;
    assert(ApricornCraft_Exchange(&bag, &money, TRUE, &total, &units) == APRICORN_CRAFT_NO_SPACE);
    assert(money == 1000 && equal(&bag, &before, sizeof(bag)));

    // Full ball pocket.
    for (unsigned i = 0; i < NUM_BAG_BALLS; i++)
        bag.balls[i] = (ITEM_SLOT){600 + i, 1};
    before = bag;
    assert(ApricornCraft_Exchange(&bag, &money, TRUE, &total, &units) == APRICORN_CRAFT_NO_SPACE);
    assert(money == 1000 && equal(&bag, &before, sizeof(bag)));

    // All eight mappings and a fee greater than 65535 dollars.
    clear(&bag, sizeof(bag));
    const u16 inputs[] = {
        ITEM_RED_APRICORN, ITEM_YELLOW_APRICORN, ITEM_BLUE_APRICORN, ITEM_GREEN_APRICORN,
        ITEM_PINK_APRICORN, ITEM_BLACK_APRICORN, ITEM_PURPLE_APRICORN, ITEM_GREY_APRICORN,
    };
    const u16 expected[] = {
        ITEM_FAST_BALL, ITEM_LEVEL_BALL, ITEM_QUICK_BALL, ITEM_FRIEND_BALL,
        ITEM_LOVE_BALL, ITEM_DUSK_BALL, ITEM_DREAM_BALL, ITEM_HEAVY_BALL,
    };
    bag.items[8] = (ITEM_SLOT){ITEM_WHITE_APRICORN, 100};
    for (unsigned i = 0; i < NELEMS(inputs); i++)
        bag.items[i] = (ITEM_SLOT){inputs[i], 999};
    money = 100000;
    assert(ApricornCraft_Exchange(&bag, &money, TRUE, &total, &units) == APRICORN_CRAFT_OK);
    assert(total == 7992 && units == 800 && money == 20000);
    for (unsigned i = 0; i < NELEMS(inputs); i++) {
        assert(!Bag_GetQuantity(&bag, inputs[i], 0));
        assert(balls(&bag, expected[i]) == 999);
    }
    assert(Bag_GetQuantity(&bag, ITEM_WHITE_APRICORN, 0) == 100);
    assert(ApricornCraft_Exchange(&bag, &money, TRUE, &total, &units) == APRICORN_CRAFT_EMPTY);
    assert(total == 0 && units == 0 && money == 20000);
    assert(!allocated);
    puts("OK: Bag-only crafting, fee rounding, all colour mappings, quote safety, exact and insufficient funds, full pocket, stack overflow, and atomic rollback");
    return 0;
}
