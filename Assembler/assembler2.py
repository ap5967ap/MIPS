import re # regular expression library in python
import pandas as pd
from instructions import *
from symbolTable import *
import sys 
from source2basic import *
inFile = sys.argv[1]
outFile = sys.argv[2]
memFile = sys.argv[3]
with open(inFile,'r') as i:
    lines = i.readlines()


code=pd.DataFrame(columns=['address','machine_code','basic code']) # panda data frame to store the final machine code
data_memory_mips=pd.DataFrame(columns=['address','data']) # dataframe for the data memory segment
data_memory=[]
text=0 # flag to see if we are in the .text section of the file 

# tells if a line contains a label definition 
def labelDef(line):
    if ":" in line:
        return True
    return False

pc = 0x00400000

data = 0x10010000
def first_pass(lines:list[str]): # first pass
    global code
    global pc
    global data
    global data_memory
    line = 0
    temp=0
    for line_str in lines:
        some_number = 1
        betterLine = line_str.strip()
        if betterLine == '' or betterLine[0]=='\n' or betterLine[0]=='#': # dealing with whitespaces and commments 
            continue 
        if "#" in betterLine: 
            betterLine = betterLine.split('#')[0]
        if betterLine.startswith('.data'): # entering the .data segment 
            global text
            line = 0
            text = 0
            
        elif text == 0: # entering the content inside the data segment 
            if ":" in betterLine:
                label=betterLine.split(':')[0]
                string=betterLine.split(':')[1].strip()
                if string.startswith(".asciiz"): # if .asciiz is used, then we store the prefix sum by adding the size of the string(for ori instruction)
                    string = string[7:].strip()
                    data_elements[label]= [str(temp),(len(string)-1)] # updating the data label table 
                    cc=0
                    for i in string :
                        if i == '\\' and string[cc+1] == 'n': # dealing with \n in the string 
                            cc+=1
                            data_memory.append(r'\n')
                        data_memory.append(i)
                        cc+=1
                    data_memory.append('\0') # there is a null character at the end of the string 
                    if r"\n" in string:
                        data_elements[label][1] -= 1
                    temp+=data_elements[label][1]
                elif string.startswith(".space"): # if we are using .space, then we use the size of the memory declared for our prefix sum
                    string=string[6:].strip()
                    data_elements[label]=[str(temp),int(string)]
                    for i in range(int(string)):
                        data_memory.append('\0')
                    temp+=int(string)
        if betterLine.startswith('.text'): # entering the .text segment 
            text = 1
            line = 0
        elif text == 1: # dealing in the inside of the .text segment 
            if ":" in betterLine: # if line is a label definition 
                label=betterLine.split(':')[0]
                betterLine = betterLine.split(':')[1] #if there is instruction after label
                if label in symbol_table: # duplicate label
                    raise Exception("Label already exists")
                symbol_table[label]=pc # storing the address of the label in the symbol for use in the second pass
                if not (betterLine): # no instructions after label
                    continue
            betterLine = betterLine.split() # list of components of instruction
            if betterLine[0] not in mips_instructions: # if the instruction doesn't exist 
                raise Exception("Invalid instruction at line {}".format(line+1),betterLine[0])
            operands=''.join(betterLine[1:]).split(',') # making a list of the operands of the instruction
            some_number = len(mips_instructions[betterLine[0]]) # how many instruction does the pseudo instruction breaks down into 
            if "beq" == betterLine[0] and operands[0].startswith("$") and operands[1].startswith("$"):...
            else:
                some_number += 1
            bc=sc2bc(betterLine[0],operands) # converting the source code to basic code 
            for i in bc: # putting the addresses and basic code in the panda dataframe 
                code=code._append({'address':str((pc)),'machine_code':"",'basic code':i},ignore_index=True)
                pc += 4 # incrementing the program counter 

def bin_string(n, bits): # converting a number string to a binary number string upto a given number of bits 
    n=int(n)
    bin_str = bin(n)[2:]  
    bin_str = bin_str.zfill(bits)
    return str(bin_str)


def bin_to_hex_str(binary_string): # converting a binary number string to a hexadecimal number string, useful for putting the machine code in proper MARS format 
    while len(binary_string) % 4 != 0:
        binary_string = '0' + binary_string
    hex_string = format(int(binary_string, 2), '08X')
    return '0x'+hex_string


def dec_to_signed_bin(number, num_bits=16): # converting a number string to a signed binary number string 
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

def secondPass(): # implementing the second pass of the two pass Assembler 
    global code
    for _, i in code.iterrows():
        bc_parts = i['basic code'].split() # seperating instruction and operands 
        if bc_parts[0] in Rtype: # if the instruction is an R-type instruction
            bc_operands = bc_parts[1].split(',') # seperating operands 
            if bc_parts[0] == "div": # if the instruction is div, we only need two operands 
                temp =bin_string(0,6) + bin_string(bc_operands[0][1:], 5) + bin_string(bc_operands[1][1:], 5) + bin_string(0, 5) + bin_string(0, 5) + bin_string(0x1a, 6)
                i['machine_code'] = bin_to_hex_str(temp)

            elif bc_parts[0] == "mfhi": # if the instruction is mfhi, we only need a single operand 
                temp =bin_string(0,6) + bin_string(0, 5) + bin_string(0, 5) + bin_string(bc_operands[0][1:], 5) + bin_string(0,5) + bin_string(16, 6)
                i['machine_code'] = bin_to_hex_str(temp)
            else: # other R-type instruction are gonnna have all three operands 
                temp = bin_string(0,6) + bin_string(bc_operands[1][1:], 5) + bin_string(bc_operands[2][1:], 5)+ bin_string(bc_operands[0][1:], 5) + bin_string(0, 5) + bin_string(int(Rtype[bc_parts[0]]), 6)
                i['machine_code'] = bin_to_hex_str(temp)
        
        elif bc_parts[0] in Itype: # if the instruction is an I-type instruction 
            bc_operands = bc_parts[1].split(',') # seperating operands 
            if '?' in bc_parts[1] and (bc_parts[0] == "beq" or bc_parts[0] == "bne"): # future symbol definitions in beq and bne instructions 
                    bc_operands[2] = str((int(i['address'])*-1 + symbol_table[bc_operands[2][1:]])//4-1) # finding the immediate value for the branch instructions 
                    temp2=bc_parts[0]+" "+','.join(bc_operands)
                    i['basic code']=temp2 # modifying the basic code to complete the future symbol definiton in it
                    temp = bin_string(Itype[bc_parts[0]], 6) + bin_string(bc_operands[0][1:],5) +bin_string(bc_operands[1][1:], 5) + dec_to_signed_bin(bc_operands[2])
                    i['machine_code'] = bin_to_hex_str(temp)
            elif bc_parts[0] != "lb" and bc_parts[0] != "sb" and bc_parts[0] != "lw" and bc_parts[0] != "sw" and bc_parts[0] != "lui" and bc_parts[0] != "beq" and bc_parts[0] != "bne": # instructions in these format cannot have future symbol definitions
                temp = bin_string(Itype[bc_parts[0]], 6) + bin_string(bc_operands[1][1:], 5) + bin_string(bc_operands[0][1:],5) + dec_to_signed_bin(bc_operands[2])
                i['machine_code'] = bin_to_hex_str(temp)
            elif bc_parts[0] == 'lui': # always gonna have the same machine code in the context used here 
                i['machine_code'] = "0x3C011001"
            
            else : # this contains instructions like lb which have a combination of second and third arguments in the format value(register)
                blah=bc_operands[1]
                result = blah.split("(")[0]
                blah=re.findall(r'\((.*?)\)', blah)[0]
                temp = bin_string(Itype[bc_parts[0]], 6) + bin_string(blah[1:], 5) + bin_string(bc_operands[0][1:], 5) + dec_to_signed_bin(result)
                i['machine_code'] = bin_to_hex_str(temp)
        elif bc_parts[0] == "syscall": # syscall always have the same machine code 
                i['machine_code'] = "0x0000000C"
        elif bc_parts[0] in Jtype: # if the instruction is a J-type instruction, gonna have only 1 operand
            bc_operands = bc_parts[1]
            bc_operands = symbol_table[bc_operands[1:]] # taking out the label address from the symbol table
            i['basic code'] = bc_parts[0] + " " + str(bc_operands)
            number = str(bc_operands)
            number=dec_to_signed_bin(number,32)
            number = number[4:]
            number = number[:-2]
            temp=bin_string(Jtype[bc_parts[0]], 6) + number
            i['machine_code'] = bin_to_hex_str(temp)
                



first_pass(lines)
secondPass()

for idx, i in code.iterrows():
    i['address'] = str(hex(int(i['address'])))
csv=code.to_csv(outFile, index=False,sep='\t')

# implementing data memory, just taking data from here and there, pretty intuitive if the reader got the code of the machine code file 
data_mem=[]
for i in range(len(data_memory)):
    if data_memory[i] == '"' or data_memory[i] == '\\' or ( data_memory[i] == 'n' and data_memory[i-1] == '\\n'):
        continue
    data_mem.append(data_memory[i])
    
data_memory = []
for i in range(len(data_mem)):
    if i and data_mem[i] == 'n' and data_mem[i-1] == '\\n':
        continue
    data_memory.append(data_mem[i])

if len(data_memory)%32:
    left=32-len(data_memory)%32

for i in range(left):
    data_memory.append('\0')
    
    
temp_list=[]

for i in range(0,len(data_memory),4):
    x=data_memory[i]
    y=data_memory[i+1]
    z=data_memory[i+2]
    w=data_memory[i+3]
    if x =='\\n':
        x='\n'
    if y =='\\n':
        y='\n'
    if z =='\\n':
        z='\n'
    if w =='\\n':
        w='\n'
    x=bin_string(ord(x),8)
    y=bin_string(ord(y),8)
    z=bin_string(ord(z),8)
    w=bin_string(ord(w),8)
    res=w+z+y+x #?writing in liitle endian format
    temp_list.append(bin_to_hex_str(res))
    
for i in range(0,len(temp_list),8):
    
    a=temp_list[i]
    b=temp_list[i+1]
    c=temp_list[i+2]
    d=temp_list[i+3]
    e=temp_list[i+4]
    f=temp_list[i+5]
    g=temp_list[i+6]
    h=temp_list[i+7]
    temp22=a+" "+b+" "+c+" "+d+" "+e+" "+f+" "+g+" "+h
    data_memory_mips=data_memory_mips._append({'address':str(hex(data)),'data':temp22},ignore_index=True)
    data+=32
    
data_file=data_memory_mips.to_csv(memFile, index=False,sep='\t')
