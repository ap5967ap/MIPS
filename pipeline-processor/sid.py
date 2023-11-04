d={}
pc=0x400000
import threading
for i in range(15):
    d[pc]=i
    pc+=4

def if1(pc):
    print("IF",pc,d[pc])
    
def id(inst):
    print("ID",d[inst])
    
def ex(inst):
    print("EX",d[inst])
    
def mem(inst):
    print("MEM",d[inst])

def wb(inst):
    print("WB",d[inst])

pipeline = []


def processor():
    while pc <= d.keys():
        for i in range(5):
            