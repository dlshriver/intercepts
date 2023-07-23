SHELL = /bin/bash -o pipefail
SRC_DIR ?= .
BUILD_DIR ?= build

ifeq ($(origin CC),default)
CC = clang
endif

# uncomment the following to keep obj files around
# .PRECIOUS: $(BUILD_DIR)/%.o

all: x86_64 aarch64

$(BUILD_DIR)/%.o: ${SRC_DIR}/handler.c
	mkdir -p $(BUILD_DIR)
	$(CC) -target $* -static -nostdlib -O3 -Werror -o $@ ${SRC_DIR}/handler.c

$(BUILD_DIR)/%.hex: $(BUILD_DIR)/%.o
	objcopy -j .text -O binary $^ >(od -An -v -t x1 | tr -d ' \n' > $@)

.PHONY: x86_64
x86_64: $(BUILD_DIR)/x86_64-linux.hex $(BUILD_DIR)/x86_64-pc-windows-gnu.hex 

.PHONY: aarch64
aarch64: $(BUILD_DIR)/aarch64-linux.hex

.PHONY: clean
clean:
	rm -f $(BUILD_DIR)/*.o
	rm -f $(BUILD_DIR)/*.out
	rm -f $(BUILD_DIR)/*.hex
	test ! -d $(BUILD_DIR) || rmdir $(BUILD_DIR)
