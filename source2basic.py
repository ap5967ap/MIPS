from instructions import *
from symbolTable import *
import re

def sc2bc(inst, operands): # function to convert source code to basic code 
    bc = ['a'] # this initial declaration is useful for future ammendments and testing 

    # now we are gonna deal with almost all instructions used in rot13.asm individually and generate respective basic code, this is easily extendable in the future
    # in case anyone wishes to do so. This also has basic register error handling in two instructions for demo, can be extended to more precise and proper error handling 
    if(inst == "li"): 
        reg=operands[0]
        value= register.get(reg)
        if value is None:
            raise Exception("Invalid register name")
        bc = ["addiu " + value +  ",$0," + operands[-1]]
    elif(inst == "la"):
        reg = operands[0]
        value = register.get(reg)
        if value is None:
            raise Exception("Invalid register name")
        bc = ["lui $1,4097", "ori " + value + ",$1," + data_elements[operands[-1]][0]] # picking some values from the .data segment labels for basic code generation
        
    elif(inst == "move"):
        bc = ["addu " + register.get(operands[0]) + ",$0," + register.get(operands[1])]
    
    elif(inst == "syscall"):
        bc = ["syscall"]
    
    elif(inst == "beq"):
        if operands[0].startswith("$") and operands[1].startswith("$"):
            bc = ["beq " + register.get(operands[1]) + "," + register.get(operands[0]) + "," + "?"+ operands[2]]
        elif operands[0].startswith("$"):
            bc = ["addi $1,$0," + operands[1], "beq " + "$1," + register.get(operands[0]) + "," + "?"+ operands[2]]
            
    elif(inst == "j"):
        bc = ["j " +  "?"+ operands[0]]
    
    elif(inst == "jal"):
        bc = ["jal " +  "?"+ operands[0]]
    
    elif(inst == "lb"):
        blah = operands[1]
        result = blah.split("(")[0]
        blah=re.findall(r'\((.*?)\)', blah)[0] # using the regular expression library for dealing with instructions like lb, sb
        bc = ["lb " + register.get(operands[0]) + "," + result +'('+ register.get(blah) + ")"]        
        
    elif(inst == "sb"):
        blah = operands[1]
        result = blah.split("(")[0]
        blah=re.findall(r'\((.*?)\)', blah)[0]
        bc = ["sb " + register.get(operands[0]) + "," + result +'('+ register.get(blah) + ")"]  
    
    elif (inst == "addi"):
        bc = ["addi " + register.get(operands[0]) + "," + register.get(operands[1]) + "," +operands[2]]
        
    elif (inst == "bgt"):
        if operands[0].startswith("$") and operands[1].startswith("$"):
            bc=["slt $1," + register.get(operands[1]) + "," + register.get(operands[0]), "bne $1,$0," + "?"+operands[2]]
        elif operands[0].startswith("$"):
            bc=["addi $1,$0,"+operands[1],"slt $1,$1," + register.get(operands[0]), "bne $1,$0," + "?"+operands[2]]
    
    elif (inst == "blt"):
        bc=["slti $1," + register.get(operands[0]) + "," + operands[1], "bne $1,$0," + "?"+operands[2]]
    
    elif (inst == "div"):
        bc=["div " + register.get(operands[0]) + "," + register.get(operands[1])]
    
    elif (inst == "mfhi"):
        bc=["mfhi " + register.get(operands[0])]
    
    
    return bc
        
        
        
