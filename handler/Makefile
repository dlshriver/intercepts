SHELL = /bin/bash -o pipefail
SRC_DIR ?= .
BUILD_DIR ?= build
OBJDUMP ?= objdump

.PRECIOUS: $(BUILD_DIR)/%.o

all: linux mac windows

$(BUILD_DIR)/%.o: handler.c
	mkdir -p $(BUILD_DIR)
	clang -c -O3 -Werror -target $* -o $@ ${SRC_DIR}/handler.c

$(BUILD_DIR)/%.hex: $(BUILD_DIR)/%.o
	$(OBJDUMP) -d $^ | tail -n +8 | awk -F'\t' '{print $$2}' | tr -d ' \n' >$@

linux: $(BUILD_DIR)/x86_64-unknown-linux.hex
mac: $(BUILD_DIR)/x86_64-apple-darwin.hex
windows: $(BUILD_DIR)/x86_64-pc-windows.hex

clean:
	rm -f $(BUILD_DIR)/*.o
	rm -f $(BUILD_DIR)/*.hex
	test ! -d $(BUILD_DIR) || rmdir $(BUILD_DIR)
