SHELL = /bin/bash -o pipefail
SRC_DIR ?= .
BUILD_DIR ?= build
OBJDUMP ?= objdump

# uncomment the following to keep obj files around
# .PRECIOUS: $(BUILD_DIR)/%.o

all: linux mac windows

$(BUILD_DIR)/%.o: handler.c
	mkdir -p $(BUILD_DIR)
	clang -c -O3 -Werror -target $* -o $@ ${SRC_DIR}/handler.c

$(BUILD_DIR)/%.hex: $(BUILD_DIR)/%.o
	$(OBJDUMP) -d $^ | tail -n +8 | awk -F'\t' '{print $$2}' | tr -d ' \n' >$@

linux: $(BUILD_DIR)/x86_64-unknown-linux.hex
mac: $(BUILD_DIR)/x86_64-apple-darwin.hex
windows: $(BUILD_DIR)/x86_64-pc-windows.hex

linux-aarch64:
	mkdir -p $(BUILD_DIR)
	clang -c -O3 -Werror -target aarch64-unknown-linux -o $(BUILD_DIR)/aarch64-unknown-linux.o ./handler_ptr.c -mcmodel=tiny
	ld $(BUILD_DIR)/aarch64-unknown-linux.o -o $(BUILD_DIR)/a.out
	objdump -s -j .text $(BUILD_DIR)/a.out | awk '/\.text/{flag=1; next} flag{print}' | awk -F' ' '{print $$2 $$3 $$4 $$5}' | tr -d ' \n' > $(BUILD_DIR)/aarch64-unknown-linux.hex

clean:
	rm -f $(BUILD_DIR)/*.o
	rm -f $(BUILD_DIR)/*.hex
	test ! -d $(BUILD_DIR) || rmdir $(BUILD_DIR)
