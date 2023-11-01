Rtype={# this is the funct for R type instructions ; opcode is 0
    0x20:"add",
    0x21:"addu",
    0x24:"and",    
    0x1A:"div",
    0x1B:"divu",
    0x08:"jr",
    0x10:"mfhi",
    0x12:"mflo",
    0x18:"mult",
    0x19:"multu",
    0x27:"nor",
    0x25:"or",
    0x26:"xor",
    0x2A:"slt",
    0x2B:"sltu",
    # 0x00:"sll",
    # 0x02:"srl",
    # 0x03:"sra",
    0x22:"sub",
    0x23:"subu",

}

# I type contains opcodes
Itype={
    0x04:"beq",
    0x05:"bne",
    0x23:"lw",
    0x21:"lh",
    0x20:"lb",
    0x28:"sb",
    0x2B:"sw",
    0x29:"sh",  
    0x09:"addiu",
    0x08:"addi",
    0x0C:"andi",
    0x0F:"lui",
    0x0D:"ori",
    0x0A:"slti",
    0x0B:"sltiu",
    0x0E:"xori"
}

# j type contains opcodes
Jtype = {
    0x02:"j",
    0x03:"jal"
}
