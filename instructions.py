
mips_instructions = {
    "li":["addiu"],
    "la":["lui","ori"],
    "syscall":["syscall"],
    "move":["addu"],
    "beq":["beq"], #if first or second argument in beq is immediate, then use addi first with $1
    "j":["j"],
    "jal":["jal"],
    "lb":["lb"],
    "lw":["lw"],
    "lbu":["lbu"],
    "lhu":["lhu"],
    "lh":["lh"],
    "sb":["sb"],
    "sw":["sw"],
    "sh":["sh"],
    "add":["add"],
    "addu":["addu"],
    "addi":["addi"],
    "addiu":["addiu"],
    "and":["and"],
    "andi":["andi"],
    "or":["or"],
    "ori":["ori"],
    "xor":["xor"],
    "xori":["xori"],
    "nor":["nor"],
    "slt":["slt"],
    "sltu":["sltu"],
    "slti":["slti"],
    "sltiu":["sltiu"],
    "sll":["sll"],
    "srl":["srl"],
    "sra":["sra"],
    "sllv":["sllv"],
    "bgt":["addi","slt","bne"],
    "blt":["slti","bne"],
    "div":["div"],
    "mfhi":["mfhi"],
}
RType=set
opcode={
    
}
# def mips_instructions()