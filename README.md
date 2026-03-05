# PyVM-16
A zero-dependency 16-bit Virtual Machine and custom Assembler written in pure Python. Features memory-mapped I/O, a custom ISA, and label resolution

# PyVM-16: 16-bit Virtual Machine & Assembler

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-0-success.svg)]()

**PyVM-16** is a custom 16-bit virtual machine and assembler written entirely using the Python standard library. This project demonstrates a deep understanding of CPU architecture, the Fetch-Decode-Execute cycle, stack operations, and bitwise manipulation. 

[Image of Fetch-Decode-Execute cycle]


## Key Features
* **Custom Assembler:** Supports instruction parsing, register and memory operations, and automatic label resolution for jumps.
* **Custom ISA (Instruction Set Architecture):** 19 basic instructions covering arithmetic, logic, stack operations (`PUSH`, `POP`), and control flow (`CALL`, `RET`, `JMP`, `JZ`).
* **Memory-Mapped I/O:** Simulates hardware interrupts and sensors via reserved memory addresses.
* **Zero Dependencies:** The entire engine runs in a single file without requiring any external libraries.

## Architecture (Hardware Design)

* **Memory:** 64 KB (implemented via `bytearray(65536)`).
* **Registers:**
  * 4 general-purpose registers: `R0`, `R1`, `R2`, `R3`.
  * `PC` (Program Counter) — pointer to the current instruction.
  * `SP` (Stack Pointer) — stack pointer (initialized to `0xFFFE`).
* **I/O (Input/Output):**
  * Read from `0xFF00`: Returns a random value from 1 to 10 (simulating an external hardware sensor).
  * Write to `0xFF01`: Outputs a signed 16-bit value to standard output (console).

## Practical Example: Math Without `MUL`

Since the processor is heavily simplified, it **lacks** a hardware multiplication instruction. To demonstrate the system's capabilities, a program was written in the custom assembly language that reads 4 values from the "sensor" (address `0xFF00`) and calculates the determinant of a 2x2 matrix:

$$D = a_{11}a_{22} - a_{12}a_{21}$$

Multiplication is implemented in software using a loop, addition, and bitwise shifts (`SHR`, `AND`).

### Code Snippet (Multiplication Algorithm)
```assembly
mul_func:
    LOAD R0, 0x0100     ; Load the first number
    LOAD R1, 0x0102     ; Load the second number
    MOV R2, 0           ; R2 - result will be stored here
mul_loop:
    JZ R1, mul_end      ; If multiplier is 0, exit
    MOV R3, 1
    AND R3, R1          ; Check the least significant bit
    JZ R3, mul_skip
    ADD R2, R0          ; Add to the result
mul_skip:
    ADD R0, R0          ; R0 = R0 * 2
    SHR R1, 1           ; R1 = R1 / 2
    JMP mul_loop
mul_end:
    STORE 0x0104, R2    ; Store the result
    RET
