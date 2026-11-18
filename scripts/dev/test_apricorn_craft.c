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
    u8 box[128], oldBox[128];
    u16 total, units;
    u32 money;
    const unsigned amounts[] = {1, 9, 10, 11, 20, 21, 99};
    for (unsigned j=0;j<7;j++) {
        clear(&bag,sizeof(bag)); clear(box,sizeof(box));
        box[0]=amounts[j]; box[7]=42; money=10000; before=bag;
        for (unsigned k=0;k<128;k++) oldBox[k]=box[k];
        assert(ApricornCraft_Exchange(&bag,box,&money,FALSE,&total,&units)==0);
        assert(total==amounts[j] && units==(amounts[j]+9)/10);
        assert(money==10000 && equal(box,oldBox,128) && equal(&bag,&before,sizeof(bag)));
        assert(ApricornCraft_Exchange(&bag,box,&money,TRUE,&total,&units)==0);
        assert(money==10000-units*100 && box[0]==0 && box[7]==42);
        assert(balls(&bag,ITEM_LEVEL_BALL)==amounts[j]);
    }
    // Mixed stores and colours, exact funds; preserve pending Kurt order bytes.
    clear(&bag,sizeof(bag)); clear(box,sizeof(box));
    bag.items[0]=(ITEM_SLOT){ITEM_RED_APRICORN,7}; box[0]=3; box[1]=1; box[7]=12;
    money=200;
    assert(ApricornCraft_Exchange(&bag,box,&money,TRUE,&total,&units)==0);
    assert(total==11 && units==2 && money==0 && !box[0] && !box[1] && box[7]==12);
    assert(!Bag_GetQuantity(&bag,ITEM_RED_APRICORN,0));
    assert(balls(&bag,ITEM_LEVEL_BALL)==10 && balls(&bag,ITEM_MOON_BALL)==1);
    assert(ApricornCraft_Exchange(&bag,box,&money,TRUE,&total,&units)==APRICORN_CRAFT_EMPTY);
    // Insufficient funds and a failure after one colour was already simulated.
    clear(&bag,sizeof(bag)); clear(box,sizeof(box)); box[0]=10; box[1]=1; money=199;
    before=bag;
    assert(ApricornCraft_Exchange(&bag,box,&money,TRUE,&total,&units)==APRICORN_CRAFT_NO_MONEY);
    assert(money==199 && box[0]==10 && box[1]==1 && equal(&bag,&before,sizeof(bag)));
    bag.balls[0]=(ITEM_SLOT){ITEM_MOON_BALL,999}; before=bag; money=1000;
    assert(ApricornCraft_Exchange(&bag,box,&money,TRUE,&total,&units)==APRICORN_CRAFT_NO_SPACE);
    assert(money==1000 && box[0]==10 && box[1]==1 && equal(&bag,&before,sizeof(bag)));
    // Full pocket and a combined Box+Bag count above the stack limit.
    clear(&bag,sizeof(bag)); clear(box,sizeof(box)); box[0]=1;
    for(unsigned i=0;i<NUM_BAG_BALLS;i++) bag.balls[i]=(ITEM_SLOT){600+i,1};
    before=bag;
    assert(ApricornCraft_Exchange(&bag,box,&money,TRUE,&total,&units)==APRICORN_CRAFT_NO_SPACE);
    assert(equal(&bag,&before,sizeof(bag)) && box[0]==1 && money==1000);
    clear(&bag,sizeof(bag)); box[0]=99; bag.items[0]=(ITEM_SLOT){ITEM_RED_APRICORN,999}; money=100000;
    assert(ApricornCraft_Exchange(&bag,box,&money,TRUE,&total,&units)==APRICORN_CRAFT_NO_SPACE);
    assert(box[0]==99 && money==100000);
    // Large quote and fee exceed 16-bit dollars; all seven mappings are tested.
    clear(&bag,sizeof(bag));
    const unsigned expected[]={493,498,494,497,496,492,495};
    for(unsigned i=0;i<7;i++) { bag.items[i]=(ITEM_SLOT){ITEM_RED_APRICORN+i,900}; box[i]=99; }
    money=100000;
    assert(ApricornCraft_Exchange(&bag,box,&money,TRUE,&total,&units)==0);
    assert(total==6993 && units==700 && money==30000);
    for(unsigned i=0;i<7;i++) assert(balls(&bag,expected[i])==999 && box[i]==0);
    assert(!allocated);
    puts("OK: fee rounding, all colour mappings, both stores, quote/cancel safety, exact/insufficient funds, full pocket, stack overflow, atomic rollback, Kurt order preservation, large totals");
    return 0;
}
