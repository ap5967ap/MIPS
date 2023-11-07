import sys
from opcodes import *
binFile = sys.argv[1]
dataMem = sys.argv[2]
processor_output = sys.argv[3]
memory11 = sys.argv[4]
processor = []
instruct_memory = {}
data_mem = {}
ffd=open(memory11,'w')

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
    """
    Decodes the instruction fetched in the previous stage and extracts the opcode, rs, rt, rd, shamt, funct, imm, address, rd1, rd2, control signals and ALU control signals.

    Args:
    ifid: A list containing the instruction fetched in the previous stage.

    Returns:
    A list containing the control signals, ALU control signals, 0, and a list of rs, rt, rd, imm, address, rd1, rd2.
    """
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
    """
    Determines the ALU control signal based on the given ALU operation and function code.

    Args:
    - AlUop (int): 4-bit ALU operation code.
    - funct (int): 6-bit function code.

    Returns:
    - int: 4-bit ALU control signal.
    """
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
    elif AlUop in [0b0001]:
        return 0b1010  # ?sub
    elif AlUop == 0b1110:
        return 0b1011  # ?bne
    elif AlUop in [0b0111]:
        return 0b1100  # ?lui
    elif (funct in [0x22, 0x23] and AlUop == 2):
        return 0b1111

def ALU(control, op1, op2):
    """
    Performs arithmetic and logical operations based on the control signal and the operands.

    Args:
    control (int): 4-bit control signal that determines the operation to be performed.
    op1 (int): First operand.
    op2 (int): Second operand.

    Returns:
    int: Result of the operation.
    """
    if control == 0b0000:#?add
        return op1 + op2
    elif control == 0b0001:#?div
        register_file["hi"] = op1 % op2
        register_file["lo"] = op1 // op2
        return 0
    elif control == 0b0010:#?and
        return op1 & op2
    elif control == 0b0011:#?mfhi
        return register_file["hi"]
    elif control == 0b0100:#?mflo
        return register_file["lo"]
    elif control == 0b0101:#?mult
        res = op1 * op2
        x = format(res, "064b")
        register_file["hi"] = int_(x[0:32])
        register_file["lo"] = int_(x[32:64])
        return 0
    elif control == 0b0110:#?nor
        return ~(op1 | op2)
    elif control == 0b0111:#?or
        return op1 | op2
    elif control == 0b1000:#?xor
        return op1 ^ op2
    elif control == 0b1001:#?slt
        if op1 < op2:
            return 1
        else:
            return 0
    elif control == 0b1111:#?sub
        return op1 - op2
    elif control == 0b1010:#?beq
        return ((op1 - op2)==0)
    elif control == 0b1011:#?bne
        return ((op1 - op2)!=0)
    elif control == 0b1100:#?lui
        return op2 << 16

def instruction_execute(idex):
    """
    Executes the instruction in the ID/EX pipeline register.

    Args:
    idex (list): The ID/EX pipeline register containing the control signals, control, and operands.

    Returns:
    list: A list containing the ALU result, destination register, and immediate value.
    """
    control_signals=idex[0]
    control=idex[1]

    if(control_signals['ALUSrc']==0b1):
        op2=idex[-1][3]
    else:
        op2=idex[-1][-1]
    print(control_signals['ALUSrc'],idex[-1][-2],op2,file=q)
    ALUResult=ALU(control,idex[-1][-2],op2)
    rd=None
    if control_signals['RegDst']==0b1:
        rd=idex[-1][2]
    else:
        rd=idex[-1][1]
    return [ALUResult,rd,idex[-1][-1]]

def memory(exmem):
    """
    This function performs memory operations based on the control signals and ALU result.
    It reads data from data memory if MemRead is set, and writes data to data memory if MemWrite is set.
    It raises an exception if the fetch address is not aligned on the correct boundary.
    Args:
    - exmem: A list containing control signals, ALU result and write data.
    Returns:
    - 0 if no memory operation is performed.
    - Data read from data memory if MemRead is set.
    """
    control_signals=exmem[0]
    ALUResult=exmem[1]
    writeData=exmem[2]
    if not(control_signals) or control_signals['MemRead']==0b00 and control_signals['MemWrite']==0b00:
        return 0
    start=(ALUResult//4)*4
    try:
        _=data_mem[start]
    except KeyError:
        data_mem[start]="0"*32
    if control_signals['MemRead']==0b01:
        start=(ALUResult//4)*4
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
        start=(ALUResult//4)*4
        offset=ALUResult%4
        if offset==1 or offset==3:
            raise Exception("fetch address not aligned on halfword boundary")
        elif offset ==0:
            return int_(sign_extend(data_mem[start][16:32],32))
        elif offset ==2:
            return int_(sign_extend(data_mem[start][0:16],32))
    elif control_signals['MemRead']==0b11:
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
    """
    Writes the result of the executed instruction back to the register file.

    Args:
    - memwb: A list containing the control signals, ALU result, read data, and destination register.

    Returns:
    - None
    """
    control_signals=memwb[0]
    ALUResult=memwb[1]
    ReadData=memwb[2]
    rd=memwb[3]
    Result = 0
    if not(control_signals) or control_signals["RegWrite"] == 0:
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
    """
    A class representing a pipeline instruction.

    Attributes:
    - l: a list of functions representing the pipeline stages
    - done: a list of booleans representing whether each stage is done
    - instr: the current instruction being processed
    - i: the current stage index

    Methods:
    - run(pipeline_register, pc): runs the pipeline instruction and returns the result
    """
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
        """
        Runs the pipeline instruction and returns the result.

        Args:
        - pipeline_register: a list representing the pipeline register
        - pc: the program counter

        Returns:
        A list containing the result and the current stage index
        """
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
    '''This class implements the pipeline interface for MIPS Pipeline Processor.'''
    pc=0x400000
    def __init__(self): #?initializing the pipeline
        self.pipeline=[]
        self.ifid=[0,0] #?pipelined registers
        self.idex=[0,0,0,0]
        self.exmem=[0,0,0,0,0]
        self.memwb=[0,0,0,0,0]
    
    def refresh(self): #?removing the instructions after writeback phase from the pipeline
        if self.pipeline and self.pipeline[-1].done[-1]:
            self.pipeline.pop()
    def append(self,inst:Pipe_instruction): #?adding the instruction to the pipeline
        self.refresh()
        if len(self.pipeline)<5:
            self.pipeline=[inst]+self.pipeline
            
    def flush_pipeline(self,old_pc,imm): #?flushing the pipeline in case of branch
        self.pipeline=self.pipeline[2:] #?removing the "NOT REQUIRED" instructions from the pipeline
        Pipeline.pc=old_pc+imm*4+4 #?updating the pc
        print("flushing pipeline, PC set to ",hex(Pipeline.pc),file=q)
        
    def jump(self,address):#?jumping to the given address
        self.pipeline=self.pipeline[1:] #? flushing the pipeline
        Pipeline.pc=address_after_jump(address)
        print("jumping to:",hex(Pipeline.pc),file=q)
        
    
    def sw(self)->bool: #?dependencies in case of sw
        return self.exmem[0] and self.exmem[0]['MemWrite']!=0 and self.memwb[3]==self.exmem[4]
    def forwarding_unit(self)->bool: #?returns select lines if forwarding is needed 
            return_value=[0,0]
            if self.memwb[4] and (self.memwb[0]['RegWrite'] or self.memwb[0]['MemWrite']) and self.idex[3][0]==self.memwb[4] and self.memwb[0]['MemRead']!=0: # rs == rt and memory read is there 
                return_value[0]=1
                print("*** Forwarding, MEM->EX(rs) ***",file=q)
            if self.memwb[4] and (self.memwb[0]['RegWrite'] or self.memwb[0]['MemWrite']) and self.idex[3][1]==self.memwb[4] and self.memwb[0]['MemRead']!=0: # rt == rt and memory read is there
                return_value[1]=1
                print("*** Forwarding, MEM->EX(rt) ***",file=q)
            if self.memwb[3] and (self.memwb[0]['RegWrite'] or self.memwb[0]['MemWrite']) and self.idex[3][0]==self.memwb[3]: # rs == rd
                return_value[0]=1
                print("*** Previous 2nd EX - forwarding, MEM->EX(rs) ***",file=q)
            if self.memwb[3] and (self.memwb[0]['RegWrite'] or self.memwb[0]['MemWrite']) and self.idex[3][1]==self.memwb[3]: # rt == rd 
                return_value[1]=1
                print("*** Previous 2nd EX - forwarding, MEM->EX(rt) ***",file=q)
            if self.exmem[3] and (self.exmem[0]['RegWrite'] or self.exmem[0]['MemWrite']) and self.exmem[3] and self.exmem[3] == self.idex[3][0]: # rd == rs
                return_value[0]=2
                print("*** Forwarding EX->EX(rs) ***",file=q)
            if self.exmem[3] and (self.exmem[0]['RegWrite'] or self.exmem[0]['MemWrite']) and self.exmem[3] and self.exmem[3] == self.idex[3][1]: # rd == rt
                return_value[1]=2
                print("*** Forwarding EX->EX(rt) ***",file=q)
            return return_value
        
    def isStall(self)->bool: #? checks if stalling is required or not
        try:
            if self.exmem and self.exmem[0]['MemRead']!=0 and (self.idex[3][0]==self.exmem[4] or self.idex[3][1]==self.exmem[4]):
                return True
            return False
        except:
            return False
    def run(self):
        clock=0
        while Pipeline.pc<max(instruct_memory.keys()) or self.pipeline:
            self.refresh()
            stall=False
            flush_pipeline=False 
            jump=False  
            clock += 1
            for i in self.pipeline[::-1]:#?Executing in parallel
                return_value,x=i.run(pc=Pipeline.pc,pipeline_register=[self.ifid,self.idex,self.exmem,self.memwb])
                if x==0:#?Executing IF stage
                    print("IF",file=q)
                    self.ifid[0]=return_value
                    self.ifid[1]=Pipeline.pc
                    print('pc:',Pipeline.pc,file=q)
                    print('instruction:',return_value,file=q)
                    print(file=q)
                    continue
                    
                elif x==1: #*[control_signals,alucontrol_singals,take_branch,[rs, rt, rd, imm, address, rd1, rd2]]#?ID
                    self.idex[0]=return_value[0] #?control_signals
                    self.idex[1]=return_value[1] #?alucontrol_singals
                    self.idex[2]=self.ifid[1]   #? storing pc for beq
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
                    
                elif x==2: #*[ALUResult,rd,rd2]#?EX
                    self.exmem[0]=self.idex[0]   #?control_signals
                    self.exmem[1]=return_value[0]#?ALUResult
                    self.exmem[2]=return_value[2]#?WriteData
                    self.exmem[3]=return_value[1]#?rd
                    self.exmem[4]=self.idex[3][1]#?rt
                    self.exmem.append([self.idex[3][3],self.idex[2]])
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
                    
                elif x==3: #*[control_signals,ALUResult,ReadData,rd]#?MEM
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
                    
                elif x==4:#?WB
                    ...
                if self.sw():#?sw dependency
                        self.exmem[2]=self.memwb[1]
                if self.isStall():#?lw/sw hazards dependency
                    print("stalling",file=q)
                    stall=True
                    self.exmem=[0,0,0,0,0]
                    break   
                
                sel0,sel1=self.forwarding_unit()
                if sel0==1: #?FORWARDING unit
                    self.idex[3][5]=self.memwb[2] if self.memwb[0]['MemtoReg'] else self.memwb[1] #?forwarding from memwb register to idex register
                elif sel0==2:
                    self.idex[3][5]=self.exmem[1]
                if sel1==1:
                    self.idex[3][6]=self.memwb[2] if self.memwb[0]['MemtoReg'] else self.memwb[1]
                elif sel1==2:
                    self.idex[3][6]=self.exmem[1]
            if stall:
                print('_________________________',file=q)
                continue
            if Pipeline.pc<=max(instruct_memory.keys()) and jump==False:
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
                self.flush_pipeline(self.exmem[-1][-1],self.exmem[-1][0])
            if jump:
                self.jump(self.idex[3][4])
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
            print('IFID:',self.ifid,file=q)
            print('IDEX:',self.idex,file=q)
            print('EXMEM:',self.exmem,file=q)
            print('MEMWB:',self.memwb,file=q)
            print(register_file,file=q)
            print("CLOCK:",clock,file=q)
            print('_________________________',file=q)
        print("TOTAL CLOCK CYCLES:",clock)
            
a=Pipeline()
a.run()
ffd=open(memory11,'w')
for i in data_mem.keys():
    print(hex(i),int(data_mem[i],2),file=ffd)   
