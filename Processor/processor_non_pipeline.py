import sys
import pandas as pd
from opcodes import *
binFile=sys.argv[1]
dataMem=sys.argv[2]
processor_output=sys.argv[3]
memory11=sys.argv[4]
instruct_memory={}
data_mem={}
processor=[]
register_file={'$0':0, '$1':0, '$2':0, '$3':0, '$4':0, '$5':0, '$6':0, '$7':0, '$8':0, '$9':0, '$10':0, '$11':0, '$12':0, '$13':0, '$14':0, '$15':0, '$16':0, '$17':0, '$18':0, '$19':0, '$20':0, '$21':0, '$22':0, '$23':0, '$24':0, '$25':0, '$26':0, '$27':0, '$28':0, '$29':0, '$30':0, '$31':0,'hi':0, 'lo':0}
control_signals={
    "RegDst":0b0, # if the destination register is rd or rt#TODO
    "Branch":0b0, # if we are making a branch instruction or not 
    "MemRead":0b00,  # if we are reading from mem or not
    "MemtoReg":0b0, # Destination from mem or ALU
    "ALUOp":0b0000, 
    "MemWrite":0b00, # if we are writing into mem or not
    "ALUSrc":0b0, # whether the second operand of the ALU is register or immediate 
    "RegWrite":0b0, # if we are writing into register or not #TODO
    "Jump":0b0, # if the instruction uses jump or not 
}

with open(binFile, 'r') as ff:
    lines = ff.readlines()
    lines = [line.strip() for line in lines]
    address=0x400000
    for i in lines:
        instruct_memory[(address)]=i
        address+=4
        
with open(dataMem, 'r') as fff:
    address=0x10010000
    lines = fff.readlines()
    lines = [line.strip() for line in lines]
    for line in lines:
        data_mem[(address)]=line
        address+=4
        
def instruction_fetch(pc): #returns the instruction at the pc
    return instruct_memory[pc]

def sign_extend(imm,imm_len=32):
    if len(imm)==32:
        return imm
    else:
        return imm[0]*(imm_len-len(imm))+imm    



def int_(binary_str): 
    if binary_str[0] == '0':
        return int(binary_str, 2)
    elif binary_str[0] == '1':
        flipped_bits = ''.join('1' if bit == '0' else '0' for bit in binary_str[1:])
        return -(int(flipped_bits, 2) + 1)
def bin_(num):
    if num >= 0:
        binary = bin(num)[2:]  
        binary = binary.zfill(32)  
    else:
        
        binary = bin(num & 0xFFFFFFFF)[2:]
    
    return binary

def control_path(opcode):
    rtype=False
    itype=False
    jtype=False
    #converting to int from binary
    if opcode == 0:
        rtype=True
    elif opcode in Itype:
        itype=True
    elif opcode in Jtype:
        jtype=True
        
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
                0x08:0b0100, #addi
                0x0C:0b0110, #andi
                0x0F:0b0111, #lui
                0x0D:0b1000, #ori
                0x0A:0b1001, #slti
                0x0B:0b1001, #sltiu
                0x0E:0b1011  #xori
            }
            control_signals['ALUOp']=itype_alu[opcode]
        
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

 
def instruction_decode(instruction):
    opcode=instruction[0:6]
    opcode=int(opcode,2)
    rs=instruction[6:11]
    rs=int(rs,2)
    rt=instruction[11:16]
    rt=int(rt,2)
    rd=instruction[16:21]
    rd=int(rd,2)
    shamt=instruction[21:26]
    shamt=int_(shamt)
    funct=instruction[26:32] 
    funct=int(funct,2)
    imm=instruction[16:32]
    imm=sign_extend(imm,32)
    imm=int_(imm)
    address=instruction[6:32]
    address=int(address,2)    
    rd1=register_file['$'+str(rs)]
    rd2=register_file['$'+str(rt)] 
    control_path(opcode) 
    return [opcode,rs,rt,rd,shamt,funct,imm,address,rd1,rd2]
    

    

def alucontrol(AlUop, funct):
    if(AlUop in [0b0100,0b0000] or (funct in [0x20,0x21] and AlUop==2)): 
        return 0b0000 #?add
    elif funct in [0x1B,0x1A] and AlUop==2 :
        return 0b0001 #?div
    elif (funct in [0x24] and AlUop==2 ) or AlUop in [0b0110]:
        return 0b0010 #?and
    elif funct == 0x10 and AlUop==2:
        return 0b0011 #?mfhi
    elif funct == 0x12 and AlUop==2:
        return 0b0100 #?mflo
    elif funct in [0x18,0x19] and AlUop==2:
        return 0b0101 #?mult
    elif funct == 0x27 and AlUop==2:
        return 0b0110 #?nor
    elif (funct == 0x25 and AlUop==2) or AlUop in [0b1000]:
        return 0b0111 #?or
    elif (funct == 0x26 and AlUop==2) or AlUop in [0b1011]:
        return 0b1000 #?xor
    elif (funct in [0x2A,0x2B] and AlUop==2) or AlUop in [0b1001]:
        return 0b1001 #?slt
    elif (funct in [0x22,0x23] and AlUop==2) or AlUop in [0b0001]:
        return 0b1010 #?sub
    elif AlUop == 0b1110:
        return 0b1011 #?bne
    elif AlUop in [0b0111]:     
        return 0b1100 #?lui
    
    
def ALU(control,op1,op2): #[output,zero_flag] #control is ALUcontrol 
    if control==0b0000:
        return [op1+op2,0]
    elif control==0b0001:
        register_file['hi']=op1%op2
        register_file['lo']=op1//op2
        return [0,0]
    elif control==0b0010:
        return [op1&op2,0]
    elif control==0b0011:
        return [register_file['hi'],0]
    elif control==0b0100:
        return [register_file['lo'],0]
    elif control==0b0101:
        res=op1*op2
        x=format(res,'064b')
        register_file['hi']=int_(x[0:32])
        register_file['lo']=int_(x[32:64])
        return [0,0]
    elif control==0b0110:
        return [~(op1|op2),0]
    elif control==0b0111:
        return [op1|op2,0]
    elif control==0b1000:
        return [op1^op2,0]
    elif control==0b1001:
        if op1<op2:
            return [1,0]
        else:
            return [0,0]
    elif control==0b1010:
        return [op1-op2,op1-op2==0]
    elif control==0b1011:
        return [0,op1-op2!=0]
    elif control==0b1100:
        return [op2<<16,0]
    
    
def instr_execute(control,imm,rd1,rd2):
    if(control_signals['ALUSrc']==0b1):
        op2=imm
    else:
        op2=rd2
    ALUResult,zero=ALU(control,rd1,op2)
    return [ALUResult,zero]



def address_after_jump(pc,imm):
    return int(imm)*4
    # pcc=pcc[0:4]+imm

def memory(ALUResult,writeData):
    if control_signals['MemRead']==0b00 and control_signals['MemWrite']==0b00:
        return 0
    if control_signals['MemRead']==0b01:
        start=(ALUResult//4)*4
        try:
            data_mem[start]
        except KeyError:
            data_mem[start]="0"*32
        offset=ALUResult%4
        if offset==0:
            return int_(sign_extend(data_mem[start][24:32],32))
        elif offset==1:
            return int_(sign_extend(data_mem[start][16:24],32))
        elif offset==2:
            return int_(sign_extend(data_mem[start][8:16],32))
        elif offset==3:
            return int_(sign_extend(data_mem[start][0:8],32))
    elif control_signals['MemRead']==0b10:
        try:
            data_mem[start]
        except KeyError:
            data_mem[start]="0"*32
        start=(ALUResult//4)*4
        offset=ALUResult%4
        if offset==1 or offset==3:
            raise Exception("fetch address not aligned on halfword boundary")
        elif offset ==0:
            return int_(sign_extend(data_mem[start][16:32],32))
        elif offset ==2:
            return int_(sign_extend(data_mem[start][0:16],32))
    elif control_signals['MemRead']==0b11:
        try:
            data_mem[start]
        except KeyError:
            data_mem[start]="0"*32
        if ALUResult%4!=0:
            raise Exception("fetch address not aligned on word boundary")
        else:
            return int_(data_mem[ALUResult])
        
    data_bin=bin_(writeData)
    if control_signals['MemWrite']==0b01:
        start=(ALUResult//4)*4
        offset=(ALUResult%4)
        if offset==0:
            data_mem[start]=data_mem[start][0:24]+data_bin[24:32]
        elif offset==1:
            data_mem[start]=data_mem[start][0:16]+data_bin[24:32]+data_mem[start][24:32]
        elif offset==2:
            data_mem[start]=data_mem[start][0:8]+data_bin[24:32]+data_mem[start][16:32]
        elif offset==3:
            data_mem[start]=data_bin[24:32]+data_mem[start][8:32]
    elif control_signals['MemWrite']==0b10:
        start=(ALUResult//4)*4
        offset=ALUResult%4
        if offset==1 or offset==3:
            raise Exception("fetch address not aligned on halfword boundary")
        elif offset ==0:
            data_mem[start]=data_mem[start][0:16]+data_bin[16:32]
        elif offset ==2:
            data_mem[start]=data_bin[0:16]+data_mem[start][16:32]
    elif control_signals['MemWrite']==0b11:
        if ALUResult%4!=0:
            raise Exception("fetch address not aligned on word boundary")
        else:
            data_mem[ALUResult]=data_bin[0:32]
    return 0
    
    
    
def writeback(ALUResult,ReadData,rd): # writeback cycle 
    Result=0
    if control_signals['RegWrite']==0:
        return
    if control_signals['MemtoReg']==0:
        Result=ALUResult
    else:
        Result=ReadData
    if rd==0:
        return
    register_file['$'+str(rd)]=(Result)
    return
    
    
def print_string(start_address): # print the string given the starting address 
    address = start_address
    address=(address//4)*4
    offset=start_address%4
    output=""
    if offset ==1:
        a=int(data_mem[address][16:24],2)
        b=int(data_mem[address][8:16],2)
        c=int(data_mem[address][0:8],2)
        if a==0:
            return output
        elif b==0:
            return chr(a)+output
        elif c==0:
            return chr(a)+chr(b)+output
        else:
            output += chr(a)+chr(b)+chr(c)
        address+=4
            
    elif offset==2:
        b=int(data_mem[address][8:16],2)
        c=int(data_mem[address][0:8],2)
        if b==0:
            return output
        elif c==0:
            return chr(b)+output
        else:
            output += chr(b)+chr(c)
        address+=4
            
    elif offset==3:
        c=int(data_mem[address][0:8],2)
        if c==0:
            return output
        else:
            output += chr(c)
        address+=4
    while True:
        dat=''
        try:
            dat=data_mem[address]
        except KeyError:
            data_mem[address]="0"*32
        dat=data_mem[address]
        a=int(dat[24:32],2)
        b=int(dat[16:24],2)
        c=int(dat[8:16],2)
        d=int(dat[0:8],2)
        if a==0:
            return output
        elif b==0:
            return output+chr(a)
        elif c==0:
            return output+chr(a)+chr(b)
        elif d==0:
            return output+chr(a)+chr(b)+chr(c)
        else:
            output += chr(a)+chr(b)+chr(c)+chr(d)
        address+=4
    return output


def string_input(string,address2): # storing the string given the string and the starting address
    for i in string:
        val=format(ord(i),'08b')
        address=address2
        if address%4==0:
            data_mem[address]=data_mem[address][0:24]+str(val)

        elif address%4==1:
            address=(address//4)*4
            data_mem[address]=data_mem[address][0:16]+str(val)+data_mem[address][24:32]
        elif address%4==2:
            address=(address//4)*4
            data_mem[address]=data_mem[address][0:8]+str(val)+data_mem[address][16:32]
        elif address%4==3:
            address=(address//4)*4
            data_mem[address]=str(val)+data_mem[address][8:32]
        
        address2+=1
 
def binary_to_string(bits): # convert binary to ascii value
	return ''.join([chr(int(i, 2)) for i in bits])   
    
def mips_processor():
    pc=0x400000
    clock=0
    while pc<=max(instruct_memory.keys()):
        for i in control_signals.keys():
            control_signals[i]=0
        #instruction fetch
        instruction=instruction_fetch((pc))
        clock+=1
        if instruction != "00000000000000000000000000001100": # syscalls 
            processor.append("IF  "+str(hex(pc))+" -- "+str(instruction)+"\n")
        pc+=4
        
        #? syscalls 5 stages would need to be incorporated in pipelining 
        if instruction == "00000000000000000000000000001100": # syscalls
            clock-=1 
            v0 = register_file['$2']
            if v0 == 1:
                print(register_file['$4'])
            elif v0 == 4:
                start_address = register_file['$4']
                print(print_string(start_address))
                
            if v0 == 5:
                register_file['$2'] = int(input()) 
                

            if v0 == 8:
                address = register_file['$4']
                max_char = register_file['$5']
                string = input() 
                string = string + '\0'
                string_input(string, address)
            continue

        #instruction decode
        opcode,rs,rt,rd,shamt,funct,imm,address,rd1,rd2=instruction_decode(instruction)
        ALUcontrol=alucontrol(control_signals['ALUOp'],funct)
        if control_signals['RegDst']==0b0:
            rd=rt
        else:
            rd=rd
        clock+=1
        processor.append("ID  ")
        processor.append("  opcode:  "+hex(opcode))
        processor.append("  rs:  "+str(rs))
        processor.append("  rt:  "+str(rt))
        processor.append("  rd:  "+str(rd))
        processor.append("  shamt:  "+str(shamt))
        processor.append("  funct:  "+hex(funct))
        processor.append("  imm:  "+str(imm))
        processor.append("  address:  "+str(address))
        processor.append("  rd1:  "+str(rd1))
        processor.append("  rd2:  "+str(rd2)+"\n")
        
        # print(hex(pc-4),opcode,rs,rt,rd,shamt,funct,"**",imm,address,rd1,rd2)  
        
        #instruction execute
        ALUResult,zero=instr_execute(ALUcontrol,imm,rd1,rd2)
        clock+=1
        processor.append("EX ALU = "+str(ALUResult)+"  zero = "+str(zero)+"\n")
        #memory access
        if control_signals['Jump'] == 1:
            pc = address_after_jump(pc, address)
            processor.append("JUMPING TO "+hex(pc))
            # continue
        elif control_signals['Branch'] ==1 and zero:
            pc = pc + imm*4
            # continue
        writeData=rd2
        readData=memory(ALUResult,writeData)
        clock+=1
        processor.append("MEM readData = "+str(readData))
        processor.append("ADDRESS = "+str(ALUResult))
        if control_signals['MemWrite']!=0:
            processor.append("VALUE  "+str(data_mem[(ALUResult//4)*4])+"  ")
        else:
            processor.append("NOT WRITTEN IN MEMORY")
        #write back
        writeback(ALUResult,readData,rd)
        processor.append("  WB  ")
        processor.append("  rd = " + str(rd))
        processor.append("  ALUresult = " + str(ALUResult))
        processor.append("  readData = " + str(readData))
        processor.append("  value = " + str(register_file['$'+str(rd)]))
        processor.append("\n")
        clock+=1
        processor.append("________________________________________________________________________________________________________________"+str(clock)+"\n")
mips_processor()
# def cc(binary:str):
#     return hex(int(binary,2))
with open(processor_output, 'w') as f:
    for i in processor:
        print(i,file=f)
    f.close()
ff=open(memory11,'w')
for i in data_mem.keys():
    c=binary_to_string([data_mem[i][0:8],data_mem[i][8:16],data_mem[i][16:24],data_mem[i][24:32]])
    s=''
    for j in c:
        s+=j
        s+=' '
    print(hex(i),s,file=ff)

