CC := gcc
CFLAGS := -std=c11 -O2 -Wall -Wextra -DECOLOGY_STANDALONE -I../../../include
TARGET := ../../../tools/ecologygen

SRCS := main.c \
	../../../src/ecology_generate.c \
	ecology_compat_data.c \
	ecology_strings_data.c

OBJS := $(SRCS:%.c=%.o)

.PHONY: all clean

all: $(TARGET)
	@:

$(TARGET): $(OBJS)
	$(CC) $(LDFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	$(RM) $(TARGET) ecologygen.exe $(OBJS)
