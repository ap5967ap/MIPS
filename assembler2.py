import re
import pandas as pd
from instructions import *
from symbolTable import *
import sys 
from source2basic import *
inFile = sys.argv[1]
outFile = sys.argv[2]

with open(inFile,'r') as i:
    lines = i.readlines()

code=pd.DataFrame(columns=['address','machine_code','basic code'])

text=0 # flag to see if we are in the .text section of the file 

# tells if a line contains a label definition 
def labelDef(line):
    if ":" in line:
        return True
    return False

pc = 0x00400000
# first pass
def first_pass(lines:list[str]):
    global code
    global pc
    line = 0
    temp=0
    for line_str in lines:
        some_number = 1
        betterLine = line_str.strip()
        # print(betterLine)
        if betterLine == '' or betterLine[0]=='\n' or betterLine[0]=='#':
            continue 
        if "#" in betterLine:
            betterLine = betterLine.split('#')[0]
        if betterLine.startswith('.data'):
            global text
            line = 0
            text = 0
            
        elif text == 0:
            if ":" in betterLine:
                label=betterLine.split(':')[0]
                string=betterLine.split(':')[1].strip()
                if string.startswith(".asciiz"):
                    string = string[7:].strip()
                    data_elements[label]= [str(temp),(len(string)-1)]
                    if r"\n" in string:
                        data_elements[label][1] -= 1
                    temp+=data_elements[label][1]
                elif string.startswith(".space"):
                    string=string[6:].strip()
                    data_elements[label]=[str(temp),int(string)]
                    temp+=int(string)
        if betterLine.startswith('.text'):
            text = 1
            line = 0
        elif text == 1:
            if ":" in betterLine:
                label=betterLine.split(':')[0]
                # print(label)
                betterLine = betterLine.split(':')[1] #if there is instruction after label
                if label in symbol_table:
                    raise Exception("Label already exists")
                symbol_table[label]=pc #!pc
                if not (betterLine):
                    continue
            betterLine = betterLine.split() # list of components of instruction
            # print(betterLine)
            if betterLine[0] not in mips_instructions:
                raise Exception("Invalid instruction at line {}".format(line+1),betterLine[0])
            operands=''.join(betterLine[1:]).split(',')
            some_number = len(mips_instructions[betterLine[0]])
            if "beq" == betterLine[0] and operands[0].startswith("$") and operands[1].startswith("$"):...
            else:
                some_number += 1
            # for i in mips_instructions[betterLine[0]]:
            bc=sc2bc(betterLine[0],operands)
            for i in bc:
                code=code._append({'address':str((pc)),'machine_code':"",'basic code':i},ignore_index=True)
                pc += 4

def bin_string(n, bits):
    n=int(n)
    bin_str = bin(n)[2:]  
    bin_str = bin_str.zfill(bits)
    return str(bin_str)

# def (binary_string):
#     hex_string = hex(int(binary_string, 2))[2:].upper()
#     return str('0x'+hex_string)

def bin_to_hex_str(binary_string):
    while len(binary_string) % 4 != 0:
        binary_string = '0' + binary_string
    hex_string = format(int(binary_string, 2), '08X')
    return '0x'+hex_string


def dec_to_signed_bin(number, num_bits=16):
    if number.startswith('0x'):
        number = int(number, 16)
    else:
        number = int(number)
    if number >= 0:
            binary_str = format(number, f'0{num_bits}b')
    else:
            abs_value = abs(number)
            binary_str = format(abs_value, f'0{num_bits}b')
            inverted_str = ''.join('1' if bit == '0' else '0' for bit in binary_str)
            inverted_value = int(inverted_str, 2) + 1
            binary_str = format(inverted_value, f'0{num_bits}b')
    return binary_str

def secondPass():
    global code
    for _, i in code.iterrows():
        bc_parts = i['basic code'].split() # seperating instruction and operands 
        if bc_parts[0] in Rtype:
            bc_operands = bc_parts[1].split(',') # seperating operands 
            if bc_parts[0] == "div": 
                temp =bin_string(0,6) + bin_string(bc_operands[0][1:], 5) + bin_string(bc_operands[1][1:], 5) + bin_string(0, 5) + bin_string(0, 5) + bin_string(0x1a, 6)
                i['machine_code'] = bin_to_hex_str(temp)

            elif bc_parts[0] == "mfhi": 
                temp =bin_string(0,6) + bin_string(0, 5) + bin_string(0, 5) + bin_string(bc_operands[0][1:], 5) + bin_string(0,5) + bin_string(16, 6)
                i['machine_code'] = bin_to_hex_str(temp)
            else:
                temp = bin_string(0,6) + bin_string(bc_operands[1][1:], 5) + bin_string(bc_operands[2][1:], 5)+ bin_string(bc_operands[0][1:], 5) + bin_string(0, 5) + bin_string(int(Rtype[bc_parts[0]]), 6)
                i['machine_code'] = bin_to_hex_str(temp)
        
        elif bc_parts[0] in Itype:
            bc_operands = bc_parts[1].split(',') # seperating operands 
            if '?' in bc_parts[1] and (bc_parts[0] == "beq" or bc_parts[0] == "bne"):
                    # print(i['address'])
                    bc_operands[2] = str((int(i['address'])*-1 + symbol_table[bc_operands[2][1:]])//4-1)
                    temp2=bc_parts[0]+" "+','.join(bc_operands)
                    i['basic code']=temp2
                    temp = bin_string(Itype[bc_parts[0]], 6) + bin_string(bc_operands[0][1:],5) +bin_string(bc_operands[1][1:], 5) + dec_to_signed_bin(bc_operands[2])
                    i['machine_code'] = bin_to_hex_str(temp)
            elif bc_parts[0] != "lb" and bc_parts[0] != "sb" and bc_parts[0] != "lw" and bc_parts[0] != "sw" and bc_parts[0] != "lui" and bc_parts[0] != "beq" and bc_parts[0] != "bne":
                temp = bin_string(Itype[bc_parts[0]], 6) + bin_string(bc_operands[1][1:], 5) + bin_string(bc_operands[0][1:],5) + dec_to_signed_bin(bc_operands[2])
                i['machine_code'] = bin_to_hex_str(temp)
            elif bc_parts[0] == 'lui':
                i['machine_code'] = "0x3C011001"
            
            else :
                blah=bc_operands[1]
                result = blah.split("(")[0]
                blah=re.findall(r'\((.*?)\)', blah)[0]
                temp = bin_string(Itype[bc_parts[0]], 6) + bin_string(blah[1:], 5) + bin_string(bc_operands[0][1:], 5) + dec_to_signed_bin(result)
                i['machine_code'] = bin_to_hex_str(temp)
        elif bc_parts[0] == "syscall":
                i['machine_code'] = "0x0000000C"
        elif bc_parts[0] in Jtype:
            bc_operands = bc_parts[1]
            bc_operands = symbol_table[bc_operands[1:]]
            i['basic code'] = bc_parts[0] + " " + str(bc_operands)
            number = str(bc_operands)
            number=dec_to_signed_bin(number,32)
            number = number[4:]
            number = number[:-2]
            temp=bin_string(Jtype[bc_parts[0]], 6) + number
            i['machine_code'] = bin_to_hex_str(temp)
            # i['machine_code'] = bin_to_hex_str(temp)
                



first_pass(lines)
secondPass()
# print(symbol_table['loopend2'])
# print()

csv=code.to_csv(outFile, index=False,sep='\t')