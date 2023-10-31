# # # Function to convert binary to ASCII value
# # def binary_to_string(bits):
# # 	return ''.join([chr(int(i, 2)) for i in bits])

# # # Driver Code

# # # This is the binary equivalent of string "GFG"
# # bin_values = ['01000111', '01000110', '01000111'] 

# # # calling the function
# # # and storing the result in variable 's'
# # s = binary_to_string(bin_values)

# # Printing the result
# print("The string created from the binary parts : ",s)
data_mem={}
dataMem='./data_binary.txt'
with open(dataMem, 'r') as f:
    address=0x10010000
    lines = f.readlines()
    lines = [line.strip() for line in lines]
    for line in lines:
        data_mem[(address)]=line
        address+=4

def print_string(start_address):
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


def string_input(string,address2):
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
        

string_input("hello",0x10010129)
print(print_string(0x10010129))
