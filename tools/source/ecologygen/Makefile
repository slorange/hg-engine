CC := gcc
CFLAGS := -std=c11 -O2 -Wall -Wextra -DECOLOGY_STANDALONE -I../../../include
TARGET := ../../../tools/ecologygen

# Keep host .o files here — never compile into src/ (make.py treats stray src/*.o as overlays).
HOST_GEN_OBJ := host_ecology_generate.o

OBJS := main.o $(HOST_GEN_OBJ) ecology_compat_data.o ecology_strings_data.o

.PHONY: all clean

all: $(TARGET)
	@:

$(TARGET): $(OBJS)
	$(CC) $(LDFLAGS) -o $@ $^

$(HOST_GEN_OBJ): ../../../src/field/ecology_generate.c
	$(CC) $(CFLAGS) -c -o $@ $<

main.o: main.c
	$(CC) $(CFLAGS) -c -o $@ $<

ecology_compat_data.o: ecology_compat_data.c
	$(CC) $(CFLAGS) -c -o $@ $<

ecology_strings_data.o: ecology_strings_data.c
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	$(RM) $(TARGET) ecologygen.exe $(OBJS)
