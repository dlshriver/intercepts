# Intercept Handler C Code

This directory provides the source and tools that are used to generate the
instructions for intercept handlers. `handler.c` provides the c source code 
which we compile for each supported system target.

Generating the code requires [clang](https://clang.llvm.org/) and a version 
of [binutils](https://www.gnu.org/software/binutils/) built to support all 
targets. The provided script `./install_build_tools.sh` will install the
required depedencies.

If clang and binutils are installed, running `make` will generate the handler
code for each target system, and save it as a hex encoded string in 
`[target].hex` in the `build` directory, where `[target]` is the build target.

Currently, the resulting hex string is then manually written to the 
corresponding location in the intercepts package.

## Build Targets

We currently only support the x86_64 (amd64) and armv8 (aarch64) architecture.
We support both linux and windows (with mac support hopefully coming soon).

- linux: x86_64 and armv8
- windows: x86_64 (and untested on armv8)

