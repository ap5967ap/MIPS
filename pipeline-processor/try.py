d={}
pc=0x400000
import random
import threading
for i in range(15):
    d[pc]=i
    pc+=4

def if1(pc):
    print("IF",pc,d[pc])
    return d[pc]
    
def id(inst1):
    print("ID",inst1)
    
def ex(inst):
    print("EX",inst)
    
def mem(inst):
    print("MEM",inst)

def wb(inst):
    print("WB",inst)

class Pipe_instruction:
    def __init__(self) -> None:
        self.l=[if1,id,ex,mem,wb]
        self.done=[False, False, False, False, False]
        self.instr=None
        self.i=0
    def run(self,pc=None):
        if self.i==0:
            self.instr=self.l[self.i](pc)
        else:
            self.l[self.i](self.instr)
        self.done[self.i]=True
        self.i+=1

xx=0.95
        
class Pipeline:
    pc=0x400000
    def __init__(self):
        self.pipeline=[]
    
    def refresh(self):
        if self.pipeline and self.pipeline[-1].done[-1]:
            self.pipeline.pop()
    def append(self,inst:Pipe_instruction):
        self.refresh()
        if len(self.pipeline)<5:
            self.pipeline=[inst]+self.pipeline
            

    def run(self):
        while Pipeline.pc<max(d.keys()) or self.pipeline:
            self.refresh()
            instr=Pipe_instruction()    
            flag=0        
            c=5
            for i in self.pipeline[::-1]:
                x=random.random()
                if x>=xx:
                    flag=1
                    print("STALL\n"*c)
                    print('_________________________')
                    break
                i.run(Pipeline.pc)
                c-=1
            if flag:
                continue
            if Pipeline.pc<=max(d.keys()):
                self.append(instr)
                self.pipeline[0].run(Pipeline.pc)
            Pipeline.pc+=4
            print('_________________________')
p=Pipeline()
p.run()