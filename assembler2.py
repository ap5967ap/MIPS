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

text=0

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


def secondPass(lines:list[str]):
    
    



first_pass(lines)
# secondPass(lines)
# print(symbol_table['loopend2'])
print(symbol_table)
code.to_csv('a.csv', index=False, sep='\t', encoding='utf-8')
