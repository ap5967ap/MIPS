import sys
from opcodes import *
# from utils import *
binFile = sys.argv[1]
dataMem = sys.argv[2]
processor_output = sys.argv[3]
memory11 = sys.argv[4]
processor = []
instruct_memory = {}
data_mem = {}

with open(binFile, "r") as ff:
    lines = ff.readlines()
    lines = [line.strip() for line in lines]
    address = 0x400000
    for i in lines:
        instruct_memory[(address)] = i
        address += 4

with open(dataMem, "r") as fff:
    address = 0x10010000
    lines = fff.readlines()
    lines = [line.strip() for line in lines]
    for line in lines:
        data_mem[(address)] = line
        address += 4
q=open(processor_output,'w')

register_file = {
    "$0": 0,
    "$1": 0,
    "$2": 0,
    "$3": 0,
    "$4": 0,
    "$5": 0,
    "$6": 0,
    "$7": 0,
    "$8": 0,
    "$9": 0,
    "$10": 0,
    "$11": 0,
    "$12": 0,
    "$13": 0,
    "$14": 0,
    "$15": 0,
    "$16": 0,
    "$17": 0,
    "$18": 0,
    "$19": 0,
    "$20": 0,
    "$21": 0,
    "$22": 0,
    "$23": 0,
    "$24": 0,
    "$25": 0,
    "$26": 0,
    "$27": 0,
    "$28": 0,
    "$29": 0,
    "$30": 0,
    "$31": 0,
    "hi": 0,
    "lo": 0,
}



def sign_extend(imm, imm_len=32): # sign extending the immediate value
    if len(imm) == 32:
        return imm
    else:
        return imm[0] * (imm_len - len(imm)) + imm


def int_(binary_str):
    if binary_str[0] == "0":
        return int(binary_str, 2)
    elif binary_str[0] == "1":
        flipped_bits = "".join("1" if bit == "0" else "0" for bit in binary_str[1:])
        return -(int(flipped_bits, 2) + 1)


def bin_(num):
    if num >= 0:
        binary = bin(num)[2:]
        binary = binary.zfill(32)
    else:
        binary = bin(num & 0xFFFFFFFF)[2:]

    return binary


def binary_to_string(bits):  # convert binary to ascii value
    return "".join([chr(int(i, 2)) for i in bits])


def address_after_jump(imm):
    return int(imm) * 4
def instruction_fetch(pc):  # returns the instruction at the pc
    return instruct_memory[pc]

def control_path(opcode)->dict:#returns the control signals for the given opcode
    control_signals = {
    "RegDst": 0b0,  # if the destination register is rd or rt#TODO
    "Branch": 0b0,  # if we are making a branch instruction or not
    "MemRead": 0b00,  # if we are reading from mem or not
    "MemtoReg": 0b0,  # Destination from mem or ALU
    "ALUOp": 0b0000,
    "MemWrite": 0b00,  # if we are writing into mem or not
    "ALUSrc": 0b0,  # whether the second operand of the ALU is register or immediate
    "RegWrite": 0b0,  # if we are writing into register or not #TODO
    "Jump": 0b0,  # if the instruction uses jump or not
    }
    rtype = False
    itype = False
    jtype = False
    # converting to int from binary
    if opcode == 0:
        rtype = True
    elif opcode in Itype:
        itype = True
    elif opcode in Jtype:
        jtype = True

    if rtype:
        control_signals["RegDst"] = 0b1
        control_signals["Branch"] = 0b0
        control_signals["MemRead"] = 0b0
        control_signals["MemtoReg"] = 0b0
        control_signals[
            "ALUOp"
        ] = 0b0010  # ?changed ALUOp to 4 bits as we need to incorporate the I type instructions too
        control_signals["MemWrite"] = 0b0
        control_signals["ALUSrc"] = 0b0
        control_signals["RegWrite"] = 0b1
        control_signals["Jump"] = 0b0

    elif itype:
        if opcode in [0x04, 0x05]:  # beq or bne
            control_signals["RegDst"] = 0b0
            control_signals["Branch"] = 0b1
            control_signals["MemRead"] = 0b0
            control_signals["MemtoReg"] = 0b0
            control_signals["ALUOp"] = 0b0001
            if opcode == 0x05:  # bne
                control_signals["ALUOp"] = 0b1110
            control_signals["MemWrite"] = 0b0
            control_signals["ALUSrc"] = 0b0
            control_signals["RegWrite"] = 0b0
            control_signals["Jump"] = 0b0

        elif opcode in [0x20, 0x23, 0x21]:  # lb or lw
            control_signals["RegDst"] = 0b0
            control_signals["Branch"] = 0b0
            control_signals["MemRead"] = 0b11
            if opcode == 0x20:  # lb
                control_signals["MemRead"] = 0b01
            elif opcode == 0x21:  # lh
                control_signals["MemRead"] = 0b10
            control_signals["MemtoReg"] = 0b1
            control_signals["ALUOp"] = 0b0000
            control_signals["MemWrite"] = 0b0
            control_signals["ALUSrc"] = 0b1
            control_signals["RegWrite"] = 0b1
            control_signals["Jump"] = 0b0

        elif opcode in [0x28, 0x2B, 0x29]:  # sb or sw
            control_signals["RegDst"] = 0b0
            control_signals["Branch"] = 0b0
            control_signals["MemRead"] = 0b0
            control_signals["MemtoReg"] = 0b0
            control_signals["ALUOp"] = 0b0000
            control_signals["MemWrite"] = 0b11
            if opcode == 0x28:  # sb
                control_signals["MemWrite"] = 0b01
            elif opcode == 0x29:  # sh
                control_signals["MemWrite"] = 0b10
            control_signals["ALUSrc"] = 0b1
            control_signals["RegWrite"] = 0b0
            control_signals["Jump"] = 0b0

        else:
            control_signals["RegDst"] = 0b0
            control_signals["Branch"] = 0b0
            control_signals["MemRead"] = 0b0
            control_signals["MemtoReg"] = 0b0
            control_signals["MemWrite"] = 0b0
            control_signals["ALUSrc"] = 0b1
            control_signals["RegWrite"] = 0b1
            control_signals["Jump"] = 0b0
            itype_alu = {
                0x09: 0b0100,  # addiu
                0x08: 0b0100,  # addi
                0x0C: 0b0110,  # andi
                0x0F: 0b0111,  # lui
                0x0D: 0b1000,  # ori
                0x0A: 0b1001,  # slti
                0x0B: 0b1001,  # sltiu
                0x0E: 0b1011,  # xori
            }
            control_signals["ALUOp"] = itype_alu[opcode]

    elif jtype:
        control_signals["RegDst"] = 0b0
        control_signals["Branch"] = 0b0
        control_signals["MemRead"] = 0b0
        control_signals["MemtoReg"] = 0b0
        control_signals["ALUOp"] = 0b00
        control_signals["MemWrite"] = 0b0
        control_signals["ALUSrc"] = 0b0
        control_signals["RegWrite"] = 0b0
        control_signals["Jump"] = 0b1

    return control_signals

def instruction_decode(ifid):
    instruction=ifid[0]
    opcode = instruction[0:6]
    opcode = int(opcode, 2)
    rs = instruction[6:11]
    rs = int(rs, 2)
    rt = instruction[11:16]
    rt = int(rt, 2)
    rd = instruction[16:21]
    rd = int(rd, 2)
    shamt = instruction[21:26]
    shamt = int_(shamt)
    funct = instruction[26:32]
    funct = int(funct, 2)
    imm = instruction[16:32]
    imm = sign_extend(imm, 32)
    imm = int_(imm)
    address = instruction[6:32]
    address = int(address, 2)
    rd1 = register_file["$" + str(rs)]
    rd2 = register_file["$" + str(rt)]
    control_signals=control_path(opcode)
    alucontrol_singals=alucontrol(control_signals['ALUOp'],funct)
    return [control_signals,alucontrol_singals,0,[rs, rt, rd, imm, address, rd1, rd2]]

def alucontrol(AlUop, funct):
    if AlUop in [0b0100, 0b0000] or (funct in [0x20, 0x21] and AlUop == 2):
        return 0b0000  # ?add
    elif funct in [0x1B, 0x1A] and AlUop == 2:
        return 0b0001  # ?div
    elif (funct in [0x24] and AlUop == 2) or AlUop in [0b0110]:
        return 0b0010  # ?and
    elif funct == 0x10 and AlUop == 2:
        return 0b0011  # ?mfhi
    elif funct == 0x12 and AlUop == 2:
        return 0b0100  # ?mflo
    elif funct in [0x18, 0x19] and AlUop == 2:
        return 0b0101  # ?mult
    elif funct == 0x27 and AlUop == 2:
        return 0b0110  # ?nor
    elif (funct == 0x25 and AlUop == 2) or AlUop in [0b1000]:
        return 0b0111  # ?or
    elif (funct == 0x26 and AlUop == 2) or AlUop in [0b1011]:
        return 0b1000  # ?xor
    elif (funct in [0x2A, 0x2B] and AlUop == 2) or AlUop in [0b1001]:
        return 0b1001  # ?slt
    elif (funct in [0x22, 0x23] and AlUop == 2) or AlUop in [0b0001]:
        return 0b1010  # ?sub
    elif AlUop == 0b1110:
        return 0b1011  # ?bne
    elif AlUop in [0b0111]:
        return 0b1100  # ?lui

def ALU(control, op1, op2):  # [output,zero_flag] #control is ALUcontrol
    if control == 0b0000:
        return op1 + op2
    elif control == 0b0001:
        register_file["hi"] = op1 % op2
        register_file["lo"] = op1 // op2
        return 0
    elif control == 0b0010:
        return op1 & op2
    elif control == 0b0011:
        return register_file["hi"]
    elif control == 0b0100:
        return register_file["lo"]
    elif control == 0b0101:
        res = op1 * op2
        x = format(res, "064b")
        register_file["hi"] = int_(x[0:32])
        register_file["lo"] = int_(x[32:64])
        return 0
    elif control == 0b0110:
        return ~(op1 | op2)
    elif control == 0b0111:
        return op1 | op2
    elif control == 0b1000:
        return op1 ^ op2
    elif control == 0b1001:
        if op1 < op2:
            return 1
        else:
            return 0
    elif control == 0b1010:
        return ((op1 - op2)==0)
    elif control == 0b1011:
        return ((op1 - op2)!=0)
    elif control == 0b1100:
        return op2 << 16

def instruction_execute(idex): #?idex is pipeline register
    control_signals=idex[0] #?control_signals
    control=idex[1]  #?ALUcontrol
    if(control_signals['ALUSrc']==0b1):
        op2=idex[-1][3]
    else:
        op2=idex[-1][-1]
    ALUResult=ALU(control,idex[-1][-2],op2)
    rd=None
    if control_signals['RegDst']==0b1:
        rd=idex[-1][2]
    else:
        rd=idex[-1][1]
    return [ALUResult,rd,idex[-1][-1]]

def memory(exmem):
    control_signals=exmem[0]
    ALUResult=exmem[1]
    writeData=exmem[2]
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

def writeback(memwb):
    control_signals=memwb[0]
    ALUResult=memwb[1]
    ReadData=memwb[2]
    rd=memwb[3]
    Result = 0
    if control_signals["RegWrite"] == 0:
        return
    if control_signals["MemtoReg"] == 0:
        Result = ALUResult
    else:
        Result = ReadData
    if rd == 0:
        return
    register_file["$" + str(rd)] = Result
    return

class Pipe_instruction:
    def __init__(self) -> None:
        self.l=[instruction_fetch,
                instruction_decode,
                instruction_execute,
                memory,
                writeback]
        self.done=[False, False, False, False, False]
        self.instr=None
        self.i=0
        
    def run(self,pipeline_register=[0,0,0,0],pc=None):
        return_value=None
        if self.i==0:
            self.instr=self.l[self.i](pc)
            # return_value=self.instr
            return_value=[self.instr,pc]
        else:
            return_value=self.l[self.i](pipeline_register[self.i-1])
        self.done[self.i]=True
        self.i+=1
        return [return_value,self.i-1]
        
class Pipeline:
    pc=0x400000
    def __init__(self):
        self.pipeline=[]
        self.ifid=[0,0] #?pipelined registers
        self.idex=[0,0,0,0]
        self.exmem=[0,0,0,0,0]
        self.memwb=[0,0,0,0,0]
    
    def refresh(self):
        if self.pipeline and self.pipeline[-1].done[-1]:
            self.pipeline.pop()
    def append(self,inst:Pipe_instruction):
        self.refresh()
        if len(self.pipeline)<5:
            self.pipeline=[inst]+self.pipeline
            
    def flush_pipeline(self,imm):
        self.pipeline=self.pipeline[1:] #? flushing the pipeline
        Pipeline.pc=Pipeline.pc+imm*4
        
    def jump(self,address):
        self.pipeline=self.pipeline[1:] #? flushing the pipeline
        Pipeline.pc=address_after_jump(address)
    
    def forwarding_unit(self)->bool: #?returns true if forwarding is needed 
        #TODO(case of lw and sw)
            return_value=[0,0]
            if self.memwb[4] and self.idex[3][0]==self.memwb[4] and self.memwb[0]['MemRead']!=0: # rs == rt and memory read is there 
                return_value[0]=1
                print("*** 3333 ***",file=q)
            if self.memwb[4] and self.idex[3][1]==self.memwb[4] and self.memwb[0]['MemRead']!=0: # rt == rt and memory read is there
                return_value[1]=1
                print("*** 4444 ***",file=q)
            if self.memwb[3] and self.idex[3][0]==self.memwb[3]: # rs == rd
                return_value[0]=1
                print("*** 5555 ***",file=q)
            if self.memwb[3] and self.idex[3][1]==self.memwb[3]: # rs == rd 
                return_value[1]=1
                print("*** 6666 ***",file=q)
            if self.exmem[3] and self.exmem[3] == self.idex[3][0]: # rd == rs
                return_value[0]=2
                print("*** 1111 ***",file=q)
            if self.exmem[3] and self.exmem[3] == self.idex[3][1]: # rd == rt
                return_value[1]=2
                print("*** 2222 ***",file=q)
                
            return return_value
        
    def isStall(self)->bool: # checks if stalling is required or not
        try:
            if self.exmem and self.exmem[0]['MemRead']!=0 and (self.idex[3][0]==self.exmem[4] or self.idex[3][1]==self.exmem[4]):
                return True
            return False
        except:
            return False
    def run(self):
        while Pipeline.pc<max(instruct_memory.keys()) or self.pipeline:
            self.refresh()
            stall=False
            flush_pipeline=False 
            jump=False  
            for i in self.pipeline[::-1]:
                if self.isStall():
                    stall=True
                    self.exmem=[0,0,0,0]
                    break
                return_value,x=i.run(pc=Pipeline.pc,pipeline_register=[self.ifid,self.idex,self.exmem,self.memwb])
                if x==0:
                    print("IF",file=q)
                    self.ifid[0]=return_value
                    self.ifid[1]=Pipeline.pc
                    print('pc:',Pipeline.pc,file=q)
                    print('instruction:',return_value,file=q)
                    print(file=q)
                    continue
                elif x==1: #*[control_signals,alucontrol_singals,take_branch,[rs, rt, rd, imm, address, rd1, rd2]]
                    self.idex[0]=return_value[0] #?control_signals
                    self.idex[1]=return_value[1] #?alucontrol_singals
                    self.idex[2]=return_value[2] #?take_branch
                    self.idex[3]=return_value[3] #?[rs, rt, rd, imm, address, rd1, rd2]
                    
                    if return_value[0]['Jump']==0b1:
                        jump=True
                    else:
                        jump=False
                    print("ID",file=q)                    
                    print('control_signals:',return_value[0],file=q)
                    print('alucontrol_singals:',return_value[1],file=q)
                    print('take_branch:',return_value[2],file=q)
                    print('rs, rt, rd, imm, address, rd1, rd2:',return_value[3],file=q)
                    print(file=q)
                elif x==2: #*[ALUResult,rd,rd2]
                    self.exmem[0]=self.idex[0]   #?control_signals
                    self.exmem[1]=return_value[0]#?ALUResult
                    self.exmem[2]=return_value[2]#?WriteData
                    self.exmem[3]=return_value[1]#?rd
                    self.exmem[4]=self.idex[3][1]#?rt
                    if self.exmem[0]['Branch']==0b1 and return_value[0]==1:
                        flush_pipeline=True
                    print("EX",file=q)
                    print('control_signals:',self.idex[0],file=q)
                    print('ALUResult:',return_value[0],file=q)
                    print('WriteData:',return_value[2],file=q)
                    print('rd:',return_value[1],file=q)
                    print('rt:',self.idex[3][1],file=q)
                    print(file=q)
                    continue
                elif x==3: #*[control_signals,ALUResult,ReadData,rd]
                    self.memwb[0]=self.exmem[0] #?control_signals
                    self.memwb[1]=self.exmem[1] #?ALUResult
                    self.memwb[2]=return_value  #?MemResult
                    self.memwb[3]=self.exmem[3] #?rd
                    self.memwb[4]=self.exmem[4] #?rt
                    print("MEM",file=q)
                    print('control_signals:',self.exmem[0],file=q)
                    print('ALUResult:',self.exmem[1],file=q)
                    print('ReadData:',return_value,file=q)
                    print('rd:',self.exmem[3],file=q)
                    print('rt:',self.exmem[4],file=q)
                    print(file=q)
                    continue    
                elif x==4:
                    continue    
                sel0,sel1=self.forwarding_unit()
                if sel0==1:
                    self.idex[3][5]=self.memwb[2] if self.memwb[0]['MemtoReg'] else self.memwb[1] #?forwarding from memwb register to idex register
                    print('FORWARDING1rd1',file=q)
                elif sel0==2:
                    self.idex[3][5]=self.exmem[1]
                    print('FORWARDING2rd1',file=q)
                if sel1==1:
                    self.idex[3][6]=self.memwb[2] if self.memwb[0]['MemtoReg'] else self.memwb[1]
                    print('FORWARDING1rd2',file=q)
                elif sel1==2:
                    self.idex[3][6]=self.exmem[1]
                    print('FORWARDING2rd2',file=q)
                
            if stall:
                continue
            if Pipeline.pc<=max(instruct_memory.keys()):
                instr=Pipe_instruction()    
                self.append(instr)
                return_value,x=self.pipeline[0].run(pc=Pipeline.pc)
                if x==0:
                    self.ifid[0]=return_value[0]
                    self.ifid[1]=Pipeline.pc
                    print("IF",file=q)
                    print('pc:',hex(Pipeline.pc),file=q)
                    print('instruction:',return_value,file=q)
                Pipeline.pc+=4
            if flush_pipeline:
                print("flushing pipeline",file=q)
                self.flush_pipeline(self.idex[3][3])
            if jump:
                self.jump(self.idex[3][4])
                print("jumping to:",hex(self.idex[3][4]),file=q)
            print('IFID:',self.ifid,file=q)
            print('IDEX:',self.idex,file=q)
            print('EXMEM:',self.exmem,file=q)
            print('MEMWB:',self.memwb,file=q)
            print(register_file,file=q)
            print('_________________________',file=q)
            
            
a=Pipeline()
a.run()