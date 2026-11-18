# macros for overlay definition that automatically grab everything that we need from the folders provided
CODE_BUILD_DIRS += $(BUILD)/
THUMB_HELP := $(BUILD)/thumb_help.o
LINKED_OUTPUTS = build/linked.o

INDIVIDUAL := individual
OVERLAYS := $(filter-out $(INDIVIDUAL) encounter $(shell cd $(C_SUBDIR); ls *.*),$(shell cd $(C_SUBDIR); ls))

INDIVIDUAL_OVERLAYS = $(basename $(notdir $(wildcard $(C_SUBDIR)/$(INDIVIDUAL)/*.c)))

# Encounter generation has typed resident imports rather than linker-script
# address aliases, so direct Thumb calls and shared data retain their ELF types.
ENCOUNTER_SRCS := $(wildcard $(C_SUBDIR)/encounter/*.c)
ENCOUNTER_OBJS := $(patsubst $(C_SUBDIR)/%.c,$(BUILD)/%.o,$(ENCOUNTER_SRCS))
ALL_C_SRCS += $(ENCOUNTER_SRCS)
CODE_BUILD_DIRS += $(BUILD)/encounter/
LINKED_OUTPUTS += $(BUILD)/encounter_linked.o
OVERLAY_OUTPUTS += $(BUILD)/output_encounter.bin
$(ENCOUNTER_OBJS): CFLAGS += -DOVERLAY129 -DENCOUNTER_OVERLAY -include include/encounter_overlay_aliases.h
$(ENCOUNTER_OBJS): overlays.mk

$(BUILD)/encounter_imports.s: $(LINK) $(ENCOUNTER_OBJS) $(THUMB_HELP) scripts/build/gen_overlay_imports.py
	$(PYTHON) scripts/build/gen_overlay_imports.py --resident $(LINK) --output $@ $(ENCOUNTER_OBJS) $(THUMB_HELP)

$(BUILD)/encounter_imports.o: $(BUILD)/encounter_imports.s
	$(CC) -mthumb -mcpu=arm946e-s -c $< -o $@

$(BUILD)/encounter_linked.o: $(ENCOUNTER_OBJS) $(BUILD)/encounter_imports.o $(THUMB_HELP) $(C_SUBDIR)/encounter/linker.ld
	$(LD) -T $(C_SUBDIR)/encounter/linker.ld -o $@ $(ENCOUNTER_OBJS) $(THUMB_HELP) $(BUILD)/encounter_imports.o

$(BUILD)/output_encounter.bin: $(BUILD)/encounter_linked.o
	$(OBJCOPY) -O binary $< $@

# everything is expanded because it was not working for me otherwise
# this is aggressively defined but works.  in order to add a new overlay, you just have to add to the top now.
define OVERLAY_DEFINE

$1_LINK = $(BUILD)/$1_linked.o
$1_OUTPUT = $(BUILD)/output_$1.bin
OVERLAY_OUTPUTS += $(BUILD)/output_$1.bin
LINKED_OUTPUTS += $(BUILD)/$1_linked.o
CODE_BUILD_DIRS += $(BUILD)/$1/

ALL_C_SRCS += $(wildcard $(C_SUBDIR)/$1/*.c)
ALL_ASM_SRCS += $(wildcard $(ASM_SUBDIR)/$1/*.s)


$(BUILD)/$1_linked.o:$(patsubst $(C_SUBDIR)/%.c,$(BUILD)/%.o,$(wildcard $(C_SUBDIR)/$1/*.c)) $(patsubst $(ASM_SUBDIR)/%.s,$(BUILD)/%.o,$(wildcard $(ASM_SUBDIR)/$1/*.s)) $(BUILD)/rom_gen.ld $(C_SUBDIR)/$1/linker.ld
	$(LD) $(BUILD)/rom_gen.ld -T $(C_SUBDIR)/$1/linker.ld -o $(BUILD)/$1_linked.o $(patsubst $(C_SUBDIR)/%.c,$(BUILD)/%.o,$(wildcard $(C_SUBDIR)/$1/*.c)) $(patsubst $(ASM_SUBDIR)/%.s,$(BUILD)/%.o,$(wildcard $(ASM_SUBDIR)/$1/*.s)) $(THUMB_HELP)

$(BUILD)/output_$1.bin:$(BUILD)/$1_linked.o
	$(OBJCOPY) -O binary $(BUILD)/$1_linked.o $(BUILD)/output_$1.bin

endef

ifneq (1,$(NOSCAN))
$(foreach overlay, $(OVERLAYS), $(eval $(call OVERLAY_DEFINE,$(overlay))))
endif


CODE_BUILD_DIRS += $(BUILD)/$(INDIVIDUAL)/

$(BUILD)/rom_gen_battle.ld:$(battle_LINK) $(battle_OUTPUT) $(BUILD)/rom_gen.ld
	cp $(BUILD)/rom_gen.ld $(BUILD)/rom_gen_battle.ld
	$(PYTHON) scripts/build/generate_ld.py $(BUILD)/rom_gen_battle.ld $(battle_LINK)


define INDIVIDUAL_OVERLAY_DEFINE

LDFLAGS_$1 = $(BUILD)/rom_gen_battle.ld -T $(C_SUBDIR)/$(INDIVIDUAL)/$1.ld

$1_LINK = $(BUILD)/$1_linked.o
$1_OUTPUT = $(BUILD)/output_$1.bin
OVERLAY_OUTPUTS += $(BUILD)/output_$1.bin
LINKED_OUTPUTS += $(BUILD)/$1_linked.o

ALL_C_SRCS += $(C_SUBDIR)/$(INDIVIDUAL)/$1.c

$(BUILD)/$1_linked.o:$(patsubst $(C_SUBDIR)/%.c,$(BUILD)/%.o,$(C_SUBDIR)/$(INDIVIDUAL)/$1.c) $(THUMB_HELP) $(BUILD)/rom_gen_battle.ld
	$(LD) $(BUILD)/rom_gen_battle.ld -T $(C_SUBDIR)/$(INDIVIDUAL)/linker/$1.ld -o $(BUILD)/$1_linked.o $(patsubst $(C_SUBDIR)/%.c,$(BUILD)/%.o,$(C_SUBDIR)/$(INDIVIDUAL)/$1.c) $(THUMB_HELP)

$(BUILD)/output_$1.bin:$(BUILD)/$1_linked.o
	$(OBJCOPY) -O binary $(BUILD)/$1_linked.o $(BUILD)/output_$1.bin

endef

ifneq (1,$(NOSCAN))
$(foreach overlay, $(INDIVIDUAL_OVERLAYS), $(eval $(call INDIVIDUAL_OVERLAY_DEFINE,$(overlay))))
endif
