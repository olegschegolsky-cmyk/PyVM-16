import random
import re

class Assembler:
    def __init__(self):
        self.opcodes = {
            'HALT': 0, 'MOV_REG': 1, 'MOV_IMM': 2, 'LOAD_ABS': 3,
            'STORE_ABS': 4, 'LOAD_IND': 5, 'STORE_IND': 6, 'PUSH': 7,
            'POP': 8, 'ADD': 9, 'SUB': 10, 'AND': 11, 'OR': 12,
            'XOR': 13, 'SHR': 14, 'JMP': 15, 'JZ': 16, 'CALL': 17, 'RET': 18
        }

    def assemble(self, source):
        lines = [re.sub(r';.*', '', l).strip() for l in source.split('\n')]
        lines = [l for l in lines if l]
        labels = {}
        addr = 0
        parsed = []

        for line in lines:
            if line.endswith(':'):
                labels[line[:-1]] = addr
                continue
            parts = [p for p in re.split(r'[,\s]+', line) if p]
            op = parts[0]
            args = parts[1:]
            parsed.append((addr, op, args))
            addr += 2
            if op == 'MOV' and not args[1].startswith('R'):
                addr += 2
            elif op == 'LOAD' and not args[1].startswith('['):
                addr += 2
            elif op == 'STORE' and not args[0].startswith('['):
                addr += 2
            elif op in ('SHR', 'JMP', 'JZ', 'CALL'):
                addr += 2

        bytecode = []
        for p_addr, op, args in parsed:
            inst = 0
            imm = None
            if op == 'HALT':
                inst = self.opcodes['HALT'] << 10
            elif op == 'MOV':
                r1 = int(args[0][1])
                if args[1].startswith('R'):
                    r2 = int(args[1][1])
                    inst = (self.opcodes['MOV_REG'] << 10) | (r1 << 8) | (r2 << 6)
                else:
                    inst = (self.opcodes['MOV_IMM'] << 10) | (r1 << 8)
                    imm = args[1]
            elif op == 'LOAD':
                r1 = int(args[0][1])
                if args[1].startswith('['):
                    r2 = int(args[1][2])
                    inst = (self.opcodes['LOAD_IND'] << 10) | (r1 << 8) | (r2 << 6)
                else:
                    inst = (self.opcodes['LOAD_ABS'] << 10) | (r1 << 8)
                    imm = args[1]
            elif op == 'STORE':
                if args[0].startswith('['):
                    r1 = int(args[0][2])
                    r2 = int(args[1][1])
                    inst = (self.opcodes['STORE_IND'] << 10) | (r1 << 8) | (r2 << 6)
                else:
                    imm = args[0]
                    r2 = int(args[1][1])
                    inst = (self.opcodes['STORE_ABS'] << 10) | (r2 << 6)
            elif op in ('PUSH', 'POP'):
                r1 = int(args[0][1])
                inst = (self.opcodes[op] << 10) | (r1 << 8)
            elif op in ('ADD', 'SUB', 'AND', 'OR', 'XOR'):
                r1 = int(args[0][1])
                r2 = int(args[1][1])
                inst = (self.opcodes[op] << 10) | (r1 << 8) | (r2 << 6)
            elif op == 'SHR':
                r1 = int(args[0][1])
                inst = (self.opcodes['SHR'] << 10) | (r1 << 8)
                imm = args[1]
            elif op in ('JMP', 'CALL'):
                inst = (self.opcodes[op] << 10)
                imm = args[0]
            elif op == 'JZ':
                r1 = int(args[0][1])
                inst = (self.opcodes['JZ'] << 10) | (r1 << 8)
                imm = args[1]
            elif op == 'RET':
                inst = self.opcodes['RET'] << 10

            bytecode.append(inst)
            if imm is not None:
                if imm in labels:
                    bytecode.append(labels[imm])
                else:
                    bytecode.append(int(imm, 0) & 0xFFFF)
        return bytecode

class VirtualMachine:
    def __init__(self):
        self.memory = bytearray(65536)
        self.regs = [0, 0, 0, 0]
        self.pc = 0
        self.sp = 0xFFFE
        self.running = False

    def load(self, bytecode):
        for i, b in enumerate(bytecode):
            self.memory[i * 2] = (b >> 8) & 0xFF
            self.memory[i * 2 + 1] = b & 0xFF

    def mem_read(self, addr):
        if addr == 0xFF00:
            return random.randint(1, 10)
        return (self.memory[addr] << 8) | self.memory[addr + 1]

    def mem_write(self, addr, val):
        val &= 0xFFFF
        if addr == 0xFF01:
            print(val if val < 32768 else val - 65536)
        else:
            self.memory[addr] = (val >> 8) & 0xFF
            self.memory[addr + 1] = val & 0xFF

    def fetch(self):
        inst = self.mem_read(self.pc)
        self.pc = (self.pc + 2) & 0xFFFF
        return inst

    def execute(self, inst):
        op = inst >> 10
        r1 = (inst >> 8) & 3
        r2 = (inst >> 6) & 3

        if op == 0:
            self.running = False
        elif op == 1:
            self.regs[r1] = self.regs[r2]
        elif op == 2:
            self.regs[r1] = self.fetch()
        elif op == 3:
            addr = self.fetch()
            self.regs[r1] = self.mem_read(addr)
        elif op == 4:
            addr = self.fetch()
            self.mem_write(addr, self.regs[r2])
        elif op == 5:
            self.regs[r1] = self.mem_read(self.regs[r2])
        elif op == 6:
            self.mem_write(self.regs[r1], self.regs[r2])
        elif op == 7:
            self.mem_write(self.sp, self.regs[r1])
            self.sp = (self.sp - 2) & 0xFFFF
        elif op == 8:
            self.sp = (self.sp + 2) & 0xFFFF
            self.regs[r1] = self.mem_read(self.sp)
        elif op == 9:
            self.regs[r1] = (self.regs[r1] + self.regs[r2]) & 0xFFFF
        elif op == 10:
            self.regs[r1] = (self.regs[r1] - self.regs[r2]) & 0xFFFF
        elif op == 11:
            self.regs[r1] &= self.regs[r2]
        elif op == 12:
            self.regs[r1] |= self.regs[r2]
        elif op == 13:
            self.regs[r1] ^= self.regs[r2]
        elif op == 14:
            shift = self.fetch()
            self.regs[r1] >>= shift
        elif op == 15:
            self.pc = self.fetch()
        elif op == 16:
            addr = self.fetch()
            if self.regs[r1] == 0:
                self.pc = addr
        elif op == 17:
            addr = self.fetch()
            self.mem_write(self.sp, self.pc)
            self.sp = (self.sp - 2) & 0xFFFF
            self.pc = addr
        elif op == 18:
            self.sp = (self.sp + 2) & 0xFFFF
            self.pc = self.mem_read(self.sp)

    def run(self):
        self.running = True
        while self.running:
            inst = self.fetch()
            self.execute(inst)

code = """
LOAD R0, 0xFF00
STORE 0x0200, R0
LOAD R0, 0xFF00
STORE 0x0202, R0
LOAD R0, 0xFF00
STORE 0x0204, R0
LOAD R0, 0xFF00
STORE 0x0206, R0

LOAD R0, 0x0200
STORE 0x0100, R0
LOAD R0, 0x0206
STORE 0x0102, R0
CALL mul_func
LOAD R0, 0x0104
STORE 0x0208, R0

LOAD R0, 0x0202
STORE 0x0100, R0
LOAD R0, 0x0204
STORE 0x0102, R0
CALL mul_func
LOAD R0, 0x0104
STORE 0x020A, R0

LOAD R0, 0x0208
LOAD R1, 0x020A
SUB R0, R1
STORE 0xFF01, R0
HALT

mul_func:
LOAD R0, 0x0100
LOAD R1, 0x0102
MOV R2, 0
mul_loop:
JZ R1, mul_end
MOV R3, 1
AND R3, R1
JZ R3, mul_skip
ADD R2, R0
mul_skip:
ADD R0, R0
SHR R1, 1
JMP mul_loop
mul_end:
STORE 0x0104, R2
RET
"""

random.seed(42)
asm = Assembler()
bytecode = asm.assemble(code)
vm = VirtualMachine()
vm.load(bytecode)
vm.run()