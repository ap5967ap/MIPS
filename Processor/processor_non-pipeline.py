import sys
import pandas as pd
from opcodes import *
binFile=sys.argv[1]
dataMem=sys.argv[2]
instruct_memory={}
data_mem={}
register_file={'$0':0, '$1':0, '$2':0, '$3':0, '$4':0, '$5':0, '$6':0, '$7':0, '$8':0, '$9':0, '$10':0, '$11':0, '$12':0, '$13':0, '$14':0, '$15':0, '$16':0, '$17':0, '$18':0, '$19':0, '$20':0, '$21':0, '$22':0, '$23':0, '$24':0, '$25':0, '$26':0, '$27':0, '$28':0, '$29':0, '$30':0, '$31':0,'hi':0, 'lo':0}
control_signals={
    "RegDst":0b0,
    "Branch":0b0,
    "MemRead":0b0,  
    "MemtoReg":0b0,
    "ALUOp":0b00,
    "MemWrite":0b0,
    "ALUSrc":0b0, 
    "RegWrite":0b0,
    "Jump":0b0,
}

with open(binFile, 'r') as f:
    lines = f.readlines()
    lines = [line.strip() for line in lines]
    address=0x400000
    for i in lines:
        instruct_memory[hex(address)]=i
        address+=4
        
with open(dataMem, 'r') as f:
    address=0x10010000
    lines = f.readlines()
    lines = [line.strip() for line in lines]
    for line in lines:
        data_mem[hex(address)]=line
        address+=4
        
def instruction_fetch(pc): #returns the instruction at the pc
    return instruct_memory[pc]

def sign_extend(imm):
    if imm[0]=='1':
        return '1111111111111111'+imm
    else:
        return '0000000000000000'+imm
    
def instruction_decode(instruction):
    opcode=instruction[0:6]
    rs=instruction[6:11]
    rt=instruction[11:16]
    rd=instruction[16:21]
    shamt=instruction[21:26]
    funct=instruction[26:32]
    imm=instruction[16:32]
    imm=sign_extend(imm)
    address=instruction[6:32]
    
    
    
def control_path(opcode,funct):
    rtype=False
    itype=False
    jtype=False
    instr=None
    opcode=int(opcode,2)
    if opcode == 0:
        rtype=True
        instr=Rtype(funct)
    elif opcode in Itype:
        itype=True
        instr=Itype(opcode)
    elif opcode in Jtype:
        jtype=True
        instr=Jtype(opcode)
        
    if rtype:
        control_signals['RegDst']=0b1
        control_signals['Branch']=0b0
        control_signals['MemRead']=0b0
        control_signals['MemtoReg']=0b0
        control_signals['ALUOp']=0b0010 #?changed ALUOp to 4 bits as we need to incorporate the I type instructions too
        control_signals['MemWrite']=0b0
        control_signals['ALUSrc']=0b0
        control_signals['RegWrite']=0b1
        control_signals['Jump']=0b0
        
    elif itype:
        
        if opcode in [0x04,0x05]: #beq or bne
            control_signals['RegDst']=0b0
            control_signals['Branch']=0b1
            control_signals['MemRead']=0b0
            control_signals['MemtoReg']=0b0
            control_signals['ALUOp']=0b0001
            if opcode==0x05: #bne
                control_signals['ALUOp']=0b1110
            control_signals['MemWrite']=0b0
            control_signals['ALUSrc']=0b0
            control_signals['RegWrite']=0b0
            control_signals['Jump']=0b0
            
        elif opcode in [0x20,0x23,0x21]: #lb or lw
            control_signals['RegDst']=0b0
            control_signals['Branch']=0b0
            control_signals['MemRead']=0b11
            if opcode==0x20: #lb
                control_signals['MemRead']=0b01
            elif opcode==0x21: #lh
                control_signals['MemRead']=0b10
            control_signals['MemtoReg']=0b1
            control_signals['ALUOp']=0b0000
            control_signals['MemWrite']=0b0
            control_signals['ALUSrc']=0b1
            control_signals['RegWrite']=0b1
            control_signals['Jump']=0b0
            
        elif opcode in [0x28,0x2B,0x29]: #sb or sw
            control_signals['RegDst']=0b0
            control_signals['Branch']=0b0
            control_signals['MemRead']=0b0
            control_signals['MemtoReg']=0b0
            control_signals['ALUOp']=0b0000
            control_signals['MemWrite']=0b11
            if opcode==0x28: #sb
                control_signals['MemWrite']=0b01
            elif opcode==0x29: #sh
                control_signals['MemWrite']=0b10
            control_signals['ALUSrc']=0b1
            control_signals['RegWrite']=0b0
            control_signals['Jump']=0b0
        
        else:
            control_signals['RegDst']=0b0
            control_signals['Branch']=0b0
            control_signals['MemRead']=0b0
            control_signals['MemtoReg']=0b0
            control_signals['MemWrite']=0b0
            control_signals['ALUSrc']=0b1
            control_signals['RegWrite']=0b1
            control_signals['Jump']=0b0
            itype_alu={
                0x09:0b0100, #addiu
                0x08:0b0101, #addi
                0x0C:0b0110, #andi
                0x0F:0b0111, #lui
                0x0D:0b1000, #ori
                0x0A:0b1001, #slti
                0x0B:0b1010, #sltiu
                0x0E:0b1011  #xori
            }
        
    elif jtype:
        control_signals['RegDst']=0b0
        control_signals['Branch']=0b0
        control_signals['MemRead']=0b0
        control_signals['MemtoReg']=0b0
        control_signals['ALUOp']=0b00
        control_signals['MemWrite']=0b0
        control_signals['ALUSrc']=0b0
        control_signals['RegWrite']=0b0
        control_signals['Jump']=0b1    

