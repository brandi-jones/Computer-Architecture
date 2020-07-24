"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
ADD = 0b10100000
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JEQ = 0b01010101
JNE = 0b01010110
JMP = 0b01010100

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.ram = [0] * 256
        self.pc = 0
        self.running = True
        self.flags = 0b00000000

    def load(self, file_name):
        """Load a program into memory."""

        # address = 0

        # # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        try:
            address = 0
            with open(file_name) as file:
                for line in file:
                    split_line = line.split('#')[0]
                    command = split_line.strip()
                    if command == '':
                        continue
                    instruction = int(command, 2)
                    self.ram_write(address, instruction)
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} file not found")
            sys.exit()



    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":

            #if equal
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flags = 0b00000001
            #if reg_a less than b
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flags = 0b00000100
            #if reg_a greater than b
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flags = 0b00000010
            
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, MAR): #MAR - memory address register
        return self.ram[MAR] 

    def ram_write(self, MAR, MDR): #MDR- memory data register
        self.ram[MAR] = MDR

    #this instruction sets a specified register to a specified value
    def ldi(self, regNum, value):
        self.reg[regNum] = value

    def prn(self, regNum):
        print(self.reg[regNum])

    def hlt(self):
        self.running = False

    def run(self):
        """Run the CPU."""
        

        while self.running:
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            instructionRegister = self.ram[self.pc]

            if instructionRegister == LDI:
                self.ldi(operand_a, operand_b)
                self.pc += 3

                #print('Writing ', operand_b, 'to register num', operand_a)

            elif instructionRegister == PRN:
                self.prn(operand_a)
                self.pc += 2

            elif instructionRegister == HLT:
                self.hlt()
                self.pc += 1

            elif instructionRegister == MUL:
                self.alu("MUL", operand_a, operand_b)
                self.pc += 3

            elif instructionRegister == ADD:
                self.alu("ADD", operand_a, operand_b)
                self.pc += 3

            elif instructionRegister == POP:

                #get the stack pointer
                sp = self.reg[7]

                #get register num to put value in
                regNum = self.ram[self.pc + 1]

                #use stack pointer to get the value
                value = self.ram[sp]

                #put the value into the given register
                self.reg[regNum] = value

                #increement our stack pointer
                self.reg[7] += 1

                #incremenet program counter
                self.pc += 2

                #print(f"Popping {self.reg[regNum]} off the stack and into register at: {regNum}")
               
               

            elif instructionRegister == PUSH:
                #decrement stack pointer
                self.reg[7] -= 1

                #get register num
                regNum = self.ram[self.pc + 1]

                #get value from the given register
                value = self.reg[regNum]

                #put the value at the stack pointer address
                sp = self.reg[7]
                self.ram[sp] = value

                #increment program counter
                self.pc += 2
                
                #print(f"Pushing {self.reg[regNum]} onto the stack at: {sp}")

            elif instructionRegister == CALL:
                #get register number
                regNum = self.ram[self.pc + 1]
                
                #get the address to jump to, from the register
                address = self.reg[regNum]

                #push command after CALL onto the stack
                returnAddress = self.pc + 2

                self.reg[7] -= 1 #decrement stack pointer
                sp = self.reg[7]
                self.ram[sp] = returnAddress #put return address onto the stack

                #then look at the register, and jump to that address
                self.pc = address

            elif instructionRegister == RET:
                #pop the return address off the stack
                sp = self.reg[7]
                returnAddress = self.ram[sp]
                self.reg[7] += 1

                #go to the return address, and set the pc to return address
                self.pc = returnAddress 

            elif instructionRegister == JMP:
                #get register num
                regNum = self.ram[self.pc + 1]

                #get the address to jump to
                address = self.reg[regNum]

                #set program counter to the address
                self.pc = address

            elif instructionRegister == CMP:
                self.alu("CMP", operand_a, operand_b)
                self.pc += 3
            
            elif instructionRegister == JEQ:
                if self.flags == 0b00000001:
                     #get register num
                    regNum = self.ram[self.pc + 1]

                    #get the address to jump to
                    address = self.reg[regNum]

                    #set program counter to the address
                    self.pc = address
                else:
                    self.pc += 2
            elif instructionRegister == JNE:
                if not self.flags == 0b00000001:
                    #get register num
                    regNum = self.ram[self.pc + 1]

                    #get the address to jump to
                    address = self.reg[regNum]

                    #set program counter to the address
                    self.pc = address
                else:
                    self.pc += 2
            else:
                self.pc += 1
        print("-----------")
        print(self.ram)
           