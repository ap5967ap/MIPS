import re
import pandas as pd
from instructions import *
from symbolTable import *
import sys 

inFile = sys.argv[1]
outFile = sys.argv[2]

with open(inFile,'r') as i:
    lines = i.readlines()

code=pd.DataFrame(columns=['address','machine_code','basic code','source code'])
# first pass

pc = 0x00400000
text=0

# tells if a line contains a label definition 
def labelDef(line):
    if ":" in line:
        return True
    return False

def first_pass(lines:list[str]):
    line = 0
    for line_str in lines:
        betterLine = line_str.strip()
        if betterLine == '' or betterLine[0]=='\n' or betterLine[0]=='#':
            continue 
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
                    data_elements[label]= len(string)-1
                    if r"\n" in string:
                        data_elements[label] -= 1
                elif string.startswith(".space"):
                    string=string[6:].strip()
                    data_elements[label]=int(string)
        if betterLine.startswith('.text'):
            text = 1
            line = 0
        elif text == 1:
            if ":" in betterLine:
                label=betterLine.split(':')[0]
                if label in symbol_table:
                    raise Exception("Label already exists")
                symbol_table[label]=line+1
                # line-=1
        line += 1


def secondPass(lines:list[str]):
    in_text = False
    currLine = 0
    
    for line in lines:
        betterLine = line.strip()
        if betterLine == '' or betterLine[0]=='\n' or betterLine[0]=='#':
            continue 
        if "#" in betterLine:
            betterLine = betterLine.split('#')[0]
        
        if betterLine.startswith('.text'):
            in_text = 1
            currLine = 0
        elif in_text == 1:
            if(labelDef(betterLine)):
                betterLine = betterLine.split(":")[1]
                if not (betterLine):
                    continue
                
            betterLine = betterLine.split()
            if betterLine[0] not in mips_instructions:
                raise Exception("Invalid instruction at line {}".format(currLine+1),betterLine[0])

            instruction=mips_instructions[betterLine[0]]
            
            operands=''.join(betterLine[1:]).split(',') # removing the , in the operands
            # print(operands,end=" ") 
            # print(betterLine)
            if "loopend2" in operands:
                print(currLine)
                break
            for i in operands: # removing the initial spaces in case of spaces after ,
                i=i.strip() 
            # for i in instruction: 
            #     ...
        
        currLine += 1
        
            
            
               
        

    

                

first_pass(lines)
secondPass(lines)
print(symbol_table['loopend2'])
# print(data_elements)