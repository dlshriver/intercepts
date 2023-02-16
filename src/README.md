`handler.c` provides the c source code which we compile into the intercept handler

On linux:

```
gcc -Wall -shared -fomit-frame-pointer -fPIC -o handler.o handler.c
objdump --disassemble=handler -Mintel handler.o
```

On windows:

```
cl /Oy handler.c
dumpbin /DISASM handler.obj
```
