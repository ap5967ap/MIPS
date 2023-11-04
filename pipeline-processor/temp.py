from processor_non_pipeline import *

# def mips_processor():
#     pc = 0x400000
#     clock = 0
#     while pc <= max(instruct_memory.keys()):
#         for i in control_signals.keys():
#             control_signals[i] = 0
#         # instruction fetch
#         instruction = instruction_fetch((pc))
#         clock += 1
#         if instruction != "00000000000000000000000000001100":  # syscalls
#         #     processor.append(
#         #         "IF  "
#         #         + str(hex(pc))
#         #         + " -- "
#         #         + str(instruction)
#         #         + f"\nCLOCK : {clock}\n"
#         #     )
#         pc += 4

#         # ? syscalls 5 stages would need to be incorporated in pipelining
#         if instruction == "00000000000000000000000000001100":  # syscalls
#             clock -= 1
#             v0 = register_file["$2"]
#             if v0 == 1:
#                 print(register_file["$4"], end=" ")
#             elif v0 == 4:
#                 start_address = register_file["$4"]
#                 print(print_string(start_address), end=" ")

#             if v0 == 5:
#                 register_file["$2"] = int(input())

#             if v0 == 8:
#                 address = register_file["$4"]
#                 max_char = register_file["$5"]
#                 string = input()
#                 string = string + "\0"
#                 string_input(string, address)
#             continue

#         # instruction decode
#         opcode, rs, rt, rd, shamt, funct, imm, address, rd1, rd2 = instruction_decode(
#             instruction
#         )
#         ALUcontrol = alucontrol(control_signals["ALUOp"], funct)
#         if control_signals["RegDst"] == 0b0:
#             rd = rt
#         else:
#             rd = rd
#         clock += 1
#         processor.append(f"ID  ")
#         processor.append("opcode:  " + hex(opcode))
#         processor.append("rs:  " + str(rs))
#         processor.append("rt:  " + str(rt))
#         processor.append("rd:  " + str(rd))
#         processor.append("shamt:  " + str(shamt))
#         processor.append("funct:  " + hex(funct))
#         processor.append("imm:  " + str(imm))
#         processor.append("address:  " + str(address))
#         processor.append("rd1:  " + str(rd1))
#         processor.append("rd2:  " + str(rd2) + f"\nCLOCK : {clock}\n")

#         # print(hex(pc-4),opcode,rs,rt,rd,shamt,funct,"**",imm,address,rd1,rd2)

#         # instruction execute
#         ALUResult, zero = instr_execute(ALUcontrol, imm, rd1, rd2)
#         clock += 1
#         processor.append(
#             "EX ALU = "
#             + str(ALUResult)
#             + "  zero = "
#             + str(zero)
#             + f"\nCLOCK : {clock}\n"
#         )
#         # memory access
#         if control_signals["Jump"] == 1:
#             pc = address_after_jump(pc, address)
#             processor.append("JUMPING TO " + hex(pc))
#             # continue
#         elif control_signals["Branch"] == 1 and zero:
#             pc = pc + imm * 4
#             # continue
#         writeData = rd2
#         readData = memory(ALUResult, writeData)
#         clock += 1
#         processor.append("MEM readData = " + str(readData))
#         processor.append("ADDRESS = " + str(ALUResult))
#         if control_signals["MemWrite"] != 0:
#             processor.append(
#                 "VALUE  " + str(data_mem[(ALUResult // 4) * 4]) + f"  \nCLOCK : {clock}"
#             )
#         else:
#             processor.append(f"NOT WRITTEN IN MEMORY,  \nCLOCK : {clock}")
#         # write back
#         writeback(ALUResult, readData, rd)
#         processor.append("\nWB  ")
#         processor.append("rd = " + str(rd))
#         processor.append("ALUresult = " + str(ALUResult))
#         processor.append("readData = " + str(readData))
#         processor.append("value = " + str(register_file["$" + str(rd)]))
#         clock += 1
#         processor.append(f"CLOCK : {clock}\n")
#         processor.append(
#             "________________________________________________________________________________________________________________\n"
#         )


# mips_processor()
instruction_memory = {4: 0b0001, 8: 0b0010, 12: 0b0100, 16: 0b1000}
def make_instruction_stages(instruction_stages):
    pc = 4
    while pc <= max(instruction_memory.keys()):
        instruction_stages[bin(instruction_memory[pc])[2:]] = [0, 0, 0, 0, 0]
        pc += 4

instruction_stages = {}
make_instruction_stages(instruction_stages)

print(instruction_stages)